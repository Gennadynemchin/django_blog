from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import RegisterForm, PostForm, CommentForm
from django.contrib.auth.models import User
from .models import Post, Comment


@login_required(login_url='/login')
def home(request):
    posts = Post.objects.all().select_related('author').prefetch_related('likes').annotate(Count('likes')).order_by('-created_at')
    pinned_post = posts.filter(pinned=True).first()
    popular_posts = posts.annotate(Count('likes')).order_by('likes__count')[:2]
    return render(request, 'main/home.html', {'posts': posts, 'pinned_post': pinned_post, 'popular_posts': popular_posts})


def manage_user(request):
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
    return None


def is_liked(post, user_id):
    if post.likes.filter(id=user_id):
        return 'Unlike'
    else:
        return 'Like'


@login_required(login_url='/login')
def post_detail(request, slug):
    manage_user(request)
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all().select_related('user', 'parent')
    like_status = is_liked(post, request.user.id)
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'like_status': like_status, 'form': form}
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
    like = request.POST.get('like')
    user = User.objects.filter(id=request.user.id).first()
    post = Post.objects.filter(id=like).first()
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))


@login_required(login_url='/login')
def create_comment(request, slug):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(slug=slug)
            comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[slug]))


@login_required(login_url='/login')
def create_reply(request, slug, comment_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(slug=slug)
            comment.parent = Comment.objects.get(pk=comment_id)
            comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[slug]))
