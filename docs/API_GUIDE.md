# ImoOS API Guide

## Base URL

```
https://imos-staging-jiow3.ondigitalocean.app/api/v1/
```

## Authentication

Most endpoints require authentication via JWT token.

### Login

```bash
POST /api/v1/users/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "MANAGER"
  }
}
```

### Using Tokens

Include the access token in all requests:

```bash
GET /api/v1/crm/leads/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
X-Tenant-Schema: demo_promotora
```

### Refresh Token

```bash
POST /api/v1/users/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Multi-Tenancy

All tenant-scoped endpoints require the `X-Tenant-Schema` header:

```bash
X-Tenant-Schema: demo_promotora
```

Available schemas:
- `public` - System administration
- `demo_promotora` - Demo tenant

## Core Endpoints

### CRM (Leads)

```bash
# List leads
GET /api/v1/crm/leads/

# Create lead
POST /api/v1/crm/leads/
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao@email.cv",
  "phone": "+2389991234",
  "status": "NEW"
}

# Update lead
PATCH /api/v1/crm/leads/{id}/
{
  "status": "QUALIFIED"
}

# Delete lead
DELETE /api/v1/crm/leads/{id}/
```

### Projects & Units

```bash
# List projects
GET /api/v1/projects/projects/

# List units
GET /api/v1/projects/units/

# Get available units
GET /api/v1/projects/units/?status=AVAILABLE
```

### Contracts

```bash
# List contracts
GET /api/v1/contracts/contracts/

# Create contract
POST /api/v1/contracts/contracts/
{
  "lead": "lead-uuid",
  "unit": "unit-uuid",
  "sale_price": "5000000.00",
  "down_payment_percent": 20,
  "installment_months": 120
}

# Get contract PDF
GET /api/v1/contracts/contracts/{id}/pdf/
```

### Construction

```bash
# List construction projects
GET /api/v1/construction/projects/

# Get project phases
GET /api/v1/construction/phases/?project={project_id}

# Get project tasks
GET /api/v1/construction/tasks/?project={project_id}

# Update task progress
PATCH /api/v1/construction/tasks/{id}/
{
  "progress_pct": 75,
  "status": "IN_PROGRESS"
}

# Get Gantt data
GET /api/v1/construction/gantt/?project={project_id}

# Create daily report
POST /api/v1/construction/daily-reports/
{
  "project": "project-uuid",
  "date": "2026-04-06",
  "progress_pct": 45,
  "summary": "Trabalhos de fundação",
  "description": "Concretagem de blocos concluída"
}
```

### Budget

```bash
# List budgets
GET /api/v1/budget/budgets/

# Get budget items
GET /api/v1/budget/budgets/{id}/items/

# Create budget item
POST /api/v1/budget/items/
{
  "budget": "budget-uuid",
  "category": "MATERIALS",
  "item_name": "Cimento",
  "unit": "KG",
  "quantity": 1000,
  "unit_price": "150.00"
}

# Search prices
GET /api/v1/budget/prices/search/?q=cimento

# Export budget Excel
GET /api/v1/budget/budgets/{id}/export/?format=excel
```

### Dashboard

```bash
# Get dashboard stats
GET /api/v1/dashboard/stats/

# Get sales metrics
GET /api/v1/dashboard/metrics/sales/

# Get construction metrics
GET /api/v1/dashboard/metrics/construction/
```

### WhatsApp

```bash
# Send message
POST /api/v1/integrations/whatsapp/send/
{
  "to": "+2389991234",
  "message": "Olá! A obra avançou 10% esta semana."
}

# Send template
POST /api/v1/integrations/whatsapp/send-template/
{
  "to": "+2389991234",
  "template_name": "payment_reminder",
  "language": "pt",
  "components": [
    {
      "type": "body",
      "parameters": [
        {"type": "text", "text": "João"},
        {"type": "text", "text": "15.000 CVE"}
      ]
    }
  ]
}

# Get message templates
GET /api/v1/integrations/whatsapp/templates/
```

### Workflows

```bash
# Trigger sales workflow
POST /api/v1/workflows/sales/create_reservation/
{
  "lead_id": "lead-uuid",
  "unit_id": "unit-uuid"
}

# Get workflow status
GET /api/v1/workflows/instances/{id}/status/
```

## SuperAdmin Endpoints

### Tenant Management

```bash
# List all tenants (public schema)
GET /api/v1/tenants/
Authorization: Bearer {superadmin_token}
X-Tenant-Schema: public

# Create tenant
POST /api/v1/tenants/
{
  "schema_name": "new_promotora",
  "name": "New Promotora",
  "plan": "pro"
}

# Impersonate tenant
POST /api/v1/tenants/{id}/impersonate/
```

### Registration

```bash
# Register new tenant
POST /api/v1/register/
{
  "company_name": "Minha Promotora",
  "admin_email": "admin@empresa.cv",
  "admin_first_name": "João",
  "admin_last_name": "Silva",
  "phone": "+2389991234"
}

# Verify registration
POST /api/v1/register/verify/
{
  "token": "verification-token"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Validation failed",
  "details": {
    "email": ["This field is required."]
  }
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Invalid setup token"
}
```

### 404 Not Found

```json
{
  "error": "Lead not found"
}
```

## Rate Limits

- Authenticated: 1000 requests/hour
- Anonymous: 100 requests/hour

## Pagination

List endpoints return paginated results:

```json
{
  "count": 100,
  "next": "https://api.example.com/api/v1/crm/leads/?page=2",
  "previous": null,
  "results": [...]
}
```

Query parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

## Filtering

Most list endpoints support filtering:

```bash
# Filter by status
GET /api/v1/crm/leads/?status=QUALIFIED

# Search
GET /api/v1/crm/leads/?search=joão

# Ordering
GET /api/v1/crm/leads/?ordering=-created_at
```

## Webhooks

### WhatsApp Webhook

```
POST /api/v1/integrations/whatsapp/webhook/
```

Configure in Twilio Console to receive incoming messages.

## SDK & Clients

### JavaScript/TypeScript

```typescript
import { ImoOSClient } from '@imoos/sdk';

const client = new ImoOSClient({
  baseURL: 'https://imos-staging-jiow3.ondigitalocean.app/api/v1/',
  tenantSchema: 'demo_promotora'
});

await client.auth.login('user@example.com', 'password');
const leads = await client.crm.listLeads();
```

## Testing with cURL

```bash
# Set variables
TOKEN=$(curl -s -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.cv","password":"Demo2026!"}' \
  | jq -r '.access')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
     -H "X-Tenant-Schema: demo_promotora" \
     https://imos-staging-jiow3.ondigitalocean.app/api/v1/crm/leads/
```
