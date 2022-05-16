from dataclasses import fields
from rest_framework.serializers import ModelSerializer
# serializers are used to convert our python objects into JSON. So that we can use
# it in our api
from base.models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
