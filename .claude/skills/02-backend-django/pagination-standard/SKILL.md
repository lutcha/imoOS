---
name: pagination-standard
description: ImoOS standard pagination class — PageNumberPagination, page_size=50, consistent response format. Auto-load when creating any list endpoint.
argument-hint: [page-size] [endpoint]
allowed-tools: Read, Write
---

# Standard Pagination — ImoOS

## Pagination Class
```python
# apps/core/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'current_page': {'type': 'integer'},
                'page_size': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            }
        }
```

## Settings Registration
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsPagination',
    'PAGE_SIZE': 50,
}
```

## Frontend Usage
```typescript
interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// React Query with pagination
const { data } = useQuery({
  queryKey: ['units', tenant, { page, pageSize, ...filters }],
  queryFn: () => api.get(`/units/?page=${page}&page_size=${pageSize}`),
});
```

## Key Rules
- Default page_size=50 — enough for tables without overloading mobile
- Max 200 per page — protect against accidental large requests
- Never return unpaginated lists for business models (can grow large)
- `total_pages` saves frontend from computing `Math.ceil(count / pageSize)`
