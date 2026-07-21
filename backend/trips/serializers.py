from rest_framework import serializers
from .models import Trip


class TripRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    cycle_hours_used = serializers.FloatField(min_value=0, max_value=70)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id", "current_location", "pickup_location", "dropoff_location",
            "cycle_hours_used", "result", "created_at",
        ]
