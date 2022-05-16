from django.urls import path
from . import views
app_name = 'base'
urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.loginUser, name='login'),
    path('register/', views.registerUser, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path("room/<int:room_id>", views.room, name='room'),
    path("create-form", views.create_form, name='create-form'),
    path("update-form/<int:room_id>", views.updateRoom, name='update-form'),
    path("delete-form/<int:room_id>", views.deleteRoom, name='delete-room'),
    path('delete-message/<int:message_id>', views.deleteMessage,
         name='delete-message'),
    path('user-profile/<int:user_id>', views.userProfile, name='user-profile'),
    path('edit-user', views.updateUser, name='edit-user'),
    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),
    
]
