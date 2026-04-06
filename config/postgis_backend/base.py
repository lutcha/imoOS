"""
Custom PostgreSQL backend that combines:
- django.contrib.gis.db.backends.postgis  (geo_db_type, PostGIS support)
- django_tenants.postgresql_backend        (schema-per-tenant switching)

MRO: PostGISDatabaseWrapper first so geo methods take precedence,
     then TenantsDatabaseWrapper for schema switching.
"""
from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISDatabaseWrapper,
)
from django_tenants.postgresql_backend.base import (
    DatabaseWrapper as TenantsDatabaseWrapper,
)


class DatabaseWrapper(PostGISDatabaseWrapper, TenantsDatabaseWrapper):
    """
    Unified wrapper: full PostGIS spatial support + django-tenants
    schema isolation.  Python MRO resolves conflicts in favour of
    PostGIS (left-most parent), while TenantsDatabaseWrapper's
    set_schema / get_schema methods are also inherited.
    """
    pass
