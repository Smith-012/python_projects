from .models import RequestLog

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # avoid logging static + admin
        if not request.path.startswith("/admin/"):
            RequestLog.objects.create(
                path=request.path,
                method=request.method,
                status_code=response.status_code
            )

        return response
