from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.username


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Post {self.post_id} by {self.author.username}"

    # Новый метод подсчёта лайков через отдельную таблицу Likes
    def likes_count(self):
        return Like.objects.filter(post=self).count()


class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Likes'
        unique_together = ('user', 'post')  # один пользователь — один лайк

    def __str__(self):
        return f"Like by {self.user.username} on post {self.post.post_id}"


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender.username} to {self.receiver.username}"