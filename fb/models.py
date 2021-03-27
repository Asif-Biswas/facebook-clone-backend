from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

# Create your models here.
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.TextField(max_length=10000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_by')
    is_liked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

class Relation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name='my_friends', blank=True)
    i_requested = models.ManyToManyField(User, related_name='i_requested', blank=True)
    requested_me = models.ManyToManyField(User, related_name='requested_me', blank=True)

    #def __str__(self):
    #    return self.user
    

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    member = models.ManyToManyField(User, related_name='groups_user')
    joined = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class GroupsPost(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    body = models.TextField(max_length=10000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_by = models.ManyToManyField(User, blank=True, related_name='groups_post_liked_by')
    is_liked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

class GroupsComment(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(GroupsPost, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

class Invite(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inviter')
    invited_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_to')

class Notification(models.Model):
    liked = models.BooleanField(null=True, default=False)
    commented = models.BooleanField(null=True, default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    groups_post = models.ForeignKey(GroupsPost, on_delete=models.CASCADE, null=True, blank=True)
    invite = models.BooleanField(null=True, default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    body = models.TextField(max_length=1000)
    date =  models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ('date',)
