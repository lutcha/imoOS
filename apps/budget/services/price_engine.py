"""
Price Engine — Lógica de sugestão de preços.

Fornece sugestões inteligentes de preços baseadas em:
1. Base oficial (LocalPriceItem)
2. Média de crowdsourced (últimos 3 meses)
3. Similar items (mesma categoria)
"""
from decimal import Decimal
from datetime import timedelta
from typing import Optional
from django.db.models import Avg, StdDev, Q
from django.utils import timezone

from apps.budget.models import LocalPriceItem, CrowdsourcedPrice


class PriceEngine:
    """
    Motor de sugestão de preços para Cabo Verde.
    
    Considera variações regionais entre ilhas e histórico de preços.
    """
    
    # Threshold para detecção de anomalia (desvios padrão)
    ANOMALY_THRESHOLD = 2.0
    
    # Peso para cada fonte de preço na sugestão combinada
    WEIGHT_OFFICIAL = 0.6
    WEIGHT_CROWDSOURCED = 0.3
    WEIGHT_SIMILAR = 0.1
    
    def suggest_price(
        self, 
        item_name: str, 
        island: str, 
        category: str,
        unit: Optional[str] = None
    ) -> dict:
        """
        Sugerir preço baseado em múltiplas fontes.
        
        Args:
            item_name: Nome do item a pesquisar
            island: Código da ilha (ex: 'SANTIAGO')
            category: Categoria do item
            unit: Unidade de medida (opcional)
            
        Returns:
            Dicionário com preço sugerido e metadados
        """
        suggestions = {
            'item_name': item_name,
            'island': island,
            'category': category,
            'suggested_price': None,
            'confidence': 'low',
            'sources': {}
        }
        
        # 1. Buscar na base oficial
        official_price = self._get_official_price(item_name, island, category, unit)
        if official_price:
            suggestions['sources']['official'] = official_price
            suggestions['confidence'] = 'high'
        
        # 2. Buscar média crowdsourced (últimos 3 meses)
        crowd_price = self._get_crowdsourced_price(item_name, island, category)
        if crowd_price:
            suggestions['sources']['crowdsourced'] = crowd_price
            if suggestions['confidence'] == 'high':
                suggestions['confidence'] = 'very_high'
        
        # 3. Buscar itens similares
        similar_price = self._get_similar_price(item_name, island, category, unit)
        if similar_price:
            suggestions['sources']['similar'] = similar_price
            if suggestions['confidence'] == 'low':
                suggestions['confidence'] = 'medium'
        
        # Calcular preço sugerido combinado
        suggestions['suggested_price'] = self._calculate_weighted_price(
            suggestions['sources']
        )
        
        return suggestions
    
    def _get_official_price(
        self, 
        item_name: str, 
        island: str, 
        category: str,
        unit: Optional[str] = None
    ) -> Optional[dict]:
        """Buscar preço na base oficial."""
        # Buscar por nome exacto ou código
        query = LocalPriceItem.objects.filter(
            Q(name__iexact=item_name) | Q(code__iexact=item_name),
            category=category,
            is_verified=True
        )
        
        if unit:
            query = query.filter(unit=unit)
        
        item = query.first()
        if item:
            price = item.get_price_for_island(island)
            return {
                'price': float(price),
                'unit': item.unit,
                'source': item.source,
                'item_code': item.code,
                'last_updated': item.last_updated.isoformat() if item.last_updated else None
            }
        return None
    
    def _get_crowdsourced_price(
        self, 
        item_name: str, 
        island: str, 
        category: str
    ) -> Optional[dict]:
        """Buscar média de preços crowdsourced dos últimos 3 meses."""
        three_months_ago = timezone.now() - timedelta(days=90)
        
        avg_result = CrowdsourcedPrice.objects.filter(
            item_name__iexact=item_name,
            island=island,
            category=category,
            status=CrowdsourcedPrice.STATUS_VERIFIED,
            created_at__gte=three_months_ago
        ).aggregate(
            avg_price=Avg('price_cve'),
            count=models.Count('id')
        )
        
        if avg_result['avg_price'] and avg_result['count'] >= 3:
            return {
                'price': float(avg_result['avg_price']),
                'sample_count': avg_result['count'],
                'period': 'last_90_days'
            }
        return None
    
    def _get_similar_price(
        self, 
        item_name: str, 
        island: str, 
        category: str,
        unit: Optional[str] = None
    ) -> Optional[dict]:
        """Buscar preço de itens similares na mesma categoria."""
        # Extrair palavras-chave do nome (primeiras 3 palavras)
        keywords = item_name.split()[:3]
        
        query = LocalPriceItem.objects.filter(
            category=category,
            is_verified=True
        )
        
        # Aplicar filtro de palavras-chave
        for keyword in keywords:
            query = query.filter(name__icontains=keyword)
        
        if unit:
            query = query.filter(unit=unit)
        
        # Excluir o item exacto se existir
        query = query.exclude(name__iexact=item_name)
        
        similar_items = query[:5]  # Top 5 similares
        
        if similar_items:
            prices = [item.get_price_for_island(island) for item in similar_items]
            avg_price = sum(prices) / len(prices)
            
            return {
                'price': float(avg_price),
                'similar_items_count': len(prices),
                'price_range': {
                    'min': float(min(prices)),
                    'max': float(max(prices))
                }
            }
        return None
    
    def _calculate_weighted_price(self, sources: dict) -> Optional[float]:
        """Calcular preço ponderado baseado nas fontes disponíveis."""
        weighted_sum = 0.0
        total_weight = 0.0
        
        if 'official' in sources:
            weighted_sum += sources['official']['price'] * self.WEIGHT_OFFICIAL
            total_weight += self.WEIGHT_OFFICIAL
        
        if 'crowdsourced' in sources:
            weighted_sum += sources['crowdsourced']['price'] * self.WEIGHT_CROWDSOURCED
            total_weight += self.WEIGHT_CROWDSOURCED
        
        if 'similar' in sources:
            weighted_sum += sources['similar']['price'] * self.WEIGHT_SIMILAR
            total_weight += self.WEIGHT_SIMILAR
        
        if total_weight > 0:
            return round(weighted_sum / total_weight, 2)
        return None
    
    def detect_price_anomaly(
        self, 
        price: Decimal, 
        item_name: str, 
        island: str,
        category: str
    ) -> dict:
        """
        Detectar se preço é anômalo (muito alto/baixo).
        
        Args:
            price: Preço a verificar
            item_name: Nome do item
            island: Código da ilha
            category: Categoria do item
            
        Returns:
            Dicionário com resultado da análise
        """
        result = {
            'is_anomaly': False,
            'price': float(price),
            'expected_range': None,
            'deviation_pct': None,
            'message': 'Preço dentro da faixa esperada'
        }
        
        # Buscar estatísticas de preços para o item
        stats = self._get_price_statistics(item_name, island, category)
        
        if not stats or stats['count'] < 5:
            # Sem dados suficientes — não podemos determinar anomalia
            result['message'] = 'Dados insuficientes para análise'
            return result
        
        mean = stats['mean']
        std_dev = stats['std_dev'] or 0
        
        # Calcular faixa esperada (±2 desvios padrão)
        lower_bound = mean - (self.ANOMALY_THRESHOLD * std_dev)
        upper_bound = mean + (self.ANOMALY_THRESHOLD * std_dev)
        
        result['expected_range'] = {
            'min': round(max(0, lower_bound), 2),
            'max': round(upper_bound, 2),
            'mean': round(mean, 2)
        }
        
        # Verificar se está fora da faixa
        if float(price) < lower_bound:
            result['is_anomaly'] = True
            deviation = ((float(price) - mean) / mean) * 100 if mean > 0 else 0
            result['deviation_pct'] = round(deviation, 2)
            result['message'] = f'Preço {abs(deviation):.1f}% abaixo da média — possível erro ou promoção'
        elif float(price) > upper_bound:
            result['is_anomaly'] = True
            deviation = ((float(price) - mean) / mean) * 100
            result['deviation_pct'] = round(deviation, 2)
            result['message'] = f'Preço {deviation:.1f}% acima da média — possível erro ou premium'
        
        return result
    
    def _get_price_statistics(
        self, 
        item_name: str, 
        island: str, 
        category: str
    ) -> Optional[dict]:
        """Calcular estatísticas de preços para um item."""
        # Combinar preços oficiais e crowdsourced
        three_months_ago = timezone.now() - timedelta(days=90)
        
        official_prices = LocalPriceItem.objects.filter(
            name__iexact=item_name,
            category=category,
            is_verified=True
        ).values_list('price_santiago', flat=True)  # Usar Santiago como referência
        
        crowd_prices = CrowdsourcedPrice.objects.filter(
            item_name__iexact=item_name,
            category=category,
            status=CrowdsourcedPrice.STATUS_VERIFIED,
            created_at__gte=three_months_ago
        ).values_list('price_cve', flat=True)
        
        # Combinar todos os preços
        all_prices = list(official_prices) + list(crowd_prices)
        
        if len(all_prices) < 5:
            return None
        
        # Calcular estatísticas manualmente
        prices = [float(p) for p in all_prices if p]
        if not prices:
            return None
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        return {
            'count': len(prices),
            'mean': mean,
            'std_dev': std_dev,
            'min': min(prices),
            'max': max(prices)
        }
    
    def get_price_trend(
        self, 
        item_name: str, 
        island: str,
        months: int = 6
    ) -> dict:
        """
        Analisar tendência de preço ao longo do tempo.
        
        Args:
            item_name: Nome do item
            island: Código da ilha
            months: Número de meses para análise
            
        Returns:
            Dicionário com tendência e variação percentual
        """
        since_date = timezone.now() - timedelta(days=30 * months)
        
        # Buscar preços crowdsourced ao longo do tempo
        prices = CrowdsourcedPrice.objects.filter(
            item_name__iexact=item_name,
            island=island,
            status=CrowdsourcedPrice.STATUS_VERIFIED,
            created_at__gte=since_date
        ).order_by('created_at')
        
        if prices.count() < 3:
            return {
                'trend': 'unknown',
                'message': 'Dados insuficientes para análise de tendência',
                'data_points': prices.count()
            }
        
        # Calcular média móvel simples
        first_half = prices[:prices.count() // 2]
        second_half = prices[prices.count() // 2:]
        
        avg_first = sum(p.price_cve for p in first_half) / len(first_half)
        avg_second = sum(p.price_cve for p in second_half) / len(second_half)
        
        variation = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
        
        if variation > 5:
            trend = 'increasing'
            message = f'Preço em alta (+{variation:.1f}%)'
        elif variation < -5:
            trend = 'decreasing'
            message = f'Preço em baixa ({variation:.1f}%)'
        else:
            trend = 'stable'
            message = f'Preço estável ({variation:+.1f}%)'
        
        return {
            'trend': trend,
            'variation_pct': round(variation, 2),
            'message': message,
            'avg_first_period': float(avg_first),
            'avg_second_period': float(avg_second),
            'data_points': prices.count()
        }


# Import no final para evitar circular import
from django.db import models
