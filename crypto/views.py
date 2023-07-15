import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from parser.main import collect_data


class CryptoList(APIView):
    def get(self, request):
        # with open('parser/data.json') as file:
        #     data = json.load(file)
        data = collect_data()
        return Response(data)
