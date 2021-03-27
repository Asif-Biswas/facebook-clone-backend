from django.contrib import admin
from .models import Post, Comment, Relation, Group, GroupsPost, Message, Notification, GroupsComment
# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Relation)
admin.site.register(Group)
admin.site.register(GroupsPost)
admin.site.register(Notification)
admin.site.register(GroupsComment)
admin.site.register(Message)






