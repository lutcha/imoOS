Product Blueprint — PropTech/Construtech Platform
Nome do Produto:** ImoOS (Proposta)
**Versão:** 1.0 | **Data:** Março 2026 | **Status:** Pronto para Execução

---

## 1. Visão e Escopo do Produto

### 1.1. Visão Estratégica
Criar o **Sistema Operativo das Promotoras e Construtoras** em Cabo Verde, unificando a gestão de empreendimentos, vendas, obra e investimento num único ecossistema, integrado nativamente com o marketplace `imo.cv`.

### 1.2. Proposta de Valor
| Stakeholder | Valor Entregue |
| :--- | :--- |
| **Promotor/Gestor** | Visão holística (Obra + Vendas + Caixa) em tempo real. Controlo de ROI por projeto. |
| **Equipa Comercial** | Leads do `imo.cv` centralizados no CRM. Automatização de follow-up via WhatsApp. |
| **Engenheiro/Obra** | App offline para registo de diário, medições e qualidade. Sem dependência de rede. |
| **Investidor** | Transparência total. Portal para acompanhar progresso físico e financeiro do capital. |
| **Comprador** | Confiança na compra em planta. Acompanhamento da evolução da sua fração. |

### 1.3. Escopo do MVP (Releases 1-3)
O MVP foca na **tração comercial e operacional básica**. Módulos avançados (BIM 5D, Investidores Complexos) ficam para a Fase 2.

| Release | Foco | Módulos Principais | Duração Est. |
| :--- | :--- | :--- | :--- |
| **R1** | **Fundação** | Tenancy, Projetos, Unidades, Inventory, Auth | 12 Semanas |
| **R2** | **Comercial** | Integração imo.cv, CRM, Leads, Reservas | 10 Semanas |
| **R3** | **Operação** | Contratos, Pagamentos, Obra (Mobile Offline), WhatsApp | 14 Semanas |
| **Total MVP** | | **36 Semanas (~9 Meses)** | |

---

## 2. Arquitetura de Alto Nível

### 2.1. Padrão Arquitetural
**Modular Monolith Multi-Tenant**.
Um único código-base backend, logicamente separado por domínios, com isolamento de dados por schema.

### 2.2. Stack Tecnológico
| Camada | Tecnologia | Justificação |
| :--- | :--- | :--- |
| **Backend Core** | Python + Django + DRF | Produtividade, segurança, ecossistema robusto. |
| **Tenancy** | `django-tenants` | Isolamento lógico (schema-per-tenant) nativo. |
| **Frontend Web** | Next.js + React + Tailwind | Performance, SEO (para portais públicos), UI rápida. |
| **Mobile App** | React Native + SQLite | **Offline-first** real, código partilhado com web. |
| **Database** | PostgreSQL + PostGIS | Robustez relacional + dados geoespaciais (terrenos). |
| **Cache/Queue** | Redis + Celery | Tarefas assíncronas (emails, sync imo.cv). |
| **Storage** | AWS S3 (ou compatível) | Documentos, fotos de obra, plantas. |
| **Infra** | Docker + App Platform | Simplicidade inicial. K8s apenas na Fase 2. |

### 2.3. Diagrama de Contexto
```mermaid
graph TD
    UserWeb[Utilizadores Web] -->|HTTPS| CDN[Cloudflare/CDN]
    UserMob[Equipa de Obra] -->|HTTPS/Sync| CDN
    IMO[imo.cv Platform] -->|Webhooks/API| Gateway[API Gateway]
    
    CDN --> Gateway
    Gateway --> Core[Django Core (Modular)]
    
    subgraph "Data Layer"
        Core --> DB[(PostgreSQL Multi-Tenant)]
        Core --> Cache[(Redis)]
        Core --> Store[(Object Storage S3)]
    end
    
    subgraph "Async Workers"
        Core --> Celery[Celery Workers]
        Celery --> Notify[Notification Service]
        Celery --> Sync[Integration Service]
    end
    
    Notify --> WhatsApp[WhatsApp API]
    Notify --> Email[SMTP]
    Sync --> Banks[Bancos/MBE]
```

---

## 3. Modelo de Dados Core (MVP)

Selecionadas as **35 tabelas críticas** para lançar o MVP. As restantes 140+ serão adicionadas iterativamente.

