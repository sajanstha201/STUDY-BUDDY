
from . import views
from django.urls import path
urlpatterns = [
    path('', views.getRoutes),
    path('rooms/', views.getRooms),
    path('rooms/<int:room_id>/', views.getRoom),
]
