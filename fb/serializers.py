from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, GroupsPost, Group, GroupsComment, Invite, Notification, Message

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name')

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields ='__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()
    class Meta:
        model = Comment
        fields = ('id','body','date','user','post')

class PostSerializer(serializers.ModelSerializer):
    #comments = CommentSerializer()
    user = SimpleUserSerializer()
    total_likes = serializers.SerializerMethodField()
    #liked_by = SimpleUserSerializer(many=True, read_only=True)
    total_comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ('id','body','date','user','total_likes','total_comments','is_liked')

    def get_total_likes(self, instance):
        return instance.liked_by.count()

    def get_total_comments(self, instance):
        return instance.comment_set.count()
        
    #def get_is_liked(self, inctance):
    #    return inctance.liked_by.filter(id=inctance.user.id).exists()

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields ='__all__'

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name')

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    admin = SimpleUserSerializer()
    member = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ('id','name','member','admin','joined')

    def get_member(self, instance):
        return instance.member.count()

class PostToGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupsPost
        fields = '__all__'

class SimpleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id','name')

class GroupsPostSerializer(serializers.ModelSerializer):
    #comments = CommentSerializer()
    user = SimpleUserSerializer()
    group = SimpleGroupSerializer()
    total_likes = serializers.SerializerMethodField()
    #liked_by = SimpleUserSerializer(many=True, read_only=True)
    total_comments = serializers.SerializerMethodField()
    class Meta:
        model = GroupsPost
        fields = ('id','body','group','date','user','total_likes','total_comments','is_liked')

    def get_total_likes(self, instance):
        return instance.liked_by.count()

    def get_total_comments(self, instance):
        return instance.groupscomment_set.count()

class CreateGroupsCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupsComment
        fields ='__all__'

class GroupsCommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()
    class Meta:
        model = GroupsComment
        fields = ('id','body','date','user','post')

class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields ='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user2 = SimpleUserSerializer()
    group = SimpleGroupSerializer()
    class Meta:
        model = Notification
        fields = ('liked','commented','post','groups_post','invite','group','user1','user2')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields ='__all__'

class GetMessageSerializer(serializers.ModelSerializer):
    sender = SimpleUserSerializer()
    receiver = SimpleUserSerializer()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        u = self.context['request'].user
        if u==obj.receiver:
            nam = {'name':obj.sender.first_name +' '+obj.sender.last_name, 'id': obj.sender.id}
            return nam
        nam = {'name':obj.receiver.first_name +' '+obj.receiver.last_name, 'id': obj.receiver.id}
        return nam

    class Meta:
        model = Message
        fields = ('user','body','date','seen','id','sender','receiver')