### 3.1. Core & Tenancy (Public Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `tenants` | Dados da empresa cliente (Promotora). | `schema_name` |
| `tenant_settings` | Configurações (moeda, fuso, branding). | `tenant_id` |
| `users` | Utilizadores da plataforma (Login global). | `email` |
| `tenant_users` | Ligação User ↔ Tenant (Roles por empresa). | `user_id`, `tenant_id` |
| `countries` | Catálogo de países (para expansão). | `code` |
| `currencies` | Moedas e taxas de câmbio. | `code` |

### 3.2. Projetos & Inventário (Tenant Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `projects` | Empreendimentos (ex: Residencial X). | `id` |
| `buildings` | Edifícios dentro do projeto. | `project_id` |
| `floors` | Pisos/Blocos. | `building_id` |
| `units` | **Unidade de Venda** (Fração, Loja, Parque). | `id`, `code` |
| `unit_types` | Tipologias (T1, T2, T3). | `name` |
| `unit_pricing` | Preços, descontos, estado comercial. | `unit_id` |
| `unit_media` | Fotos, plantas, renders associados. | `unit_id` |

### 3.3. CRM & Vendas (Tenant Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `leads` | Leads (origem imo.cv ou manual). | `id`, `source` |
| `lead_interactions` | Histórico de contactos (WhatsApp, Email). | `lead_id` |
| `visits` | Registo de visitas ao stand/obra. | `lead_id`, `unit_id` |
| `reservations` | Reservas de unidade (bloqueio temporal). | `unit_id`, `buyer_id` |
| `buyers` | Dados do cliente final (KYC). | `id` |

### 3.4. Financeiro & Contratos (Tenant Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `contracts` | Promessas de Compra e Venda (PCV). | `reservation_id` |
| `payment_plans` | Modelos de planos (ex: 20/80, faseado). | `id` |
| `installments` | Prestações individuais geradas. | `plan_id`, `contract_id` |
| `invoices` | Faturas emitidas. | `installment_id` |
| `payments` | Pagamentos recebidos (reconciliação). | `invoice_id` |

### 3.5. Obra & Execução (Tenant Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `wbs` | Estrutura Analítica do Projeto. | `project_id` |
| `schedule_tasks` | Tarefas do cronograma. | `wbs_id` |
| `daily_logs` | Diário de obra (offline sync). | `project_id`, `date` |
| `inspections` | Checklists de qualidade/segurança. | `task_id` |
| `budget_lines` | Orçamento por capítulo da WBS. | `wbs_id` |

### 3.6. Integração & Marketplace (Tenant Schema)
| Tabela | Descrição | Chave |
| :--- | :--- | :--- |
| `marketplace_channels` | Canais (imo.cv, Idealista, etc.). | `name` |
| `marketplace_listings` | Estado da publicação por canal. | `unit_id`, `channel_id` |
| `marketplace_sync_logs` | Logs de erros/sucesso de sync. | `listing_id` |

---

## 4. Épicos e User Stories (Para Jira)

Organizados por Módulo para facilitar a alocação de equipas.

### 📦 Módulo 1: Tenancy & Core (Release 1)
**Épico:** `CORE-01` — Gestão de Empresas e Utilizadores
*   **US-1.1:** Como Super Admin, quero criar um novo Tenant para que uma nova promotora possa usar a plataforma.
    *   *Critério:* Cria schema DB, user admin inicial e settings básicos.
*   **US-1.2:** Como Admin do Tenant, quero convidar utilizadores e atribuir roles (Gestor, Vendedor, Engenheiro).
    *   *Critério:* Email de convite, RBAC funcional.

**Épico:** `CORE-02` — Estrutura de Projetos
*   **US-1.3:** Como Gestor, quero criar um Projeto e definir a sua localização geoespacial.
    *   *Critério:* Mapa interativo, polígono do terreno.
*   **US-1.4:** Como Gestor, quero definir Edifícios, Blocos e Pisos dentro do Projeto.
    *   *Critério:* Hierarquia visual clara.

### 🏠 Módulo 2: Inventário Imobiliário (Release 1)
**Épico:** `INV-01` — Gestão de Unidades
*   **US-2.1:** Como Gestor, quero criar unidades (T1, T2, Lojas) em lote ou individualmente.
    *   *Critério:* Importação via CSV/Excel, geração automática de códigos.
