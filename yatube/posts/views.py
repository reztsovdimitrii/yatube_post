from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import pagination


def index(request):
    posts_list = Post.objects.all()
    page_obj = pagination(request, posts_list)
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = pagination(request, posts_list)
    title = f'Записи сообщества { group }.'
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = pagination(request, posts)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    title = 'Профайл пользователя'
    context = {
        'title': title,
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    title = 'Пост'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'title': title,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.id
        post.save()
        return redirect('posts:profile', request.user)
    title = 'Новая запись'
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        return redirect('posts:post_edit', post_id)

    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    title = 'Редактирование записи'
    context = {
        'post_id': post_id,
        'form': form,
        'is_edit': True,
        'title': title,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, posts_list)
    title = 'Посты подписок'
    context = {
        'page_obj': page_obj,
        'title': title,
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    is_follower.delete()
    return redirect('posts:profile', author)
