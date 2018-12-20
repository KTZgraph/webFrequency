from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
import json

from api.frequency import FrequencyKeywords, FrequencyKeywordException

class Frequency(View):
    """Returns frequency of keyword from webPage"""
    template_name = 'api/frequency.html'
    
    def get(self, request):
        """Return html file with input for user GET requests"""
        return render(request, self.template_name, {"info": "Podaj adres url strony dla, której chcesz poznać częstotliwość słów kluczowych."})

    def post(self, request):
        """Return keywords frequency, for webpage from user url"""
        if not request.body:
            return JsonResponse({"message": "Empty request.body"})
        response = json.loads(request.body)

        if "userUrl" not in response:
            return JsonResponse({"errorMessage" : "Brak wymaganego parametu: 'userUrl'."})
        userUrl = response["userUrl"]

        try:
            frequency_obj = FrequencyKeywords(userUrl)
        except FrequencyKeywordException as exception:
            return JsonResponse({"errorMessage": "Błąd: {e}".format(e=exception)})

        errorMessage = ''
        if not frequency_obj.frequency:
            errorMessage += "Brak słów kluczowych dla strony o podanym adresie. "
        if frequency_obj.status_code == 404:
            errorMessage += "Strona zwróciła kod 404 http. "

        return JsonResponse({
            "keywords" :frequency_obj.keywords ,
            "frequency": frequency_obj.frequency,
            "statusCode" : frequency_obj.status_code,
            "errorMessage" :errorMessage
            })
