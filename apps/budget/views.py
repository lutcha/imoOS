"""
Budget views - ImoOS
APIs para preços, orçamentos e gamificação.
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Q, Sum, F, Count
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsTenantMember
from .models import (
    PriceCategory, PriceItem, CrowdsourcedPrice,
    Budget, BudgetItem, UserPoints, PointsLog
)
from .serializers import (
    PriceCategorySerializer, PriceItemSerializer, PriceItemListSerializer,
    CrowdsourcedPriceSerializer, CrowdsourcedPriceCreateSerializer,
    BudgetListSerializer, BudgetDetailSerializer, BudgetCreateSerializer,
    BudgetItemSerializer, BudgetItemCreateSerializer,
    UserPointsSerializer, PointsLogSerializer, LeaderboardEntrySerializer,
    BudgetExportSerializer
)
from .filters import PriceItemFilter, BudgetFilter, CrowdsourcedPriceFilter
from .renderers import BudgetPDFRenderer, BudgetExcelRenderer


class PriceCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorias de preços"""
    queryset = PriceCategory.objects.filter(is_active=True)
    serializer_class = PriceCategorySerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class PriceItemViewSet(viewsets.ModelViewSet):
    """ViewSet para itens de preços"""
    queryset = PriceItem.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PriceItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price_santiago', 'last_updated', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PriceItemListSerializer
        return PriceItemSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Busca avançada por nome ou descrição"""
        query = request.query_params.get('q', '')
        island = request.query_params.get('island', 'SANTIAGO')
        category = request.query_params.get('category')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category__code=category)
        
        # Ordenar por relevância (nome começa com query primeiro)
        queryset = queryset.order_by('name')[:50]
        
        serializer = PriceItemListSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response({
            'query': query,
            'island': island,
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def island_price(self, request, pk=None):
        """Retorna preço específico para uma ilha"""
        item = self.get_object()
        island = request.query_params.get('island', 'SANTIAGO')
        
        valid_islands = [code for code, _ in PriceItem.ISLANDS]
        if island not in valid_islands:
            return Response(
                {'error': f'Ilha inválida. Use: {valid_islands}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        price = item.get_price_for_island(island)
        return Response({
            'item_id': str(item.id),
            'item_name': item.name,
            'island': island,
            'price': price,
            'unit': item.unit,
            'is_fallback': not getattr(item, f'price_{island.lower()}', None)
        })


class CrowdsourcedPriceViewSet(viewsets.ModelViewSet):
    """ViewSet para preços crowdsourced"""
    queryset = CrowdsourcedPrice.objects.all()
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CrowdsourcedPriceFilter
    ordering_fields = ['created_at', 'price_cve']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CrowdsourcedPriceCreateSerializer
        return CrowdsourcedPriceSerializer
    
    def get_queryset(self):
        """Filtra baseado no utilizador"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Admin vê todos, outros só veem os seus ou aprovados
        if not user.is_staff:
            queryset = queryset.filter(
                Q(reported_by=user) | Q(status='APPROVED')
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Cria preço e atribui pontos"""
        with transaction.atomic():
            # Guardar preço
            crowdsourced = serializer.save()
            
            # Atualizar pontos do utilizador
            user_points, _ = UserPoints.objects.get_or_create(
                user=crowdsourced.reported_by,
                defaults={'total_points': 0}
            )
            user_points.add_points(
                crowdsourced.points_earned,
                f"Preço reportado: {crowdsourced.item_name}"
            )
            user_points.increment_prices_reported()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def pending(self, request):
        """Lista preços pendentes de aprovação (admin only)"""
        queryset = self.get_queryset().filter(status='PENDING')
        serializer = CrowdsourcedPriceSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def approve(self, request, pk=None):
        """Aprova um preço crowdsourced e cria PriceItem"""
        crowdsourced = self.get_object()
        
        if crowdsourced.status != 'PENDING':
            return Response(
                {'error': f"Preço já está {crowdsourced.get_status_display()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Criar ou atualizar PriceItem
            category = crowdsourced.category
            if not category:
                # Criar categoria default se não especificada
                category, _ = PriceCategory.objects.get_or_create(
                    code='CROWD',
                    defaults={'name': 'Crowdsourced', 'icon': '👥'}
                )
            
            # Verificar se já existe item com mesmo nome na ilha
            island_field = f"price_{crowdsourced.island.lower()}"
            
            price_item, created = PriceItem.objects.get_or_create(
                name=crowdsourced.item_name,
                category=category,
                defaults={
                    'unit': 'un',  # Default unit
                    'price_santiago': crowdsourced.price_cve,
                    island_field: crowdsourced.price_cve,
                    'source': f"Crowdsourced by {crowdsourced.reported_by.email}",
                    'is_verified': True,
                }
            )
            
            if not created:
                # Atualizar preço para a ilha específica
                setattr(price_item, island_field, crowdsourced.price_cve)
                price_item.save()
            
            # Atualizar crowdsourced
            crowdsourced.status = 'APPROVED'
            crowdsourced.reviewed_by = request.user
            crowdsourced.reviewed_at = timezone.now()
            crowdsourced.linked_item = price_item
            crowdsourced.save()
            
            # Bonus points por aprovação
            user_points = UserPoints.objects.get(user=crowdsourced.reported_by)
            user_points.add_points(20, f"Preço aprovado: {crowdsourced.item_name}")
            user_points.increment_prices_verified()
        
        return Response({
            'status': 'approved',
            'price_item_id': str(price_item.id),
            'crowdsourced': CrowdsourcedPriceSerializer(crowdsourced).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def reject(self, request, pk=None):
        """Rejeita um preço crowdsourced"""
        crowdsourced = self.get_object()
        reason = request.data.get('reason', '')
        
        if crowdsourced.status != 'PENDING':
            return Response(
                {'error': f"Preço já está {crowdsourced.get_status_display()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        crowdsourced.status = 'REJECTED'
        crowdsourced.reviewed_by = request.user
        crowdsourced.reviewed_at = timezone.now()
        crowdsourced.review_notes = reason
        crowdsourced.save()
        
        return Response({
            'status': 'rejected',
            'reason': reason,
            'crowdsourced': CrowdsourcedPriceSerializer(crowdsourced).data
        })


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet para orçamentos"""
    queryset = Budget.objects.all()
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BudgetFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'total', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BudgetListSerializer
        elif self.action == 'create':
            return BudgetCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return BudgetDetailSerializer
        return BudgetDetailSerializer
    
    def get_queryset(self):
        """Filtra orçamentos do tenant"""
        queryset = super().get_queryset()
        
        # Filtrar por projeto se especificado
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project', 'created_by').prefetch_related('items', 'items__price_item')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalcula totais do orçamento"""
        budget = self.get_object()
        budget.recalculate_totals()
        return Response({
            'message': 'Orçamento recalculado com sucesso',
            'budget': BudgetDetailSerializer(budget).data
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplica um orçamento"""
        budget = self.get_object()
        
        with transaction.atomic():
            # Criar novo orçamento baseado no original
            new_budget = Budget.objects.create(
                project=budget.project,
                name=f"{budget.name} (Cópia)",
                description=budget.description,
                island=budget.island,
                contingency_pct=budget.contingency_pct,
                status='DRAFT',
                created_by=request.user
            )
            
            # Copiar itens
            for item in budget.items.all():
                BudgetItem.objects.create(
                    budget=new_budget,
                    price_item=item.price_item,
                    custom_name=item.custom_name,
                    custom_unit=item.custom_unit,
                    custom_unit_price=item.custom_unit_price,
                    quantity=item.quantity,
                    order=item.order,
                    notes=item.notes
                )
            
            new_budget.recalculate_totals()
        
        return Response({
            'message': 'Orçamento duplicado com sucesso',
            'budget': BudgetDetailSerializer(new_budget).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def set_baseline(self, request, pk=None):
        """Define orçamento como baseline (congelado)"""
        budget = self.get_object()
        
        if budget.status == 'ARCHIVED':
            return Response(
                {'error': 'Orçamento arquivado não pode ser definido como baseline'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'BASELINE'
        budget.save(update_fields=['status'])
        
        return Response({
            'message': 'Orçamento definido como baseline',
            'budget': BudgetDetailSerializer(budget).data
        })
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Exporta orçamento para PDF ou Excel"""
        budget = self.get_object()
        serializer = BudgetExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        export_format = serializer.validated_data['format']
        include_notes = serializer.validated_data.get('include_notes', True)
        
        if export_format == 'pdf':
            renderer = BudgetPDFRenderer()
            return renderer.render(budget, include_notes)
        elif export_format == 'excel':
            renderer = BudgetExcelRenderer()
            return renderer.render(budget, include_notes)
        
        return Response(
            {'error': 'Formato inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )


class BudgetItemViewSet(viewsets.ModelViewSet):
    """ViewSet para itens de orçamento"""
    queryset = BudgetItem.objects.all()
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'created_at']
    ordering = ['order', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BudgetItemCreateSerializer
        return BudgetItemSerializer
    
    def get_queryset(self):
        """Filtra itens de um orçamento específico"""
        queryset = super().get_queryset()
        budget_id = self.kwargs.get('budget_pk')
        if budget_id:
            queryset = queryset.filter(budget_id=budget_id)
        return queryset.select_related('price_item', 'price_item__category')
    
    def perform_create(self, serializer):
        """Cria item e recalcula orçamento"""
        budget_id = self.kwargs.get('budget_pk')
        budget = Budget.objects.get(id=budget_id)
        
        # Verificar se orçamento pode ser editado
        if budget.status in ['BASELINE', 'ARCHIVED']:
            raise PermissionDenied(
                'Não é possível editar orçamentos baseline ou arquivados'
            )
        
        serializer.save(budget=budget)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request, budget_pk=None):
        """Cria múltiplos itens de uma vez"""
        budget = Budget.objects.get(id=budget_pk)
        
        if budget.status in ['BASELINE', 'ARCHIVED']:
            return Response(
                {'error': 'Não é possível editar orçamentos baseline ou arquivados'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        items_data = request.data.get('items', [])
        if not items_data:
            return Response(
                {'error': 'Nenhum item fornecido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_items = []
        with transaction.atomic():
            for item_data in items_data:
                serializer = BudgetItemCreateSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                item = serializer.save(budget=budget)
                created_items.append(item)
        
        return Response({
            'count': len(created_items),
            'items': BudgetItemSerializer(created_items, many=True).data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def leaderboard(request):
    """Retorna leaderboard dos maiores contribuidores"""
    top_users = UserPoints.objects.select_related('user').order_by('-total_points')[:20]
    
    results = []
    for rank, user_points in enumerate(top_users, 1):
        results.append({
            'rank': rank,
            'user_name': user_points.user.email,
            'total_points': user_points.total_points,
            'prices_reported': user_points.prices_reported,
            'badges': user_points.badges
        })
    
    return Response({
        'count': len(results),
        'results': results
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def my_points(request):
    """Retorna pontos e histórico do utilizador atual"""
    user = request.user
    
    user_points, _ = UserPoints.objects.get_or_create(
        user=user,
        defaults={'total_points': 0}
    )
    
    # Recent logs
    recent_logs = PointsLog.objects.filter(user=user).order_by('-created_at')[:10]
    
    return Response({
        'user': user.email,
        'total_points': user_points.total_points,
        'prices_reported': user_points.prices_reported,
        'prices_verified': user_points.prices_verified,
        'badges': user_points.badges,
        'recent_activity': PointsLogSerializer(recent_logs, many=True).data
    })


class UserPointsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para pontos de utilizadores (readonly)"""
    queryset = UserPoints.objects.select_related('user')
    serializer_class = UserPointsSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['total_points', 'prices_reported']
    ordering = ['-total_points']
