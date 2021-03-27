from django.shortcuts import render, HttpResponse, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .filters import UserFilter, GroupFilter

import random

from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .serializers import (
    UserSerializers,
    SimpleUserSerializer,
    ChangePasswordSerializer, 
    PostSerializer, 
    CreatePostSerializer,
    CreateCommentSerializer,
    CommentSerializer,
    UserDetailsSerializer,
    CreateGroupSerializer,
    GroupSerializer,
    PostToGroupSerializer,
    GroupsPostSerializer,
    CreateGroupsCommentSerializer,
    GroupsCommentSerializer,
    InviteSerializer,
    NotificationSerializer,
    MessageSerializer,
    GetMessageSerializer,
    SimpleGroupSerializer,
    )
from .models import Post, Comment, Relation, Group, GroupsPost, GroupsComment, Invite, Notification, Message

# Create your views here.
#@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def createPost(request):
    user = request.user.id
    data = {'body': request.data['body'], 'user': user}
    serializer = CreatePostSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})


#@login_required(login_url='/')
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def apiView(request):
    user = request.user.id
    fn = User.objects.get(id=user).first_name
    ln = User.objects.get(id=user).last_name
    data = {
        'firstname':str(fn),
        'lastname':str(ln),
        'user': user
    }
    return Response(data)