*   **US-2.2:** Como Gestor, quero definir preços e estados (Disponível, Reservado, Vendido).
    *   *Critério:* Histórico de alterações de preço guardado.
*   **US-2.3:** Como Gestor, quero anexar plantas e renders a cada unidade.
    *   *Critério:* Upload S3, preview no browser.

### 🤝 Módulo 3: Integração imo.cv (Release 2)
**Épico:** `INT-01` — Publicação de Listagens
*   **US-3.1:** Como Comercial, quero publicar uma unidade no imo.cv com um clique.
    *   *Critério:* Validação de campos obrigatórios, envio API, retorno de `listing_id`.
*   **US-3.2:** Como Sistema, quero atualizar o estado no imo.cv quando a unidade for reservada no ERP.
    *   *Critério:* Webhook ou Job agendado, latência < 5 min.

**Épico:** `INT-02` — Captura de Leads
*   **US-3.3:** Como Sistema, quero receber leads do imo.cv e criar registo automático no CRM.
    *   *Critério:* Lead associado à unidade de interesse, notificação ao vendedor.
*   **US-3.4:** Como Vendedor, quero ver a origem do lead (imo.cv, Walk-in, Telefone).
    *   *Critério:* Filtros no dashboard de leads.

### 💰 Módulo 4: Financeiro & Contratos (Release 3)
**Épico:** `FIN-01` — Contratos e Pagamentos
*   **US-4.1:** Como Comercial, quero gerar um Contrato de Reserva baseado num modelo pré-aprovado.
    *   *Critério:* PDF gerado, campos preenchidos automaticamente.
*   **US-4.2:** Como Financeiro, quero gerar um Plano de Pagamentos (ex: 10% sinal + 90% escritura).
    *   *Critério:* Geração de prestações com datas e valores.
*   **US-4.3:** Como Financeiro, quero registar um pagamento recebido e reconciliar com a fatura.
    *   *Critério:* Baixa automática da prestação, envio de recibo.

### 👷 Módulo 5: Obra Mobile Offline (Release 3)
**Épico:** `OBRA-01` — Diário e Tarefas
*   **US-5.1:** Como Engenheiro, quero registar o Diário de Obra sem internet.
    *   *Critério:* Dados guardados em SQLite, sync automático quando houver rede.
*   **US-5.2:** Como Engenheiro, quero tirar fotos da obra e anexar ao registo diário.
    *   *Critério:* Compressão de imagem local, upload em background.
*   **US-5.3:** Como Gestor, quero ver o % de progresso físico da WBS no dashboard.
    *   *Critério:* Cálculo baseado nas tarefas concluídas.

### 📢 Módulo 6: Comunicação (WhatsApp) (Release 3)
**Épico:** `COM-01` — Hub de Comunicação
*   **US-6.1:** Como Sistema, quero enviar um WhatsApp automático quando uma prestação estiver vencida.
    *   *Critério:* Template aprovado, registo de envio no histórico.
*   **US-6.2:** Como Vendedor, quero enviar propostas comerciais por WhatsApp diretamente do CRM.
    *   *Critério:* Botão "Enviar WhatsApp", link para PDF.

---

## 5. Requisitos Não-Funcionais (NFRs)

Estes requisitos são **críticos** e devem ser validados em cada Sprint.

| ID | Categoria | Requisito | Critério de Aceite |
| :--- | :--- | :--- | :--- |
| **NFR-01** | **Offline** | O Mobile App deve funcionar sem conectividade. | Todas as ações de escrita (logs, fotos) devem ser guardadas localmente e sincronizadas quando a rede voltar. |
| **NFR-02** | **Tenancy** | Isolamento total de dados entre empresas. | Uma query de um Tenant NUNCA pode retornar dados de outro Tenant. Testes automatizados de isolamento. |
| **NFR-03** | **Performance** | Carregamento de páginas < 2 segundos. | Otimização de queries, uso de Redis para cache de sessões e dados frequentes. |
| **NFR-04** | **Segurança** | Dados sensíveis encriptados. | Passwords (bcrypt), Dados de clientes (AES-256 no DB), HTTPS obrigatório. |
| **NFR-05** | **Audit** | Rastreabilidade de todas as ações. | Tabela `audit_logs` guarda Quem, O Quê, Quando e IP de todas as escritas críticas. |
| **NFR-06** | **Sync** | Sincronização imo.cv confiável. | Mecanismo de retry exponencial em caso de falha da API externa. Dashboard de erros de sync. |

