from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('post/<slug:slug>', views.post_detail, name='post_detail'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('create_post', views.create_post, name='create_post'),
    path('like', views.like, name='like'),
    path('post/<slug:slug>/create_comment', views.create_comment, name='create_comment'),
    path('post/<slug:slug>/<int:comment_id>/create_reply', views.create_reply, name='create_reply'),
]
