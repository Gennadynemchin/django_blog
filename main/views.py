from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from .forms import RegisterForm, PostForm
from django.contrib.auth.models import User
from .models import Post


@login_required(login_url='/login')
def home(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_author_id = request.POST.get('post_author_id')
        like_post_id = request.POST.get('like_post')
        unlike_post_id = request.POST.get('unlike_post')
        if post_id:
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm('main.delete_post')):
                post.delete()
        elif post_author_id and request.user.is_staff:
            user = User.objects.filter(id=post_author_id).first()
            user.is_active = False
            user.save()
        elif like_post_id:
            user_like = User.objects.filter(id=request.user.id).first()
            post_to_like = Post.objects.filter(id=like_post_id).first()
            post_to_like.likes.add(user_like)
        elif unlike_post_id:
            user_unlike = User.objects.filter(id=request.user.id).first()
            post_to_unlike = Post.objects.filter(id=unlike_post_id).first()
            post_to_unlike.likes.remove(user_unlike)
    posts = Post.objects.all().select_related('author')


    return render(request, 'main/home.html', {'posts': posts})


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {'form': form})


@login_required(login_url='/login')
@permission_required('main.add_post', login_url='/login', raise_exception=True)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'main/create_post.html', {'form': form})
