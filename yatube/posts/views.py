from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from .forms import CommentForm, PostForm
from .models import Follow, Group, Like, Post, User


def page_of_paginator(request, queryset):
    return Paginator(queryset, settings.NUMB_POSTS_PAGE).get_page(
        request.GET.get('page')
    )


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_of_paginator(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': page_of_paginator(request, group.posts.all())
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user.is_authenticated,
        author=author,
    ).exists()
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': page_of_paginator(request, author.posts.all()),
        'following': following,
    })


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, id=post_id),
        'form': CommentForm(request.POST or None),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': page_of_paginator(
            request,
            Post.objects.filter(author__following__user=request.user)
        ),
    })


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:follow_index')


class AddLikeView(View):
    def post(self, request, *args, **kwargs):
        blog_post_id = int(request.POST.get('blog_post_id'))
        user_id = int(request.POST.get('user_id'))
        url_from = request.POST.get('url_from')

        user_inst = User.objects.get(id=user_id)
        blog_post_inst = Post.objects.get(id=blog_post_id)

        try:
            blog_like_inst = Like.objects.get(
                blog_post=blog_post_inst,
                liked_by=user_inst
            )
        except Exception as error:
            blog_like = Like(
                blog_post=blog_post_inst,
                liked_by=user_inst,
                like=True
            )
            blog_like.save()
        return redirect(url_from)


class RemoveLikeView(View):
    def post(self, request, *args, **kwargs):
        blog_likes_id = int(request.POST.get('blog_likes_id'))
        url_from = request.POST.get('url_from')

        blog_like = Like.objects.get(id=blog_likes_id)
        blog_like.delete()

        return redirect(url_from)