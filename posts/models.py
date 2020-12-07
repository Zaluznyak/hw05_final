from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField("Текст", help_text="Содержимое поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts"
                               )
    group = models.ForeignKey("Group", on_delete=models.SET_NULL,
                              related_name="posts", blank=True,
                              null=True, verbose_name="Группа",
                              help_text="Куда разместить"
                              )
    image = models.ImageField(
        "Изображение", upload_to='posts/',
        blank=True, null=True
        )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=20)
    description = models.TextField(max_length=500)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(
        "Комментарий", help_text="Оставьте свой комментарий",
        max_length=400
        )
    created = models.DateTimeField("Дата", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f'{self.author.username}: {self.text}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
