"""
Custom database backend: django-tenants + PostGIS.

django_tenants.postgresql_backend wraps django.db.backends.postgresql.
For projects that use PostGIS (django.contrib.gis), we need the wrapper to
target django.contrib.gis.db.backends.postgis instead.
"""
from django_tenants.postgresql_backend.base import DatabaseWrapper as TenantDatabaseWrapper
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as PostGISDatabaseWrapper


class DatabaseWrapper(TenantDatabaseWrapper):
    """
    Tenant-aware PostGIS database wrapper.

    Inherits schema-switching logic from django-tenants and GIS operation
    support (geo_db_type, etc.) from the PostGIS backend.
    """

    # Pull GIS-specific operations from the PostGIS backend
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Overlay PostGIS operations onto this connection
        from django.contrib.gis.db.backends.postgis.operations import PostGISOperations
        self.ops.__class__ = type(
            'TenantPostGISOperations',
            (PostGISOperations, self.ops.__class__),
            {},
        )
