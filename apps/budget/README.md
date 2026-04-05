# App Budget — ImoOS

Sistema de orçamentos e base de preços local para Cabo Verde, integrado na plataforma ImoOS.

## Funcionalidades

### 1. Base de Preços Local (`LocalPriceItem`)

Base de dados de preços de materiais, mão-de-obra, equipamentos e serviços específicos para Cabo Verde.

**Características principais:**
- Preços diferenciados por ilha (Santiago, São Vicente, Sal, etc.)
- Fallback automático para preços de Santiago quando ilha não tem preço específico
- Suporte a categorias: MATERIALS, LABOR, EQUIPMENT, SERVICES
- Campos IFC para integração futura com BIM
- Verificação por administradores

**Exemplo de uso:**
```python
from apps.budget.models import LocalPriceItem

# Buscar preço do cimento
item = LocalPriceItem.objects.get(code='CV-001')
preco_santiago = item.get_price_for_island('SANTIAGO')  # 850.00
preco_sal = item.get_price_for_island('SAL')  # 900.00
```

### 2. Orçamentos Simplificados (`SimpleBudget`)

Sistema de orçamentos estilo Excel com:
- Múltiplas versões por projecto
- Cálculo automático de totais por categoria
- Margem de contingência configurável
- Status: Rascunho, Aprovado, Baseline, Arquivado

**Templates disponíveis:**
- `residential_t2`: Apartamento T2 típico
- `residential_t3`: Apartamento T3 típico  
- `commercial_small`: Loja/Escritório pequeno (~50m²)

### 3. Crowdsourcing de Preços (`CrowdsourcedPrice`)

Sistema de gamificação onde utilizadores reportam preços observados:
- Pontos por contribuições verificadas
- Sistema de ranks: Novato → Contribuidor → Especialista → Guru → Lenda
- Moderação por administradores
- Integração automática com base de preços oficial

**Ranks e pontos:**
| Rank | Pontos Necessários |
|------|-------------------|
| Novato | 0 |
| Contribuidor | 50 |
| Especialista | 200 |
| Guru | 500 |
| Lenda | 1000 |

### 4. Price Engine (`PriceEngine`)

Motor de sugestão inteligente de preços:

```python
from apps.budget.services import PriceEngine

engine = PriceEngine()

# Sugerir preço
suggestion = engine.suggest_price(
    item_name='Cimento CP350 50kg',
    island='SANTIAGO',
    category='MATERIALS',
    unit='SACO'
)
# Retorna: preço sugerido, confiança, fontes consultadas

# Detectar anomalias
result = engine.detect_price_anomaly(
    price=Decimal('1500.00'),
    item_name='Cimento CP350 50kg',
    island='SANTIAGO',
    category='MATERIALS'
)
# Retorna: se é anomalia, mensagem, faixa esperada
```

### 5. Import/Export Excel

Importação e exportação de orçamentos em Excel:

```python
from apps.budget.services import ExcelImporter, ExcelExporter

# Importar
importer = ExcelImporter(budget)
result = importer.import_from_file(excel_file)

# Exportar
exporter = ExcelExporter(budget)
excel_bytes = exporter.export_to_bytes()
```

## API Endpoints

### Base de Preços
```
GET    /api/v1/budget/price-items/              # Listar items
GET    /api/v1/budget/price-items/?search=cimento&island=SANTIAGO
POST   /api/v1/budget/price-items/suggest/      # Sugerir preço
POST   /api/v1/budget/price-items/check_anomaly/ # Verificar anomalia
```

### Orçamentos
```
GET    /api/v1/budget/budgets/                  # Listar orçamentos
POST   /api/v1/budget/budgets/                  # Criar orçamento
POST   /api/v1/budget/budgets/from_template/    # Criar de template
GET    /api/v1/budget/budgets/{id}/             # Ver detalhes
POST   /api/v1/budget/budgets/{id}/duplicate/   # Duplicar
POST   /api/v1/budget/budgets/{id}/compare/     # Comparar versões
POST   /api/v1/budget/budgets/{id}/approve/     # Aprovar
GET    /api/v1/budget/budgets/{id}/summary/     # Resumo
POST   /api/v1/budget/budgets/{id}/import_excel/ # Importar Excel
GET    /api/v1/budget/budgets/{id}/export_excel/ # Exportar Excel
```

### Items de Orçamento
```
GET    /api/v1/budget/budget-items/?budget={id} # Listar items
POST   /api/v1/budget/budget-items/             # Adicionar item
PATCH  /api/v1/budget/budget-items/{id}/        # Actualizar
DELETE /api/v1/budget/budget-items/{id}/        # Remover
```

### Crowdsourcing
```
GET    /api/v1/budget/crowdsourced/             # Listar preços
POST   /api/v1/budget/crowdsourced/             # Reportar preço
GET    /api/v1/budget/crowdsourced/leaderboard/ # Top contribuidores
POST   /api/v1/budget/crowdsourced/{id}/verify/ # Verificar (admin)
```

### Gamificação
```
GET    /api/v1/budget/scores/                   # Rankings
GET    /api/v1/budget/scores/me/                # Meu score
```

## Seed Data

Para carregar os dados iniciais de preços:

```bash
python manage.py loaddata apps/budget/fixtures/cv_prices.json
```

Inclui **50+ itens** reais de Cabo Verde:
- 35 materiais de construção
- 7 tipos de mão-de-obra
- 4 equipamentos
- 3 serviços profissionais

## Configuração

Adicionar a `TENANT_APPS` em `config/settings/base.py`:

```python
TENANT_APPS = [
    # ... outros apps
    'apps.budget',
]
```

## Testes

```bash
# Todos os testes do app
python manage.py test apps.budget.tests

# Testes específicos
python manage.py test apps.budget.tests.test_models
python manage.py test apps.budget.tests.test_services
python manage.py test apps.budget.tests.test_tenant_isolation
```

## Admin

Interface administrativa disponível em `/admin/budget/`:

- **LocalPriceItem**: Gestão da base de preços com badges coloridos
- **SimpleBudget**: Gestão de orçamentos com items inline
- **CrowdsourcedPrice**: Moderação de preços reportados
- **UserPriceScore**: Visualização de rankings

## Isolamento de Tenants

⚠️ **CRÍTICO**: Todos os modelos herdam de `TenantAwareModel` e respeitam o isolamento por schema do django-tenants. Os testes em `test_tenant_isolation.py` verificam:

- Items de preço não são visíveis entre tenants
- Orçamentos mantêm-se isolados
- Crowdsourced prices são por tenant
- Códigos podem repetir entre tenants (tabelas físicas separadas)

## Dependências

```
django>=4.2.9
django-tenants>=3.5.0
openpyxl>=3.1.0  # Para import/export Excel
```

## Notas sobre Preços em CV

- **Santiago**: Preço base (maior oferta, menor custo logístico)
- **Sal/Boa Vista**: Preços mais altos (ilhas turísticas, importação)
- **Santo Antão**: Preços intermediários (agricultura, produção local)
- **Brava/Fogo**: Preços elevados (acesso difícil, menor mercado)

Materiais importados (cimento, ferro, cerâmicas) têm variações significativas entre ilhas devido ao frete marítimo.
