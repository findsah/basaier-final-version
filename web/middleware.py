from django.conf import settings
from django.utils import translation
from django.http import HttpResponse


class ForceLangMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # def process_exception(self, request, exception):
    #     return HttpResponse("in exception")

    def process_request(self, request):
        request.LANG = getattr(settings, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)

        if request.LANGUAGE_CODE == "en":
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
        else:
            translation.activate('ar')
            request.LANGUAGE_CODE = 'ar'

    def process_response(self, request, response):
        """Let's handle old-style response processing here, as usual."""
        # Do something with response, possibly using request.
        return response

    def __call__(self, request):
        """Handle new-style middleware here."""
        response = self.process_request(request)
        if response is None:
            # If process_request returned None, we must call the next middleware or
            # the view. Note that here, we are sure that self.get_response is not
            # None because this method is executed only in new-style middlewares.
            response = self.get_response(request)

        response = self.process_response(request, response)
        return response