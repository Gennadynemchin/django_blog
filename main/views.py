from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import RegisterForm, PostForm
from django.contrib.auth.models import User
from .models import Post, Comment


@login_required(login_url='/login')
def home(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_author_id = request.POST.get('post_author_id')
        if post_id:
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm('main.delete_post')):
                post.delete()
        elif post_author_id and request.user.is_staff:
            user = User.objects.filter(id=post_author_id).first()
            user.is_active = False
            user.save()
    posts = Post.objects.all().select_related('author')
    return render(request, 'main/home.html', {'posts': posts})


@login_required(login_url='/login')
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    context = {'post': post, 'comments': comments}
    return render(request, 'main/post_detail.html', context)


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


@login_required(login_url='/login')
def like(request):
    if request.POST.get('like_post'):
        like = request.POST.get('like_post')
        user = User.objects.filter(id=request.user.id).first()
        post = Post.objects.filter(id=like).first()
        post.likes.add(user)
    else:
        like = request.POST.get('unlike_post')
        user = User.objects.filter(id=request.user.id).first()
        post = Post.objects.filter(id=like).first()
        post.likes.remove(user)
    return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))
