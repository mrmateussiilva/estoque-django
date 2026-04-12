from django.utils.deprecation import MiddlewareMixin


class CompanyContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.company = None
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            request.company = getattr(getattr(user, "profile", None), "company", None)
