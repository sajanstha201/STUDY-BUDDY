
from ast import operator
from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from numpy import require
from pyparsing import Or
from requests import RequestException, session
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message, Room, Topic, User
from .forms import RoomForm, Message, UserForm, MyUserCreationForm


def loginUser(request):
    page = 'login'
    context = {'page': page}
    if request.user.is_authenticated:
        return redirect('base:home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            # message will help us to throw flash messages( It will
            # disappear after 1 refresh)
            messages.error(request, "User doesn't exist.")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # login() function will create a session in user browser
            # as well as in our database
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, "User or Password doesn't exist.")

    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    # logout(request) will delete the token so the user will not be in
    # session
    logout(request)
    return redirect('base:home')


def registerUser(request):
    form = MyUserCreationForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        # creates an instance of form with data populated by request.POST
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # before actually saving the object in the database. if we want to make
            # changes to our object. We can get the object using form.save(commit=False)
            # form.save(commit=False) will throw an object of model which we want to save
            # in our database.
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            context['username'] = user.username
            return redirect('base:home')
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    # using "Q" we can lookup using "|"(or)
    # operator
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q) |
                                Q(host__username__icontains=q))
    topics = Topic.objects.all()[0:5]
    # use count instead of len() to count the number of items in
    # querySet because count is much faster than len
    context = {
        'rooms': rooms,
        'topics': topics,
        'total_rooms': rooms.count(),
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)


def room(request, room_id):
    room = Room.objects.get(pk=room_id)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    if request.method == "POST":
        # objects.create() will create the object and save it to database in a single step
        # so instead of using .save() method after creating the instance we can use this
        print("Post called")
        print("message ", request.POST['body'])
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST['body']
        )
        print(message)
        room.participants.add(message.user)
        return redirect('base:room', room_id)
    return render(request, 'base/room.html', context)

# CREATE


@login_required(login_url='base:login')
# this login_required decorator add some functionality to our
# create_form view. Only the user who are currently in the session are
# allowed to create form . if the user is not in the session it will
# redirect to whatever url we pass with login_url
def create_form(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # this will create a form instance with data populated by request.POST
        # form = RoomForm(request.POST)

        topic_name = request.POST['topic']
        # this will bascially check if the object of this specific field is present or not
        # if it is present then create will be False and it will return
        # the present object. And if the object is not present then it will create
        # a new object and in this case create will be True.
        topic, create = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST['name'],
            description=request.POST['description']
        )
        return redirect('base:home')
    context = {
        'form': form,
        'topics': topics,
    }
    return render(request, 'base/room_form.html', context)

# UPDATE


@login_required(login_url='base:login')
def updateRoom(request, room_id):
    room = Room.objects.get(pk=room_id)
    # we are allowing only the host of the room to update/delete the
    # room and not any user who has logged in
    if request.user != room.host:
        return HttpResponse("You are not allowed here.")
    # here instance=room will create a form which will be filled
    # with all the fields of the object room
    form = RoomForm(instance=room)  # pre filling form
    context = {'form': form, 'room': room}
    if request.method == 'POST':
        # make sure to pass the object( instance=room) or else
        # instead of updating it will create a new object in db
        # form = RoomForm(request.POST, instance=room)
        topic_name = request.POST['topic']
        # this will bascially check if the object of this specific field is present or not
        # if it is present then create will be False and it will return
        # the present object. And if the object is not present then it will create
        # a new object and in this case create will be True.
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST['name']
        room.description = request.POST['description']
        room.save()
        return redirect('base:home')
    return render(request, 'base/room_form.html', context)

# DELETE


@login_required(login_url='base:login')
def deleteRoom(request, room_id):
    room = Room.objects.get(pk=room_id)
    # we are allowing only the host of the room to update/delete the
    # room and not any user who has logged in
    if request.user != room.host:
        return HttpResponse("You are not allowed here.")
    if request.method == "POST":
        room.delete()
        return redirect('base:home')
    return render(request, 'base/deleteItem.html', {"obj": room})


@login_required(login_url='base:login')
def deleteMessage(request, message_id):
    message = Message.objects.get(pk=message_id)
    # we are allowing only the host of the room to update/delete the
    # room and not any user who has logged in
    if request.user != message.user:
        return HttpResponse("You are not allowed here.")
    if request.method == "POST":
        message.delete()
        return redirect('base:home')
    return render(request, 'base/deleteItem.html', {"obj": message})


def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages
    }
    return render(request, 'base/user_profile.html', context)


@login_required(login_url='base:login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)  # pre filling
    context = {
        'form': form}
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        form.save()
        return redirect("base:user-profile", user.id)
    return render(request, 'base/edit-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
