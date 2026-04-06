# Testes E2E - ImoOS

Esta pasta contém testes End-to-End (E2E) que validam fluxos completos do sistema, simulando a interação real dos utilizadores.

## Estrutura

```
tests/e2e/
├── conftest.py                    # Fixtures específicas para E2E
├── test_complete_sales_flow.py    # Lead → Reserva → Contrato → Assinatura
├── test_project_creation_flow.py  # Contrato → Projeto de Obra → Tasks
├── test_construction_progress.py  # Progresso → Milestone → Pagamento
├── test_mobile_sync.py            # Offline → Sync → Online
├── test_whatsapp_notifications.py # Notificações em diferentes eventos
├── test_tenant_isolation_e2e.py   # Isolamento entre tenants (E2E)
└── test_performance.py            # Performance de endpoints críticos
```

## Executando os Testes

### Todos os testes E2E
```bash
pytest tests/e2e/ -v -m e2e
```

### Teste específico
```bash
pytest tests/e2e/test_complete_sales_flow.py -v
```

### Com cobertura
```bash
pytest tests/e2e/ -v --cov=apps --cov-report=html
```

### Apenas testes rápidos (excluir performance)
```bash
pytest tests/e2e/ -v -m "e2e and not performance"
```

## Marcadores (Markers)

- `e2e`: Todos os testes end-to-end
- `performance`: Testes de performance (mais lentos)
- `slow`: Testes que podem demorar mais
- `isolation`: Testes de isolamento de tenant

## Fluxos Testados

### 1. Fluxo Completo de Venda (`test_complete_sales_flow.py`)

```
Lead → Reserva → Contrato → Assinatura → Projeto de Obra
```

**Cenários:**
- Criar lead e converter em reserva
- Criar contrato a partir de reserva
- Fluxo de assinatura digital
- Verificação de integridade dos dados

### 2. Criação de Projeto de Obra (`test_project_creation_flow.py`)

```
Contrato Assinado → Projeto → Fases → Tasks → Atribuição
```

**Cenários:**
- Inicialização automática de projeto
- Criação de fases padrão
- Criação de tasks
- Atribuição e notificações

### 3. Progresso e Pagamentos (`test_construction_progress.py`)

```
Task Concluída → Milestone → Pagamento → Notificação
```

**Cenários:**
- Geração de pagamento por milestone
- Cálculo de EVM (Earned Value Management)
- Tracking de pagamentos

### 4. Mobile Sync (`test_mobile_sync.py`)

```
Offline → Queue → Sync → Online
```

**Cenários:**
- Criação de tasks offline
- Upload de fotos com compressão
- Resolução de conflitos
- Sincronização incremental

### 5. WhatsApp Notifications (`test_whatsapp_notifications.py`)

**Eventos:**
- Novo lead
- Confirmação de reserva
- Lembrete de visita
- Pedido de assinatura
- Confirmação de pagamento
- Atribuição de task
- Conclusão de milestone

### 6. Tenant Isolation (`test_tenant_isolation_e2e.py`)

**Verificações:**
- Acesso cruzado negado
- Isolamento via JWT
- Isolamento de workflows
- Isolamento de notificações

### 7. Performance (`test_performance.py`)

**Métricas:**
- Dashboard: < 2 segundos
- API Gantt: < 500ms
- Listagens: < 1 segundo
- Relatórios: < 3 segundos

## Fixtures E2E

### Clientes
- `e2e_api_client`: Cliente API base
- `authenticated_client`: Cliente autenticado

### Dados
- `e2e_tenant`: Tenant de teste
- `e2e_user`: Utilizador admin
- `e2e_vendedor`: Vendedor
- `e2e_encarregado`: Encarregado de obra
- `e2e_project`: Projeto imobiliário
- `e2e_unit`: Unidade disponível
- `e2e_lead`: Lead
- `e2e_reservation`: Reserva ativa
- `e2e_contract`: Contrato em rascunho
- `e2e_signed_contract`: Contrato assinado
- `e2e_construction_project`: Projeto de obra
- `e2e_construction_phases`: Fases de construção
- `e2e_construction_tasks`: Tasks de construção

### Mocks
- `mock_whatsapp_service`: Mock do WhatsApp
- `mock_signature_service`: Mock de assinatura
- `mock_s3_storage`: Mock do S3
- `mock_celery_task`: Mock de tasks Celery

## Boas Práticas

1. **Isolamento**: Cada teste deve ser independente
2. **Limpieza**: Dados criados devem ser limpos automaticamente
3. **Realismo**: Simular cenários reais de uso
4. **Performance**: Monitorar tempos de resposta
5. **Idempotência**: Mesmo resultado ao rodar múltiplas vezes

## CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v -m e2e --tb=short
```

## Troubleshooting

### Testes falhando por timeout
Aumentar timeout no pytest:
```bash
pytest tests/e2e/ --timeout=300
```

### Erros de banco de dados
Verificar se as migrações estão aplicadas:
```bash
python manage.py migrate_schemas
```

### Conflitos de porta
Certificar-se de que nenhum servidor está rodando na porta de teste.
