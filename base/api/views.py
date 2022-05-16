from pickle import GET
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    # safe=False basically means that the argument that is passed to
    # JsonResponse doesn't have to be a dictionary
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    # many=True is because we are passing QuerySet
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, room_id):
    room = Room.objects.get(pk=room_id)
    # many=False is because we are passing one object and expecting one Json object
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
