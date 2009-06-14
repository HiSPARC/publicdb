class TracebackMiddleware:
    def process_exception(self, request, exception):
        print exception
