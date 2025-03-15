from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class APILanguageMiddleware(MiddlewareMixin):
    """
    Middleware that sets the language for an API request based on the
    Accept-Language header or a query parameter.
    """
    
    def process_request(self, request):
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_language:
            languages = [lang.split(';')[0].strip() for lang in accept_language.split(',')]
            if languages:
                translation.activate(languages[0])
                request.LANGUAGE_CODE = translation.get_language()
                return
                
        lang_code = request.GET.get('lang')
        if lang_code:
            translation.activate(lang_code)
            request.LANGUAGE_CODE = translation.get_language()
            return 