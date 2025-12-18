# middleware.py
class FixAuthorizationHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_AUTHORIZATION' in request.META and 'HTTP_AUTHORIZATION' not in request.META:
            request.META['HTTP_AUTHORIZATION'] = request.META['HTTP_X_AUTHORIZATION']
        return self.get_response(request)
