from rest_framework import serializers

from .models import ConstructionPhoto, ConstructionProgress, DailyReport


class ConstructionPhotoSerializer(serializers.ModelSerializer):
    has_geotag = serializers.ReadOnlyField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ConstructionPhoto
        fields = [
            'id',
            'report',
            's3_key',
            'thumbnail_s3_key',
            'caption',
            'latitude',
            'longitude',
            'has_geotag',
            'created_by',
            'created_at',
        ]
        read_only_fields = ['id', 'has_geotag', 'created_by', 'created_at']


class DailyReportSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    photos = ConstructionPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = DailyReport
        fields = [
            'id',
            'project',
            'building',
            'date',
            'author',
            'summary',
            'progress_pct',
            'status',
            'status_display',
            'weather',
            'workers_count',
            'photos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'status', 'created_at', 'updated_at']


class ConstructionProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionProgress
        fields = [
            'id',
            'building',
            'progress_pct',
            'last_updated',
            'last_report',
        ]
        read_only_fields = ['id', 'last_updated']
