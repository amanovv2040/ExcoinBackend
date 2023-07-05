from rest_framework import serializers

from .models import Review


class ReviewAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['name', 'email', 'text', 'date_created']
