class TracebackMiddleware:
    def process_request(self, request):
        print "I have a request, Yeah!"

    def process_exception(self, request, exception):
        print "I have an exeception"
        print exception
