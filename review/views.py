from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewAPIViewSerializer
from account.models import User


class ReviewAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewAPIViewSerializer

    def post(self, request, *args, **kwargs):
        email = request.data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            user = User.objects.get(email=email)
            request.data['user'] = user.id

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