@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def changeName(request):
    user = request.user
    #creating a Relation object
    try:
        Relation.objects.get(user=user.id)
    except:
        Relation.objects.create(user=user)
    serializer = UserSerializers(instance=user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def allPost(request):
    paginator = PageNumberPagination()
    paginator.page_size = 10

    user = request.user.id
    allpost = Post.objects.all().exclude(liked_by=user)
    #allpost2 = Post.objects.filter(liked_by=user)
    #allpost = allpost1.
    result_page = paginator.paginate_queryset(allpost, request)
    serializer = PostSerializer(result_page, many=True)
    liked = Post.objects.filter(liked_by__id=user).values_list('id', flat=True)

    for i in serializer.data:
        if i['id'] in liked:
            i['is_liked'] = True
        
    return paginator.get_paginated_response(serializer.data) #Response(serializer.data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def likePost(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    user1 = post.user
    if user != user1:
        if Notification.objects.filter(post=post, liked=True).exists():
            Notification.objects.filter(post=post).update(user2=user)
        else:
            Notification.objects.create(post=post, user1=user1, user2=user, liked=True)
            
    previous_user = post.liked_by.all().values_list('id', flat=True)
    liked_by = [user.id]
    for i in previous_user:
        liked_by.append(i)
    data = {'liked_by':liked_by}
    serializer = CreatePostSerializer(instance=post, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)
    
    return Response({'response': 'liked'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def unLikePost(request, pk):
    user = request.user.id
    post = Post.objects.get(id=pk)
    Notification.objects.filter(post=post, liked=True).delete()
    previous_user = post.liked_by.all().values_list('id', flat=True)
    try:
        liked_by = previous_user.exclude(id=user)
    except:
        pass
    data = {'liked_by':liked_by}
    serializer = CreatePostSerializer(instance=post, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'unliked'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def postComment(request):
    user = request.user
    postId = request.data['post']
    post = Post.objects.get(id=postId)
    data = {'body': request.data['body'], 'user': user.id, 'post':request.data['post']}
    user1 = post.user
    if user != user1:
        if Notification.objects.filter(post=post, commented=True).exists():
            Notification.objects.filter(post=post).update(user2=user)
        else:
            Notification.objects.create(post=post, user1=user1, user2=user, commented=True)
            
    serializer = CreateCommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def allComments(request,pk):
    #user = request.user.id
    allComments = Comment.objects.filter(post=pk)
    #allpost = Post.objects.all()
    serializer = CommentSerializer(allComments, many=True)
    #print(serializer)
    #liked = Post.objects.filter(liked_by__id=user).values_list('id', flat=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def userDetails(request,pk):
    user = User.objects.get(id=pk)
    serializer = UserDetailsSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def checkRelation(request,pk):
    me = request.user
    user = User.objects.get(id=pk)
    if me == user:
        return Response({'response':'me'})
    else:
        try:
            rel = Relation.objects.get(user=me.id)
        except:
            rel = Relation.objects.create(user=me)
        if rel.friends.filter(id=user.id).exists():
            return Response({'response':'friend'})
        elif rel.i_requested.filter(id=user.id).exists():
            return Response({'response':'i_requested'})
        elif rel.requested_me.filter(id=user.id).exists():
            return Response({'response':'requested_me'})
        else:
            return Response({'response':'add_friend'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def addFriend(request,pk):
    me = request.user
    user = User.objects.get(id=pk)
    try:
        myrel = Relation.objects.get(user=me.id)
    except:
        myrel = Relation.objects.create(user=me)
    try:
        userrel = Relation.objects.get(user=user.id)
    except:
        userrel = Relation.objects.create(user=user)
    myrel.i_requested.add(user)
    userrel.requested_me.add(me)
    return Response({'response':'added'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def cancelFriendRequest(request,pk):
    me = request.user
    user = User.objects.get(id=pk)
    try:
        myrel = Relation.objects.get(user=me.id)
    except:
        myrel = Relation.objects.create(user=me)

    try:
        userrel = Relation.objects.get(user=user.id)
    except:
        userrel = Relation.objects.create(user=user)
    myrel.i_requested.remove(user)
    userrel.requested_me.remove(me)
    return Response({'response':'canceled'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def acceptFriendRequest(request,pk):
    me = request.user
    user = User.objects.get(id=pk)
    try:
        myrel = Relation.objects.get(user=me.id)
    except:
        myrel = Relation.objects.create(user=me)

    try:
        userrel = Relation.objects.get(user=user.id)
    except:
        userrel = Relation.objects.create(user=user)
    myrel.friends.add(user)
    myrel.requested_me.remove(user)
    userrel.friends.add(me)
    userrel.i_requested.remove(me)

    Message.objects.create(receiver=user, sender=me, body='We are connected now')

    return Response({'response':'accepted'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def deleteFriendRequest(request,pk):
    me = request.user
    user = User.objects.get(id=pk)
    try:
        myrel = Relation.objects.get(user=me.id)
    except:
        myrel = Relation.objects.create(user=me)

    try:
        userrel = Relation.objects.get(user=user.id)
    except:
        userrel = Relation.objects.create(user=user)
    myrel.requested_me.remove(user)
    userrel.i_requested.remove(me)
    return Response({'response':'deleted'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usersAllPost(request,pk):
    myid = request.user.id
    user = User.objects.get(id=pk)
    allpost = Post.objects.filter(user=user.id)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(allpost, request)
    serializer = PostSerializer(result, many=True)
    liked = Post.objects.filter(liked_by__id=myid).values_list('id', flat=True)

    for i in serializer.data:
        if i['id'] in liked:
            i['is_liked'] = True
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def requestedMe(request):
    me = request.user
    #print(Relation.objects.get(user=me.id))
    try:
        rel = Relation.objects.get(user=me.id)
    except:
        rel = Relation.objects.create(user=me)
    #me = request.user
    req = rel.requested_me.all().order_by('?')
    serializer = SimpleUserSerializer(req, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def allUser(request):
    me = request.user
    try:
        f = Relation.objects.get(user=me.id)
    except:
        f = Relation.objects.create(user=me)
    #f = Relation.objects.get(user=me)
    ff = f.friends.all()
    fi = f.i_requested.all()
    fm = f.requested_me.all()

    user = User.objects.all().order_by('?')
    e = user.exclude(id=me.id).exclude(id__in=ff.values_list('id', flat=True)).exclude(id__in=fi.values_list('id', flat=True)).exclude(id__in=fm.values_list('id', flat=True))
    #e = user.exclude(id=me.id)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(e, request)

    serializer = SimpleUserSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def createGroup(request):
    me = request.user.id
    data = {'name': request.data['name'], 'admin': me}
    serializer = CreateGroupSerializer(data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getSomeGroup(request):
    me = request.user.id
    allGroup = Group.objects.all().order_by('?')#.values_list('id', flat=True)
    for i in allGroup:
        if i.member.filter(id=me).exists():
            allGroup = allGroup.exclude(pk=i.id)

    #print(allGroup)
    #llGroup = 16
    #randomGroupId = random.sample(range(6,llGroup), 3)
    randomGroup = allGroup[:3] #Group.objects.filter(id__in=randomGroupId)
    serializer = GroupSerializer(randomGroup, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getAllGroup(request):
    me = request.user.id
    allGroup = Group.objects.all().order_by('?')
    for i in allGroup:
        if i.member.filter(id=me).exists():
            allGroup = allGroup.exclude(pk=i.id)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(allGroup, request)

    serializer = GroupSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def groupsData(request, pk):
    user = request.user.id
    group = Group.objects.get(id=pk)
    serializer = GroupSerializer(group)
    serialized_data = serializer.data
    if group.member.filter(id=user).exists():
        serialized_data['joined'] = True
    return Response(serialized_data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def joinGroup(request, pk):
    me = request.user
    group = Group.objects.get(id=pk)
    group.member.add(me)
    return Response({'response': 'ok'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def postToGroup(request, pk):
    group = Group.objects.get(id=pk)
    me = request.user.id
    data = {'body': request.data['body'], 'user': me, 'group': group.id}
    serializer = PostToGroupSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getGroupsPost(request, pk):
    group = Group.objects.get(id=pk)
    me = request.user.id
    allPost = GroupsPost.objects.filter(group=group)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(allPost, request)
    serializer = GroupsPostSerializer(result, many=True)
    liked = GroupsPost.objects.filter(liked_by__id=me).values_list('id', flat=True)

    for i in serializer.data:
        if i['id'] in liked:
            i['is_liked'] = True
        
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def likeGroupsPost(request, pk):
    user = request.user
    post = GroupsPost.objects.get(id=pk)
    group = post.group
    user1 = post.user
    if user != user1:
        if Notification.objects.filter(groups_post=post, liked=True, group=group).exists():
            Notification.objects.filter(groups_post=post).update(user2=user)
        else:
            Notification.objects.create(groups_post=post, user1=user1, user2=user, liked=True, group=group)
            
    previous_user = post.liked_by.all().values_list('id', flat=True)
    liked_by = [user.id]
    for i in previous_user:
        liked_by.append(i)
    data = {'liked_by':liked_by}
    serializer = PostToGroupSerializer(instance=post, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'liked'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def unLikeGroupsPost(request, pk):
    user = request.user.id
    post = GroupsPost.objects.get(id=pk)
    Notification.objects.filter(groups_post=post, liked=True).delete()
    previous_user = post.liked_by.all().values_list('id', flat=True)
    try:
        liked_by = previous_user.exclude(id=user)
    except:
        pass
    data = {'liked_by':liked_by}
    serializer = PostToGroupSerializer(instance=post, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'unliked'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def postGroupsComment(request):
    user = request.user
    userId = user.id
    data = {'body': request.data['body'], 'user': userId, 'post':request.data['post']}

    postId = request.data['post']
    post = GroupsPost.objects.get(id=postId)
    group = post.group
    user1 = post.user
    if user != user1:
        if Notification.objects.filter(groups_post=post, commented=True).exists():
            Notification.objects.filter(groups_post=post).update(user2=user)
        else:
            Notification.objects.create(groups_post=post, user1=user1, user2=user, commented=True, group=group)
            
    serializer = CreateGroupsCommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def allGroupsComments(request,pk):
    #user = request.user.id
    allComments = GroupsComment.objects.filter(post=pk)
    #allpost = Post.objects.all()
    serializer = GroupsCommentSerializer(allComments, many=True)
    #print(serializer)
    #liked = Post.objects.filter(liked_by__id=user).values_list('id', flat=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getSomeJoinedGroup(request):
    me = request.user.id
    allGroup = Group.objects.all().order_by('?')#.values_list('id', flat=True)
    for i in allGroup:
        if i.member.filter(id=me).exists() != True:
            allGroup = allGroup.exclude(pk=i.id)
    
    randomGroup = allGroup[:3] 
    serializer = GroupSerializer(randomGroup, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getAllJoinedGroup(request):
    me = request.user.id
    allGroup = Group.objects.all().order_by('?')
    for i in allGroup:
        if i.member.filter(id=me).exists() != True:
            allGroup = allGroup.exclude(pk=i.id)
    serializer = GroupSerializer(allGroup, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def allJoinedGroupsPost(request):
    me = request.user.id
    myGroups = Group.objects.filter(member=me)
    allpost = GroupsPost.objects.all().order_by('?')
    for i in allpost:
        groupName = i.group
        if groupName not in myGroups:
            allpost = allpost.exclude(pk=i.id)
        #i.objects.filter(group__)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(allpost, request)

    serializer = GroupsPostSerializer(result, many=True)
    liked = GroupsPost.objects.filter(liked_by__id=me).values_list('id', flat=True)

    for i in serializer.data:
        if i['id'] in liked:
            i['is_liked'] = True
        
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def myAllFriends(request):
    me = request.user.id
    try:
        myrel = Relation.objects.get(user=me)
    except:
        myrel = Relation.objects.create(user=me)

    myFriends = myrel.friends.all().order_by('?')

    serializer = SimpleUserSerializer(myFriends, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def invite(request, pk):
    inviter = request.user
    invited_to = User.objects.get(id=pk)
    groupId = request.data['group']
    group = Group.objects.get(id=groupId)
    if not Notification.objects.filter(group=group, user2=inviter, user1=invited_to).exists():
        Notification.objects.create(group=group, user2=inviter, user1=invited_to, invite=True)
    '''data = {'group': group,'inviter': inviter, 'invited_to': invited_to}
    serializer = InviteSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)'''

    return Response({'response': 'invited'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def myNotification(request):
    me = request.user.id
    notification = Notification.objects.filter(user1=me).order_by('-id')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(notification, request)
    serializer = NotificationSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def postDetails(request, pk):
    me = request.user
    post = Post.objects.get(id=pk)
    serializer = PostSerializer(post)
    if post.liked_by.filter(id=me.id).exists():
        data = serializer.data
        data['is_liked']=True
    else:
        data = serializer.data
    return Response(data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def groupsPostDetails(request, pk):
    me = request.user
    post = GroupsPost.objects.get(id=pk)
    serializer = GroupsPostSerializer(post)
    if post.liked_by.filter(id=me.id).exists():
        data = serializer.data
        data['is_liked']=True
    else:
        data = serializer.data
    return Response(data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def sendMessage(request):
    me = request.user.id
    receiver = request.data['receiver']
    body = request.data['body']
    data = {'sender':me, 'receiver': receiver, 'body': body}
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)

    return Response({'response': 'ok'})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getMessage(request, pk):
    me = request.user.id
    user = User.objects.get(id=pk)
    msg = Message.objects.filter(Q(receiver=me, sender=user.id)|Q(receiver=user.id, sender=me)).reverse()
    paginator = PageNumberPagination()
    paginator.page_size = 15
    result = paginator.paginate_queryset(msg, request)
    serializer = GetMessageSerializer(result, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def messageHome(request):
    me = request.user.id
    msg = []
    user = []
    mess = Message.objects.filter(Q(receiver=me)|Q(sender=me)).order_by('-date')
    
    for mes in mess:
        if mes.sender.id == me:
            if mes.receiver.id not in user:
                user.append(mes.receiver.id)
        else:
            if mes.sender.id not in user:
                user.append(mes.sender.id)

    for i in user:
        lm = Message.objects.filter(Q(receiver=me, sender=i)|Q(receiver=i, sender=me)).latest('date')
        msg.append(lm)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result = paginator.paginate_queryset(msg, request)

    s = GetMessageSerializer(result, many=True, context={'request': request})
    return paginator.get_paginated_response(s.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def randomNum(request):
    num = random.randint(1,10)
    return Response({'num':num})

#@api_view(['GET'])
'''@permission_classes((IsAuthenticated,))
class SearchUser(ListAPIView):
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer
    filterset_fields = ['username']'''


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def searchUser(request):
    me = request.user
    queryset = User.objects.all()#.exclude(id=me.id)
    filterset = UserFilter(request.GET, queryset=queryset)
    if filterset.is_valid():
        queryset = filterset.qs

    paginator = PageNumberPagination()
    paginator.page_size = 3
    result = paginator.paginate_queryset(queryset, request)

    serializer = SimpleUserSerializer(result, many=True)

    try:
        rel = Relation.objects.get(user=me.id)
    except:
        rel = Relation.objects.create(user=me)
    
    myresult = serializer.data
    #print(rel.friends.all().values_list('id', flat=True))
    for i in myresult:
        if i['id'] in rel.friends.all().values_list('id', flat=True):
            i['relation'] = 'friend'
        elif i['id'] in rel.requested_me.all().values_list('id', flat=True):
            i['relation'] = 'requested_me'
        elif i['id'] in rel.i_requested.all().values_list('id', flat=True):
            i['relation'] = 'i_requested'
        elif i['id'] == me.id:
            i['relation'] = 'me'
        else:
            i['relation'] = 'add_friend'
    
    return paginator.get_paginated_response(myresult)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def searchGroup(request):
    queryset = Group.objects.all()
    filterset = GroupFilter(request.GET, queryset=queryset)
    if filterset.is_valid():
        queryset = filterset.qs
    
    paginator = PageNumberPagination()
    paginator.page_size = 3
    result = paginator.paginate_queryset(queryset, request)

    serializer = SimpleGroupSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)
