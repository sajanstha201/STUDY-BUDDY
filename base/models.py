from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import base64
from studybuddy import settings
# Create your models here.

# creating our own User Model that inherits all the functionality of
# inbuilt User Model


def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    print("img path ", image_file)
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
    return 'data:image/%s;base64,%s' % (format, encoded_string.decode())


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    # Note : Django ImageField in models relies on pillow library to process
    # the image. So make sure it is installed.
    # Also set the MEDIA_ROOT and MEDIA_URL in main app settings.
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_avatar_base64(self):
        # settings.MEDIA_ROOT = '/path/to/env/projectname/media'
        return image_as_base64(self.avatar.path)


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # models.SET_NULl will set topic field to null if
    # topic object gets deleted.
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User,
                                          related_name="participants",
                                          blank=True)
    # auto_now = True means  the field will be updated every time there is
    # a change in model
    updated = models.DateTimeField(auto_now=True)
    # auto_now_add=True means the field will be updated only first time
    # when we make changes to our models
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This will orderBy descending order of updated and created
        # without "-" will order it in ascending order
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="messages")
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This will orderBy descending order of updated and created
        # without "-" will order it in ascending order
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body
