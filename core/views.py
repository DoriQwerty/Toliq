from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Message, Like, User
from .forms import UserRegistrationForm, PostForm, MessageForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!',extra_tags='register')
            return redirect('feed')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.',extra_tags='register')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Неверный логин или пароль',extra_tags='login')
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    form = PostForm()
    suggested_users = User.objects.exclude(id=request.user.id).order_by('?')[:5]

    return render(request, 'feed.html', {
        'posts': posts,
        'form': form,
        'suggested_users': suggested_users
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    return redirect('feed')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    like_exists = Like.objects.filter(user=request.user, post=post).exists()

    if like_exists:
        Like.objects.filter(user=request.user, post=post).delete()
    else:
        Like.objects.create(user=request.user, post=post)

    likes_count = Like.objects.filter(post=post).count()
    return JsonResponse({'likes_count': likes_count})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id, author=request.user)
    post.delete()
    return redirect('feed')


# ==================== ПРОФИЛЬ ====================

@login_required
def profile(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    # Обработка загрузки аватарки
    if request.method == 'POST' and request.FILES.get('avatar') and profile_user == request.user:
        profile_user.avatar = request.FILES['avatar']
        profile_user.save()
        messages.success(request, 'Аватарка успешно обновлена!')
        return redirect('my_profile')

    posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts
    })


@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, 'Аватарка успешно обновлена!')
    return redirect('my_profile')


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Аккаунт был удалён.')
        return redirect('login')
    return redirect('my_profile')


# ==================== ПОИСК И СООБЩЕНИЯ ====================

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[:20] if query else []
    return render(request, 'search_users.html', {'users': users, 'query': query})


@login_required
def messages_list(request):
    chats = []

    users = User.objects.exclude(id=request.user.id)

    for user in users:
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by('-created_at').first()

        if last_message:
            chats.append({
                'user': user,
                'last_message': last_message.text,
                'last_time': last_message.created_at
            })

    return render(request, 'messages.html', {'chats': chats})


@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect('chat', user_id=user_id)
    else:
        form = MessageForm()

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages_qs,
        'form': form
    })

def password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают', extra_tags='reset_password')
        elif len(new_password) < 6:
            messages.error(request, 'Пароль должен быть не менее 6 символов', extra_tags='reset_password')
        else:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, f'Пароль для пользователя {username} успешно изменён!', extra_tags='reset_password')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким именем не найден', extra_tags='reset_password')

    return render(request, 'password_reset.html')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            # При успехе — просто возвращаемся в ленту без сообщения
            return redirect('feed')
        else:
            # Показываем ошибку только при проблеме
            messages.error(request, '❌ Ошибка при редактировании поста. Проверьте текст.', extra_tags='edit_post')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {
        'form': form,
        'post': post
    })