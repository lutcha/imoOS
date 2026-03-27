# Sprint 5 — Cleanup: `apps/units` Legacy

## Contexto

`apps/units/` contém modelos duplicados de `apps/inventory/` — provavelmente uma versão anterior
que ficou esquecida. Antes de expandir o projecto, este conflito precisa de ser resolvido
para evitar imports errados, migrations duplicadas e confusão futura.

## Pré-requisitos — Ler TUDO antes de tocar em qualquer ficheiro

```bash
# Verificar o que existe em apps/units
find apps/units -type f -name "*.py" | xargs head -5

# Verificar se apps/units está registado em INSTALLED_APPS
grep -r "apps.units\|'units'" config/settings/ --include="*.py"

# Verificar se há imports de apps.units em qualquer lugar do projecto
grep -r "from apps.units\|import apps.units" apps/ --include="*.py"

# Verificar migrations de apps/units
find apps/units -name "*.py" -path "*/migrations/*"

# Verificar se apps/inventory já tem todos os modelos equivalentes
grep "^class " apps/units/models.py
grep "^class " apps/inventory/models.py
```

## Skills a carregar

```
@.claude/skills/01-multi-tenant/django-tenants-migrations/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `django-tenants-specialist` | Análise de impacto das migrations antes de qualquer remoção |
| `migration-orchestrator` | Planear a remoção segura de apps/units se for duplicado |

---

## Tarefa 1 — Análise (OBRIGATÓRIO antes de qualquer edição)

Prompt para `django-tenants-specialist`:
> "Analisa `apps/units/models.py` e `apps/inventory/models.py` em ImoOS. São duplicados? Há diferenças de schema? `apps/units` está em `TENANT_APPS`? Há migrations aplicadas? Há FKs de outras apps apontando para `apps.units`? Dá um relatório ✅/⚠️/❌ antes de qualquer remoção."

### Resultado esperado da análise
Se `apps/units` for duplicado limpo (sem migrations aplicadas, sem FK externas):
→ **Acção:** remover o directório, verificar INSTALLED_APPS, correr `migrate_schemas`

Se `apps/units` tiver migrations aplicadas ou FK externas:
→ **Acção:** criar migration `RenameModel` ou `RunSQL` para migrar dados → `apps/inventory`
→ NÃO apagar sem migration de transição

---

## Tarefa 2 — Remover (apenas se análise confirmar segurança)

**Nunca executar sem o relatório da Tarefa 1.**

Prompt para `migration-orchestrator`:
> "Planeia a remoção segura de `apps/units` em ImoOS, dado que `apps/inventory` tem os modelos equivalentes. Cria migration de squash se necessário. Garante que `pytest tests/tenant_isolation/ -v` continua a passar após a remoção."

### Passos manuais seguros
```bash
# 1. Remover de INSTALLED_APPS em base.py / TENANT_APPS
# 2. Apagar apps/units/ (apenas se sem migrations aplicadas)
# 3. Correr migrations
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
# 4. Verificar que os testes passam
pytest tests/tenant_isolation/ -v
pytest apps/ -v --tb=short
```

---

## Verificação final

- [ ] `grep -r "apps.units" .` → zero resultados
- [ ] `python manage.py check` → sem erros
- [ ] `python manage.py migrate_schemas` → sem erros
- [ ] `pytest tests/tenant_isolation/ -v` → 100% passing
- [ ] `npm run build` → sem erros (nenhum import frontend afectado)
