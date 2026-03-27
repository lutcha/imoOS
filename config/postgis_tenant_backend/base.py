"""
Tenant-aware PostGIS backend for ImoOS.

Combines:
  - django_tenants.postgresql_backend  (schema-per-tenant switching)
  - django.contrib.gis.db.backends.postgis (geo_db_type, GIS operations)

Django loads database backends by importing <ENGINE>.base.DatabaseWrapper.
We resolve the MRO conflict by putting the GIS backend first (so its
`ops` class is used) and the tenant backend second (so schema-switching
__init__ / _cursor methods win via super()).
"""
from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISDatabaseWrapper,
)
from django_tenants.postgresql_backend.base import (
    DatabaseWrapper as TenantDatabaseWrapper,
)


class DatabaseWrapper(PostGISDatabaseWrapper, TenantDatabaseWrapper):
    """
    MRO: PostGISDatabaseWrapper → TenantDatabaseWrapper → psycopg2 wrapper.

    PostGIS is first so `ops` is a PostGISOperations instance (provides
    geo_db_type and all spatial query compilation).
    TenantDatabaseWrapper is second so its __init__ / set_tenant / _cursor
    overrides still run via the MRO chain through super() calls.
    """
