---
name: coding-standards
description: Enforce ImoOS coding conventions, PEP8, TypeScript strict mode, and commit message format
argument-hint: [language] [file-type]
allowed-tools: Read, Write
---

# ImoOS Coding Standards

## Python/Django
- Follow PEP8 with Black formatting (line length: 120)
- Type hints required for all function signatures
- Docstrings: Google style for public APIs
- Model methods: keep under 50 lines, extract helpers if longer
- Views: use DRF ViewSets, never function-based for APIs

## TypeScript/Next.js
- Strict mode enabled: no implicit any, strict null checks
- Prefer functional components + hooks over class components
- Use TypeScript interfaces for API responses, not 'any'
- Tailwind classes: use clsx for conditional styling

## Commit Messages
Format: `<type>(<scope>): <subject>`
Types: feat, fix, docs, style, refactor, test, chore
Scope: module name (tenants, projects, crm, etc.)
Example: `feat(inventory): add bulk unit import via CSV`

## Naming Conventions
- Python: snake_case for variables/functions, PascalCase for classes
- TypeScript: camelCase for variables/functions, PascalCase for components
- Database: snake_case for tables/columns
- URLs: kebab-case for slugs
