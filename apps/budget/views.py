"""
Budget Views — API Views para o app budget.
"""
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.utils import timezone

from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem,
    CrowdsourcedPrice, UserPriceScore,
    ConstructionExpense, ConstructionAdvance
)
from apps.budget.serializers import (
    LocalPriceItemSerializer, LocalPriceItemListSerializer,
    SimpleBudgetSerializer, SimpleBudgetDetailSerializer,
    BudgetItemSerializer, CrowdsourcedPriceSerializer,
    CrowdsourcedPriceVerifySerializer, UserPriceScoreSerializer,
    PriceSuggestionRequestSerializer, PriceAnomalyCheckSerializer,
    BudgetCreateFromTemplateSerializer, BudgetCompareSerializer,
    ExcelImportSerializer, ConstructionExpenseSerializer,
    ConstructionAdvanceSerializer
)
from apps.budget.services import PriceEngine, BudgetCalculator, ExcelImporter, ExcelExporter
from apps.budget.services.financial_service import FinancialConsolidationService
from apps.budget.services.report_service import ConstructionReportService
from apps.projects.models import Project


class LocalPriceItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir a base de preços local.
    
    list: Listar items de preço (com filtros e search)
    retrieve: Ver detalhes de um item
    create: Criar novo item (admin only)
    update: Actualizar item (admin only)
    """
    queryset = LocalPriceItem.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_verified', 'unit']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'last_updated', 'price_santiago']
    ordering = ['category', 'code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LocalPriceItemListSerializer
        return LocalPriceItemSerializer
    
    def get_queryset(self):
        """Filtrar por ilha se especificado."""
        queryset = super().get_queryset()
        
        # Filtro de ilha para preço específico
        island = self.request.query_params.get('island')
        if island:
            # Anotação do preço para a ilha solicitada
            price_field = f'price_{island.lower()}'
            if hasattr(LocalPriceItem, price_field):
                queryset = queryset.filter(**{f'{price_field}__isnull': False})
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def suggest(self, request):
        """
        Sugerir preço baseado em histórico e similares.
        
        POST /api/v1/budget/price-items/suggest/
        {
            "item_name": "Cimento CP350 50kg",
            "island": "SANTIAGO",
            "category": "MATERIALS",
            "unit": "SACO"
        }
        """
        serializer = PriceSuggestionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        engine = PriceEngine()
        suggestion = engine.suggest_price(
            item_name=serializer.validated_data['item_name'],
            island=serializer.validated_data['island'],
            category=serializer.validated_data['category'],
            unit=serializer.validated_data.get('unit')
        )
        
        return Response(suggestion)
    
    @action(detail=False, methods=['post'])
    def check_anomaly(self, request):
        """
        Verificar se um preço é anômalo.
        
        POST /api/v1/budget/price-items/check_anomaly/
        {
            "price": "950.00",
            "item_name": "Cimento CP350 50kg",
            "island": "SANTIAGO",
            "category": "MATERIALS"
        }
        """
        serializer = PriceAnomalyCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        engine = PriceEngine()
        result = engine.detect_price_anomaly(
            price=serializer.validated_data['price'],
            item_name=serializer.validated_data['item_name'],
            island=serializer.validated_data['island'],
            category=serializer.validated_data['category']
        )
        
        return Response(result)


class SimpleBudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir orçamentos.
    
    list: Listar orçamentos
    retrieve: Ver detalhes de um orçamento
    create: Criar novo orçamento
    update: Actualizar orçamento
    """
    queryset = SimpleBudget.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'island']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'grand_total', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SimpleBudgetDetailSerializer
        return SimpleBudgetSerializer
    
    def get_queryset(self):
        """Filtrar por projecto se especificado."""
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def from_template(self, request):
        """
        Criar orçamento a partir de template.
        
        POST /api/v1/budget/budgets/from_template/
        {
            "template_type": "residential_t2",
            "project_id": "uuid-do-projecto",
            "island": "SANTIAGO",
            "name": "Orçamento T2 Personalizado"
        }
        """
        serializer = BudgetCreateFromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        calculator = BudgetCalculator()
        budget = calculator.create_budget_from_template(
            project_id=serializer.validated_data['project_id'],
            template_type=serializer.validated_data['template_type'],
            user=request.user,
            island=serializer.validated_data.get('island', 'SANTIAGO'),
            custom_name=serializer.validated_data.get('name')
        )
        
        return Response(
            SimpleBudgetSerializer(budget).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicar um orçamento existente.
        
        POST /api/v1/budget/budgets/{id}/duplicate/
        {
            "name": "Cópia do Orçamento",
            "increment_version": true
        }
        """
        budget = self.get_object()
        
        calculator = BudgetCalculator()
        new_budget = calculator.duplicate_budget(
            budget_id=budget.id,
            user=request.user,
            new_name=request.data.get('name'),
            increment_version=request.data.get('increment_version', True)
        )
        
        return Response(
            SimpleBudgetSerializer(new_budget).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def compare(self, request, pk=None):
        """
        Comparar duas versões do orçamento.
        
        POST /api/v1/budget/budgets/{id}/compare/
        {
            "version_a": "1.0",
            "version_b": "2.0"
        }
        """
        budget = self.get_object()
        
        serializer = BudgetCompareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        calculator = BudgetCalculator()
        comparison = calculator.compare_versions(
            budget_id=budget.project_id,  # Compara orçamentos do mesmo projecto
            version_a=serializer.validated_data['version_a'],
            version_b=serializer.validated_data['version_b']
        )
        
        return Response(comparison)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Aprovar o orçamento.
        
        POST /api/v1/budget/budgets/{id}/approve/
        """
        budget = self.get_object()
        
        if budget.status == SimpleBudget.STATUS_APPROVED:
            return Response(
                {'detail': 'Orçamento já está aprovado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.approve(request.user)
        
        return Response(
            SimpleBudgetSerializer(budget).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Obter resumo estatístico do orçamento.
        
        GET /api/v1/budget/budgets/{id}/summary/
        """
        budget = self.get_object()
        
        calculator = BudgetCalculator()
        summary = calculator.get_budget_summary(budget.id)
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def import_excel(self, request, pk=None):
        """
        Importar items de um ficheiro Excel.
        
        POST /api/v1/budget/budgets/{id}/import_excel/
        Multipart form com campo 'file'
        """
        budget = self.get_object()
        
        serializer = ExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        importer = ExcelImporter(budget)
        result = importer.import_from_file(serializer.validated_data['file'])
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk=None):
        """
        Exportar orçamento para Excel.
        
        GET /api/v1/budget/budgets/{id}/export_excel/
        """
        budget = self.get_object()
        
        exporter = ExcelExporter(budget)
        excel_data = exporter.export_to_bytes()
        
        filename = f"orcamento_{budget.name.replace(' ', '_')}_v{budget.version}.xlsx"
        
        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class BudgetItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir items de orçamento.
    
    list: Listar items de um orçamento
    create: Adicionar item ao orçamento
    update: Actualizar item
    destroy: Remover item
    """
    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'price_source']
    ordering_fields = ['line_number', 'total']
    ordering = ['line_number']
    
    def get_queryset(self):
        """Filtrar por orçamento."""
        queryset = super().get_queryset()
        budget_id = self.request.query_params.get('budget')
        if budget_id:
            queryset = queryset.filter(budget_id=budget_id)
        return queryset


class CrowdsourcedPriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para preços crowdsourced.
    
    list: Listar preços reportados
    create: Reportar novo preço
    """
    queryset = CrowdsourcedPrice.objects.all()
    serializer_class = CrowdsourcedPriceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'island']
    search_fields = ['item_name', 'location', 'supplier']
    ordering_fields = ['created_at', 'price_cve']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar preços do utilizador ou verificados."""
        queryset = super().get_queryset()
        
        # Se não for admin, mostrar apenas:
        # - Próprios preços reportados
        # - Preços verificados
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(reported_by=self.request.user) | 
                Q(status=CrowdsourcedPrice.STATUS_VERIFIED)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """
        Top contribuidores (gamificação).
        
        GET /api/v1/budget/crowdsourced/leaderboard/
        """
        scores = UserPriceScore.objects.select_related('user').order_by('-total_points')[:20]
        
        return Response({
            'count': scores.count(),
            'results': UserPriceScoreSerializer(scores, many=True).data
        })
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verificar (aprovar) um preço reportado.
        
        POST /api/v1/budget/crowdsourced/{id}/verify/
        {
            "action": "verify",
            "points": 10,
            "link_to_official": "uuid-do-item-oficial"
        }
        """
        price = self.get_object()
        
        # Apenas admins podem verificar
        if not request.user.is_staff:
            return Response(
                {'detail': 'Apenas administradores podem verificar preços.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if price.status != CrowdsourcedPrice.STATUS_PENDING:
            return Response(
                {'detail': f'Preço já está {price.get_status_display().lower()}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CrowdsourcedPriceVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        if action_type == 'verify':
            price.verify(request.user, serializer.validated_data.get('points', 10))
            
            # Linkar a item oficial se especificado
            link_id = serializer.validated_data.get('link_to_official')
            if link_id:
                try:
                    official_item = LocalPriceItem.objects.get(id=link_id)
                    price.linked_price_item = official_item
                    price.save(update_fields=['linked_price_item'])
                except LocalPriceItem.DoesNotExist:
                    pass
            
            return Response({
                'status': 'verified',
                'points_awarded': price.points_earned,
                'message': 'Preço verificado e pontos atribuídos ao utilizador.'
            })
        
        else:  # reject
            price.reject(
                request.user,
                serializer.validated_data.get('rejection_reason', '')
            )
            return Response({
                'status': 'rejected',
                'message': 'Preço rejeitado.'
            })


class UserPriceScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para pontuações de utilizadores (gamificação).
    
    list: Listar rankings
    retrieve: Ver pontuação de um utilizador
    """
    queryset = UserPriceScore.objects.all()
    serializer_class = UserPriceScoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['total_points', 'prices_verified']
    ordering = ['-total_points']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Ver própria pontuação.
        
        GET /api/v1/budget/scores/me/
        """
        score, created = UserPriceScore.objects.get_or_create(user=request.user)
        return Response(UserPriceScoreSerializer(score).data)


class ConstructionExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet para despesas de construção."""
    
    queryset = ConstructionExpense.objects.all()
    serializer_class = ConstructionExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'task', 'category', 'status', 'supplier']
    search_fields = ['description', 'invoice_number', 'supplier']
    ordering_fields = ['payment_date', 'amount_cve', 'created_at']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        """Filtrar por projecto se especificado."""
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def project_summary(self, request):
        """
        Resumo financeiro de um projecto (Budget vs Actual).
        GET /api/v1/budget/expenses/project_summary/?project=<uuid>
        """
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'detail': 'O parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = FinancialConsolidationService()
        data = service.get_project_financial_status(project_id)
        
        if not data:
            return Response(
                {'detail': 'Projecto não encontrado ou sem dados financeiros.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(data)


class ConstructionAdvanceViewSet(viewsets.ModelViewSet):
    """ViewSet para adiantamentos a empreiteiros."""
    
    queryset = ConstructionAdvance.objects.all()
    serializer_class = ConstructionAdvanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'is_settled', 'recipient']
    search_fields = ['description', 'recipient']
    ordering_fields = ['payment_date', 'amount_cve', 'created_at']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        """Filtrar por projecto se especificado."""
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        """Marcar adiantamento como liquidado."""
        advance = self.get_object()
        advance.is_settled = True
        advance.settled_at = timezone.now()
        advance.status = ConstructionAdvance.STATUS_PAID
        advance.save()
        return Response(ConstructionAdvanceSerializer(advance).data)