---

## 6. Plano de Integração

### 6.1. imo.cv (Prioridade Alta)
*   **Método:** API REST + Webhooks.
*   **Direção:** Bidirecional.
    *   *Saída:* Unidades, Preços, Fotos, Estado.
    *   *Entrada:* Leads, Métricas de Visualização, Estado da Reserva.
*   **Segurança:** OAuth2 ou API Key rotativa.

### 6.2. WhatsApp Business API (Prioridade Alta)
*   **Provider:** Meta Cloud API ou Partner (ex: Twilio/Take Blip).
*   **Uso:** Notificações transacionais (pagamentos, obra) e Comunicação Comercial.
*   **Custo:** Por conversa. Deve ser previsto no modelo de negócio.

### 6.3. Bancos Locais (Prioridade Média)
*   **Fase 1:** Importação de extractos (CSV/OFX) e reconciliação manual.
*   **Fase 2:** Integração direta com APIs bancárias (se disponíveis em CV) ou MBE.

---

## 7. Roadmap e Estimativa de Recursos

### 7.1. Cronograma (36 Semanas)

```text
Mês 1-3  : [ RELEASE 1 ] Core, Tenancy, Projetos, Unidades
Mês 4-5  : [ RELEASE 2 ] Integração imo.cv, CRM, Leads
Mês 6-8  : [ RELEASE 3 ] Financeiro, Contratos, Obra Mobile, WhatsApp
Mês 9    : [ UAT & PILOTO ] Testes com 3 promotoras parceiras
Mês 10   : [ LANÇAMENTO ] Go-to-market oficial
```

### 7.2. Equipa Necessária (Squad Dedicada)
| Role | Qty | Alocação |
| :--- | :--- | :--- |
| **Tech Lead / Arquiteto** | 1 | 100% (Arquitetura, Code Review, Core) |
| **Backend Dev (Django)** | 2 | 100% (APIs, Lógica de Negócio, DB) |
| **Frontend Dev (React)** | 1 | 100% (Web App, Dashboards) |
| **Mobile Dev (React Native)** | 1 | 100% (App Obra, Offline Sync) |
| **DevOps / QA** | 1 | 50% (CI/CD, Infra, Testes) |
| **Product Owner** | 1 | 50% (Backlog, Validação com Mercado) |
| **UI/UX Designer** | 1 | 30% (Protótipos, Design System) |

### 7.3. Estimativa de Custo de Infra (Mensal - Fase Inicial)
*   **App Hosting (ex: DigitalOcean/AWS):** $200 - $400
*   **Database Gerido:** $150 - $300
*   **Storage (S3):** $50 (variável com uso)
*   **Serviços Externos (WhatsApp, Email, Maps):** $200 - $500
*   **Total Estimado:** **$600 - $1,500 / mês** (Escalável com receita).

---

## 8. Critérios de Sucesso (KPIs)

Para considerar o MVP um sucesso após 6 meses de operação:

1.  **Adoção:** 5 Promotoras ativas a usar a plataforma diariamente.
2.  **Dados:** 50+ Projetos e 1000+ Unidades geridas no sistema.
3.  **Integração:** 95% de sucesso nas sincronizações com o `imo.cv`.
4.  **Operação:** 80% dos registos de obra feitos via Mobile App (e não papel).
5.  **Financeiro:** 100% das reservas e contratos emitidos através da plataforma.

---

## 9. Próximos Passos Imediatos

1.  **Validação Técnica:** Reunião com a equipa de engenharia para validar a stack e o modelo de tenancy (`django-tenants`).
2.  **Configuração de Ambiente:** Criar repositórios, pipelines CI/CD e ambientes de Dev/Staging.
3.  **Setup do Jira:** Importar os Épicos e User Stories deste Blueprint para o backlog.
4.  **Kick-off:** Iniciar Sprint 0 (Arquitetura detalhada e Design System).

---

**Documento Aprovado Para:** Planeamento de Sprint 0
**Próxima Revisão:** Após Release 1 (Fundação)
**Resumo da Estratégia Validada:**

