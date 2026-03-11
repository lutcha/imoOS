from django_tenants.middleware import TenantMainMiddleware
from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse

class ImoOSTenantMiddleware(TenantMainMiddleware):
    """
    Middleware personalizado com validações adicionais de tenant.
    """
    
    def get_tenant(self, model, hostname, request):
        try:
            tenant = super().get_tenant(model, hostname, request)
            
            # Validações adicionais
            if not tenant.is_active:
                raise PermissionDenied("Tenant inativo")
            
            # Guardar tenant no request para acesso fácil
            request.tenant = tenant
            
            return tenant
        except model.DoesNotExist:
            # Let the super class handle it or raise custom error
            raise Http404("Tenant não encontrado")

    def process_request(self, request):
        try:
            return super().process_request(request)
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception as e:
            # Handle other tenant-related errors
            return super().process_request(request)
    
    def process_response(self, request, response):
        # Only expose internal tenant headers to authenticated requests
        user = getattr(request, 'user', None)
        if hasattr(request, 'tenant') and user is not None and user.is_authenticated:
            response['X-Tenant-Name'] = request.tenant.name
            response['X-Tenant-Schema'] = request.tenant.schema_name

        return response
