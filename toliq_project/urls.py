from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    path('messages/', views.messages_list, name='messages_list'),
    path('chat/<int:user_id>/', views.chat, name='chat'),

    path('profile/', views.profile, name='my_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/avatar/upload/', views.upload_avatar, name='upload_avatar'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    path('search/', views.search_users, name='search_users'),

    path('admin/', admin.site.urls),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)