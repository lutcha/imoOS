---
name: i18n-l10n
description: Internationalization and localization for ImoOS — pt-PT, pt-AO, fr-SN. Auto-load when adding user-facing strings, date/number formatting, or multi-language content.
argument-hint: [language] [module]
allowed-tools: Read, Write
---

# ImoOS Internationalisation Patterns

## Backend (Django)
```python
# Model field translations via django-modeltranslation
from modeltranslation.translator import register, TranslationOptions
from apps.projects.models import Project

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    # Creates: name_pt_pt, name_pt_ao, name_fr_sn columns

# Usage in views: request.LANGUAGE_CODE sets active translation
```

## Frontend (Next.js)
```typescript
// i18n/pt-PT/projects.json
{
  "create_project": "Criar Projecto",
  "project_status": {
    "PLANNING": "Em Planeamento",
    "CONSTRUCTION": "Em Construção"
  }
}

// Component
import { useTranslation } from 'next-i18next';
const { t } = useTranslation('projects');
<Button>{t('create_project')}</Button>
```

## Date & Number Formatting
```python
# Backend
from django.utils.formats import date_format, number_format
date_format(obj.created_at, 'DATE_FORMAT', use_l10n=True)  # 11/03/2026
number_format(price, decimal_pos=2, use_l10n=True)          # 15.000,00

# Frontend
import { format } from 'date-fns';
import { pt } from 'date-fns/locale';
format(new Date(), 'dd/MM/yyyy', { locale: pt });  // 11/03/2026
```

## Locale Priority Chain
1. User profile language preference
2. Tenant default language (TenantSettings.language)
3. Accept-Language header
4. Fallback: `pt-PT`

## Key Rules
- All user-facing strings must go through `{% trans %}` / `t()` — never hardcode
- Extract strings weekly: `python manage.py makemessages -a`
- Date format always DD/MM/YYYY (never MM/DD/YYYY)
- Prepare `fr-SN` namespace from day 1 even if unused — avoid rewrite later
