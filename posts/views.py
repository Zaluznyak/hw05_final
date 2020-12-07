from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .forms import CommentForm, PostForm
from .models import Post, Group, Follow

User = get_user_model()


def index(request):
    """Dialpaying posts on the homepage."""
    all_posts = Post.objects.all()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
        )


def group_post(request, slug):
    """Displaying posts on the group/slug page."""
    group = get_object_or_404(Group, slug=slug)
    all_posts = group.posts.all()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'group.html', context)


def groups(request):
    """Displaying groups on the group page."""
    all_groups = Group.objects.all()
    paginator = Paginator(all_groups, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'groups.html',
        {'groups': page, 'paginator': paginator}
        )


@login_required
def new_post(request):
    """Displaying a form for adding posts."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        data = form.save(commit=False)
        data.author = request.user
        data.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Displaying posts on the profile."""
    author = get_object_or_404(User, username=username)
    all_posts = author.posts.all()
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).count() != 0
    else:
        following = False
    count_follower = author.following.all().count()
    count_following = author.follower.all().count()
    paginator = Paginator(all_posts, 10)
    count = paginator.count
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'count': count,
        'author': author,
        'following': following,
        'count_follower': count_follower,
        'count_following': count_following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    """Displaying one post."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    else:
        following = False
    count_follower = author.following.all().count()
    count_following = author.follower.all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count = post.author.posts.all().count()
    context = {
        'post': post,
        'count': count,
        'for_pytest': comments,  # костыль.
        'comments': page,
        'form': form,
        'paginator': paginator,
        'following': following,
        'count_follower': count_follower,
        'count_following': count_following
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    """Displaying a form for edit post."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    if request.user == author:
        form = PostForm(request.POST or None, files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', author, post_id)
        return render(request, 'new_post.html', {'form': form, 'post': post})
    return redirect('post', author, post_id)


@login_required
def add_comment(request, username, post_id):
    """Displaying a for for add comment."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        data = form.save(commit=False)
        data.author = request.user
        data.post = post
        data.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    """Displaying posts for subscribe."""
    all_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator}
        )


@login_required
def profile_follow(request, username):
    """Subscribe to author."""
    author = get_object_or_404(User, username=username)
    user = request.user
    subscribe = user.follower.filter(author=author).exists()
    if author != request.user and subscribe is False:
        Follow.objects.create(
            author=author,
            user=user
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe from author."""
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = user.follower.filter(author=author)
    subscribe = follow.exists()
    if subscribe is True:
        follow.delete()
    return redirect('profile', username)


def page_not_found(request, exception=None):
    """Displayning message ERROR404."""
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Displayning message ERROR500."""
    return render(request, "misc/500.html", status=500)
