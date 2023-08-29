from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('post/<slug:slug>', views.post_detail, name='post_detail'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('create_post', views.create_post, name='create_post'),
    path('like', views.like, name='like')
]
