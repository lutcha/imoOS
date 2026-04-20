from django.db import connection
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Building, Floor, ProjectDocument
from .serializers import ProjectSerializer, BuildingSerializer, FloorSerializer, ProjectDocumentSerializer
from apps.users.permissions import IsTenantMember
from rest_framework.permissions import IsAuthenticated


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related('buildings')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'city']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['created_at', 'name', 'expected_delivery_date']

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            from apps.memberships.models import TenantMembership
            # Check if user is solely an investor
            # Actually, standard behavior: restrict if role is INVESTIDOR 
            is_investor = TenantMembership.objects.filter(
                user=request.user,
                role=TenantMembership.ROLE_INVESTIDOR,
                is_active=True
            ).exists()
            is_manager = TenantMembership.objects.filter(
                user=request.user,
                role__in=[TenantMembership.ROLE_ADMIN, TenantMembership.ROLE_GESTOR, TenantMembership.ROLE_ENGENHEIRO],
                is_active=True
            ).exists()
            
            if is_investor and not is_manager:
                self.permission_denied(
                    request,
                    message="Investidores da Diáspora apenas têm permissão de leitura.",
                    code="read_only_for_investor"
                )

    def perform_create(self, serializer):
        from apps.tenants.models import TenantSettings
        from apps.tenants.limits import check_project_limit
        tenant_settings, _ = TenantSettings.objects.get_or_create(
            tenant__schema_name=connection.schema_name,
            defaults={'tenant': self.request.tenant},
        )
        check = check_project_limit(tenant_settings)
        if not check.allowed:
            raise ValidationError({'non_field_errors': [check.message]})
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'], parser_classes=[MultiPartParser, FormParser])
    def documents(self, request, pk=None):
        project = self.get_object()
        
        if request.method == 'GET':
            docs = ProjectDocument.objects.filter(project=project)
            serializer = ProjectDocumentSerializer(docs, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            # Create a new document
            serializer = ProjectDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(project=project, uploaded_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def update_progress_photo(self, request, pk=None):
        """
        Skill: update_progress_photo
        Accepts phase_id, progress_percent, notes, image
        """
        project = self.get_object()
        phase_id = request.data.get('phase_id')
        new_progress = request.data.get('progress_percent')
        image = request.data.get('image')
        notes = request.data.get('notes', '')

        if not phase_id or not new_progress:
            return Response({"error": "phase_id and progress_percent are required."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.construction.models.phase import ConstructionPhase
        from apps.construction.models.progress import TaskProgressLog, TaskPhoto
        from apps.construction.models.task import ConstructionTask
        from django.utils import timezone
        
        try:
            phase = ConstructionPhase.objects.get(id=phase_id, project=project)
        except ConstructionPhase.DoesNotExist:
            return Response({"error": "Phase not found."}, status=status.HTTP_404_NOT_FOUND)

        # Atualizar percentagem da Fase
        old_progress = phase.progress_percent
        phase.progress_percent = new_progress
        if float(new_progress) >= 100:
            phase.status = ConstructionPhase.STATUS_COMPLETED
            if not phase.end_actual:
                phase.end_actual = timezone.now().date()
        elif float(new_progress) > 0:
            phase.status = ConstructionPhase.STATUS_IN_PROGRESS
            if not phase.start_actual:
                phase.start_actual = timezone.now().date()
        phase.save(update_fields=['progress_percent', 'status', 'start_actual', 'end_actual'])

        # Create a dummy task to hold the photo directly at phase level if needed, or link to Phase directly...
        # Wait, TaskPhoto requires a ConstructionTask. If the user uploads a general progress photo, 
        # we might need to create an "Update Geral" task or we can adapt TaskPhoto. 
        # Let's create a generic task if none exists.
        task, _ = ConstructionTask.objects.get_or_create(
            phase=phase,
            name="Atualização Geral de Progresso",
            defaults={'project': project, 'start_planned': timezone.now().date(), 'end_planned': timezone.now().date(), 'created_by': request.user}
        )
        task.progress_percent = new_progress
        task.save(update_fields=['progress_percent'])

        # Registrar log
        TaskProgressLog.objects.create(
            task=task,
            updated_by=request.user,
            old_percent=old_progress,
            new_percent=new_progress,
            notes=notes
        )

        # Upload de Foto se existir
        if image:
            photo = TaskPhoto.objects.create(
                task=task,
                uploaded_by=request.user,
                image=image,
                caption=notes,
                progress_at_upload=new_progress
            )

        return Response({"status": "Progress updated", "phase": phase.id, "progress_percent": phase.progress_percent})

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all().prefetch_related('floors')
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project']
    search_fields = ['name']

class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all().prefetch_related('units')
    serializer_class = FloorSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['building']
