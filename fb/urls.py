from django.urls import path
from . import views
from .views import ChangePasswordView

urlpatterns = [
    path('', views.home, name='home'),
    path('myapi/', views.apiView, name='apiView'),
    path('myapi/changename/', views.changeName, name='changeName'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('myapi/createpost/', views.createPost, name='createPost'),
    path('myapi/allpost/', views.allPost, name='allPost'),
    path('myapi/likepost/<str:pk>/', views.likePost, name='likePost'),
    path('myapi/unlikepost/<str:pk>/', views.unLikePost, name='unLikePost'),

    path('myapi/postcomment/', views.postComment, name='postComment'),
    path('myapi/allcomments/<str:pk>/', views.allComments, name='allComments'),
    path('myapi/userdetails/<str:pk>/', views.userDetails, name='userDetails'),
    path('myapi/checkrelation/<str:pk>/', views.checkRelation, name='checkRelation'),
    path('myapi/addfriend/<str:pk>/', views.addFriend, name='addFriend'),
    path('myapi/cancelfriendrequest/<str:pk>/', views.cancelFriendRequest, name='cancelFriendRequest'),
    path('myapi/deletefriendrequest/<str:pk>/', views.deleteFriendRequest, name='deleteFriendRequest'),
    path('myapi/acceptfriendrequest/<str:pk>/', views.acceptFriendRequest, name='acceptFriendRequest'),
    path('myapi/usersallpost/<str:pk>/', views.usersAllPost, name='usersAllPost'),

    path('myapi/requestedme/', views.requestedMe, name='requestedMe'),
    path('myapi/alluser/', views.allUser, name='allUser'),

    path('myapi/creategroup/', views.createGroup, name='createGroup'),
    path('myapi/getsomegroup/', views.getSomeGroup, name='getSomeGroup'),
    path('myapi/getallgroup/', views.getAllGroup, name='getAllGroup'),
    path('myapi/groupsdata/<str:pk>/', views.groupsData, name='groupsData'),
    path('myapi/joingroup/<str:pk>/', views.joinGroup, name='joinGroup'),
    path('myapi/posttogroup/<str:pk>/', views.postToGroup, name='postToGroup'),
    path('myapi/getgroupspost/<str:pk>/', views.getGroupsPost, name='getGroupsPost'),
    path('myapi/likegroupspost/<str:pk>/', views.likeGroupsPost, name='likeGroupsPost'),
    path('myapi/unlikegroupspost/<str:pk>/', views.unLikeGroupsPost, name='unLikeGroupsPost'),
    path('myapi/postgroupscomment/', views.postGroupsComment, name='postGroupsComment'),
    path('myapi/allgroupscomments/<str:pk>/', views.allGroupsComments, name='allGroupsComments'),
    path('myapi/getsomejoinedgroup/', views.getSomeJoinedGroup, name='getSomeJoinedGroup'),
    path('myapi/getalljoinedgroup/', views.getAllJoinedGroup, name='getAllJoinedGroup'),
    path('myapi/alljoinedgroupspost/', views.allJoinedGroupsPost, name='allJoinedGroupsPost'),

    path('myapi/myallfriends/', views.myAllFriends, name='myAllFriends'),
    path('myapi/invite/<str:pk>/', views.invite, name='invite'),

    path('myapi/notification/', views.myNotification, name='myNotification'),
    path('myapi/postdetails/<str:pk>/', views.postDetails, name='postDetails'),
    path('myapi/groupspostdetails/<str:pk>/', views.groupsPostDetails, name='groupsPostDetails'),

    path('myapi/sendmessage/', views.sendMessage, name='sendMessage'),
    path('myapi/getmessage/<str:pk>/', views.getMessage, name='getMessage'),
    path('myapi/messagehome/', views.messageHome, name='messageHome'),
    path('myapi/number/', views.randomNum, name='randomNum'),

    path('myapi/searchuser/', views.searchUser, name='searchUser'),
    path('myapi/searchgroup/', views.searchGroup, name='searchGroup'),
]