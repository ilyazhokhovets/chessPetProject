
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView


def home(request):

    return render(request, 'training/base.html')


from .logic import _delete_db
class MoveView(APIView):
    def post(self, request):
        _delete_db()

        return Response(request.data)

class ChangeTrainingView(APIView):
    def post(self, request):

        return Response(request.data)
