"""
grant_schema_create — Tenta conceder privilégio CREATE SCHEMA ao utilizador da app.

Em DO App Platform dev databases, o utilizador da app não tem CREATE on database.
Este comando conecta via DATABASE_URL (potencialmente com mais privilégios) e
tenta fazer GRANT CREATE ON DATABASE ao DB_USER.

Corre com || true no migrate job — falha silenciosa é aceitável.
"""
import os

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Concede CREATE privilege ao DB user via DATABASE_URL (doadmin)'

    def handle(self, *args, **options):
        db_user = os.environ.get('DB_USER', '')
        database_url = os.environ.get('DATABASE_URL', '')

        # Diagnóstico: user e privilégios actuais
        with connection.cursor() as cur:
            cur.execute("SELECT current_user, current_database();")
            current_user, current_db = cur.fetchone()
            cur.execute(
                "SELECT has_database_privilege(%s, %s, 'CREATE');",
                [current_user, current_db],
            )
            has_create = cur.fetchone()[0]

        self.stdout.write(
            f'DB info: user={current_user}, db={current_db}, '
            f'has_CREATE={has_create}, db_user_env={db_user!r}'
        )

        if has_create:
            self.stdout.write(self.style.SUCCESS(
                '✅ User already has CREATE privilege — schema creation will work.'
            ))
            return

        # Se DATABASE_URL existe e é diferente do user actual, tenta GRANT via psycopg2 directo
        if database_url and db_user:
            try:
                import psycopg2
                self.stdout.write(
                    f'Trying GRANT via DATABASE_URL connection → {db_user}...'
                )
                conn = psycopg2.connect(database_url, sslmode='require')
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SELECT current_user, current_database();")
                    admin_user, admin_db = cur.fetchone()
                    self.stdout.write(f'  DATABASE_URL user: {admin_user}')

                    cur.execute(
                        "SELECT has_database_privilege(%s, %s, 'CREATE');",
                        [admin_user, admin_db],
                    )
                    admin_has_create = cur.fetchone()[0]
                    self.stdout.write(f'  DATABASE_URL has_CREATE: {admin_has_create}')

                    if admin_has_create and admin_user != db_user:
                        cur.execute(
                            f'GRANT CREATE ON DATABASE "{admin_db}" TO "{db_user}";'
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'✅ GRANT CREATE ON DATABASE {admin_db} TO {db_user} — OK'
                        ))
                    elif admin_user == db_user:
                        self.stdout.write(
                            'DATABASE_URL is same user — cannot self-grant. '
                            'Manual GRANT needed as superuser.'
                        )
                    else:
                        self.stdout.write(
                            'DATABASE_URL user also lacks CREATE — '
                            'cannot grant. Manual intervention required.'
                        )
                conn.close()
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(f'GRANT via DATABASE_URL failed: {exc}')
                )
        else:
            self.stdout.write(
                'DATABASE_URL or DB_USER not set — skipping GRANT attempt.'
            )