1.  **ImoOS + imo.cv:** O modelo de ecossistema (marketplace + sistema operativo) é a vantagem competitiva central.
2.  **Arquitetura Adaptada:** Monólito modular inicial, com evolução para microserviços apenas onde necessário. Prioridade ao modo offline-first para a app de obra.
3.  **Roadmap Faseado:** MVP focado em multitenancy, projetos, unidades e integração imo.cv. Expansão gradual para financeiro, construção, BIM e investidores.
4.  **Tecnologia Acertada:** Django/Next.js/PostgreSQL como base sólida, com camadas de integração (Kafka/RabbitMQ) e observabilidade.

**Próximos Passos Operacionais (Sugestão):**

Para transformar esta visão em realidade, recomendo as seguintes ações imediatas:

1.  **Criação do Blueprint de Arquitetura Detalhado:**
    *   Diagramas C4 (Contexto, Contentores, Componentes, Código).
    *   Definição dos contratos de API entre os módulos principais.
    *   Especificação do modelo de dados físico para o MVP (30-40 tabelas).

2.  **Backlog Estruturado (Formato Jira/ClickUp):**
    *   Épicos por trimestre (ex: Fundação, Integração imo.cv, Financeiro, Construção).
    *   User stories detalhadas com critérios de aceitação.
    *   Priorização MoSCoW (Must have, Should have, Could have, Won't have).

3.  **Apresentação Comercial e Business Case:**
    *   Pitch para investidores e potenciais clientes piloto em Cabo Verde.
    *   Projeções financeiras (ARR, CAC, LTV) com base no modelo de monetização definido.

4.  **Setup Inicial de Desenvolvimento:**
    *   Repositório Git com boilerplate (Django + Next.js + Docker).
    *   Configuração de CI/CD (GitHub Actions) e ambiente de staging.
    *   Escolha definitiva entre React Native e Flutter para mobile (recomendo React Native pela partilha de código com Next.js).


Abaixo, apresento o **Addendum Técnico e Operacional v1.1**. Este documento não substitui o Blueprint anterior, mas **integra-se nele** para colmatar as lacunas identificadas na tua análise.

---

# 📘 Addendum Técnico e Operacional — ImoOS (v1.1)
### **Objetivo:** Refinar o Blueprint com detalhes de execução, conformidade e escalabilidade.

---

## 1. Modelo de Dados Detalhado (Core Crítico)

Para garantir rastreabilidade e integridade, utilizaremos a biblioteca `django-simple-history` para todas as tabelas transacionais. Abaixo, o detalhe das entidades mais críticas.

### 1.1. Tabela `units` (Inventário)
| Campo | Tipo | Nullable | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | UUID | No | Chave primária. |
| `tenant_id` | FK | No | Isolamento lógico. |
| `project_id` | FK | No | Ligação ao empreendimento. |
| `code` | String | No | Código único (ex: BLK-A-P3-DT). |
| `type` | FK | No | Tipologia (T1, T2, Loja). |
| `area_bruta` | Decimal | No | Área em m². |
| `price_base` | Decimal | No | Preço base na moeda do tenant. |
| `status` | Enum | No | `AVAILABLE`, `RESERVED`, `SOLD`, `MAINTENANCE`. |
| `bim_guid` | String | Yes | Ligação ao elemento IFC (Fase 2). |
| `created_at` | DateTime | No | Auditoria. |
| `updated_at` | DateTime | No | Auditoria. |
| `history` | Relation | - | Tabela histórica automática (preço, status). |

### 1.2. Tabela `reservations` (Concorrência Crítica)
| Campo | Tipo | Nullable | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | UUID | No | Chave primária. |
| `unit_id` | FK | No | Unidade reservada. |
| `buyer_id` | FK | No | Cliente interessado. |
| `agent_id` | FK | No | Vendedor responsável. |
| `expires_at` | DateTime | No | Validade da reserva (ex: 48h). |
| `status` | Enum | No | `PENDING`, `CONFIRMED`, `EXPIRED`, `CANCELLED`. |
| `lock_version` | Integer | No | Para otimistic locking se necessário. |

**Estratégia de Concorrência (Double Booking Prevention):**
Para evitar que dois vendedores reservem a mesma unidade simultaneamente:
1.  **Database Level:** Uso de `SELECT ... FOR UPDATE` na transação de criação da reserva.
2.  **Logic Level:** Verificação de `status = AVAILABLE` e `expires_at < NOW()` antes de inserir.
3.  **Frontend Level:** Polling de status da unidade a cada 30s no dashboard de vendas.

---

## 2. Evolução da Arquitetura (Monólito → Serviços)

O Monólito Modular é o início, mas precisamos de gatilhos claros para extrair serviços.

| Módulo | Gatilho para Extração | Tecnologia Alvo |
| :--- | :--- | :--- |
| **Notification Service** | Volume > 10k mensagens/dia ou necessidade de canais múltiplos complexos. | Python/FastAPI + Redis Queue |
| **BIM Engine** | Processamento de IFC causar latência > 2s no core ou consumo alto de CPU. | Go ou Python (isolado em container pesado) |
| **Analytics/Reporting** | Queries analíticas degradarem performance transacional (> 5s). | Read Replica + ClickHouse/BigQuery |
| **Integration Service** | Necessidade de conectar a 5+ marketplaces com protocolos diferentes. | Node.js ou Python (Event-Driven) |

**Comunicação Futura:**
*   Inicialmente: Chamadas de função internas (Python imports).
*   Futuro: **Event Bus (RabbitMQ/Kafka)**. O core publica eventos (`unit.reserved`), e os serviços subscrevem.

---

## 3. Segurança e Conformidade (Cabo Verde)

### 3.1. Lei de Proteção de Dados (Lei n.º 133/V/2019)
O sistema deve garantir nativamente:
*   **Consentimento:** Campo `consent_marketing` e `consent_data_processing` obrigatório no registo de leads (`buyers`).
*   **Direito ao Esquecimento:** Comando de gestão (`mgmt command`) para anonimizar dados de um titular mediante solicitação, mantendo apenas dados fiscais obrigatórios por lei.
*   **Portabilidade:** Exportação de dados do cliente em formato JSON/CSV estruturado.
*   **Registo de Atividades:** Tabela `audit_logs` deve registar *quem* acedeu a dados pessoais e *quando*.

### 3.2. Controlo de Acesso (RBAC + ABAC)
*   **RBAC (Roles):** Admin, Gestor, Vendedor, Engenheiro, Investidor.
*   **ABAC (Attribute-Based):** Um vendedor só vê leads atribuídos a si (`owner_id = user.id`). Um gestor vê todos do seu tenant.
*   **Implementação:** `django-guardian` para permissões a nível de objeto (ex: este utilizador pode editar *esta* unidade específica).

### 3.3. Proteção de API
*   **Rate Limiting:** `django-ratelimit` para prevenir brute-force (ex: 100 req/hora por IP para endpoints públicos).
*   **Input Validation:** Validação estrita de tipos e tamanhos nos Serializers (DRF) para prevenir SQL Injection e XSS.

---

## 4. Especificação de Integração (imo.cv)

### 4.1. Payload de Publicação (Exemplo JSON)
```json
POST /api/v1/marketplace/sync/listings
{
  "tenant_id": "uuid-tenant",
  "action": "CREATEOrUpdate",
  "listings": [
    {
      "internal_unit_id": "uuid-unit-123",
      "external_ref": "imo-cv-999",
      "title": "T2 Luxo com Vista Mar",
      "price": 150000,
      "currency": "EUR",
      "status": "AVAILABLE",
      "features": ["varanda", "parking", "piscina"],
      "media_urls": ["s3://.../img1.jpg"],
      "location": { "lat": 14.9177, "lon": -23.5170 }
    }
  ]
}
```

### 4.2. Gestão de Erros de Sync
*   **Retry Policy:** Exponential Backoff (1min, 5min, 30min, 2h).
*   **Dead Letter Queue:** Após 5 falhas, o registo move-se para tabela `marketplace_errors` e alerta o admin por email.
*   **Fallback:** Interface manual no backend para forçar publicação se a API falhar persistentemente.

---

## 5. Estratégia de Testes e Qualidade

| Tipo de Teste | Ferramenta | Cobertura Alvo | Frequência |
| :--- | :--- | :--- | :--- |
| **Unitários** | `pytest` + `factory_boy` | 80% da lógica de negócio (Models, Services) | Em cada Commit |
| **Integração** | `pytest-django` | 100% das APIs críticas (Reserva, Pagamento) | Em cada Commit |
| **E2E (Web)** | `Playwright` | Fluxos críticos (Login → Criar Projeto → Publicar) | Nightly Build |
| **Mobile Sync** | `Detox` (React Native) | Cenários Offline/Online (Modo Avião) | Semanal |
| **Carga** | `k6` ou `Locust` | Endpoint de Listagem e Dashboard | Antes de Release |
| **Segurança** | `OWASP ZAP` | Scan automático de vulnerabilidades | Mensal |

**Teste Específico de Tenancy:**
*   Script automatizado que tenta aceder a dados do Tenant A com credenciais do Tenant B. Se retornar dados, o build falha imediatamente.

---

## 6. Matriz de Riscos (Top 5)

| Risco | Impacto | Probabilidade | Mitigação |
| :--- | :--- | :--- | :--- |
| **Baixa adoção do App de Obra** | Alto | Média | UX simplificada (botões grandes), formação presencial no estaleiro, incentivos por uso. |
| **Instabilidade da API imo.cv** | Alto | Média | Fila de retry robusta, modo de publicação manual de emergência, monitorização de saúde da API. |
| **Vazamento de Dados entre Tenants** | Crítico | Baixa | Testes automatizados de isolamento, revisão de código focada em `tenant_id`, uso de `django-tenants`. |
| **Conflito de Reservas (Double Booking)** | Alto | Baixa | Locking a nível de DB (`FOR UPDATE`), validação frontend em tempo real. |
| **Conectividade na Obra (Offline)** | Médio | Alta | Arquitetura Offline-First real (SQLite local), sync assíncrono, compressão de imagens. |

---

## 7. Plano de Onboarding e Gestão de Mudança

Para garantir que as 3 promotoras piloto adotem a ferramenta:

1.  **Seleção das Piloto:**
    *   Critério: Estar a iniciar um projeto novo (não tentar migrar obra a meio).
    *   Perfil: Direção aberta à digitalização.
2.  **Kick-off Presencial:**
    *   Workshop de 1 dia com a direção e equipas chave (Comercial + Obra).
    *   Configuração inicial feita pela equipa ImoOS (não deixar o cliente configurar sozinho).
3.  **Materiais de Suporte:**
    *   Vídeos curtos (2-3 min) por funcionalidade (ex: "Como registar uma visita", "Como validar uma medição").
    *   Manual PDF simplificado.
4.  **Suporte Dedicado (Concierge):**
    *   Canal WhatsApp direto com a equipa de suporte nas primeiras 4 semanas.
    *   Reunião semanal de feedback para ajustar bugs rápidos.
5.  **Migração de Dados:**
    *   Não migrar histórico antigo complexo.
    *   Importar apenas: Lista de Unidades Atuais, Leads Ativos, Contactos de Clientes. (Via CSV template).

---

## 8. Internacionalização (i18n) e Localização (l10n)

Preparar para Angola e Senegal desde o código, mesmo que o lançamento seja em CV.

*   **Backend:** `django-modeltranslation` para campos de conteúdo (descrições de projetos).
*   **Frontend:** `react-i18next` para toda a interface.
*   **Formatos:** Usar biblioteca `babel` ou nativa do JS para formatar moeda e data conforme a locale do tenant (`pt-CV`, `pt-AO`, `fr-SN`).
*   **Contratos:** Sistema de templates onde as cláusulas legais são carregadas conforme o `country_config` do tenant.

---

## 9. Conclusão do Addendum

Com a integração destes pontos, o **ImoOS** deixa de ser apenas um plano de desenvolvimento e torna-se um **plano de engenharia de produto robusto**.

**Próximos Passos Imediatos (Semana 1):**
1.  Configurar repositório com `django-tenants` e `django-simple-history`.
2.  Criar pipeline CI/CD com testes de isolamento de tenants.
3.  Desenhar protótipos de alta fidelidade (Figma) focados no "Modo Obra Offline".
4.  Reunião técnica com a equipa do `imo.cv` para validar especificação da API.

Este documento deve ser anexado ao Blueprint original e tratado como **referência obrigatória** para a equipa de desenvolvimento.