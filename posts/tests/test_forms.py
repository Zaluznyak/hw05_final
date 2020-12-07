from django.urls import reverse

from posts.models import Post
from .settings import Settings


class FormTests(Settings):
    def test_add_post(self):
        """Пост добавлен в БД, после отправки попали на главную страницу."""
        post_count = Post.objects.all().count()
        files = (
            (self.gif_file, post_count + 1, 'Пост не был добавлен'),
            (self.txt_file, post_count + 1, 'Текст вместо img был добавлен'),
        )
        for uploaded, count, msg in files:
            form_data = {
                'text': 'Тестовый текст' * 5,
                'author': self.User,
                'image': uploaded
                }
            response = self.authorized_client.post(
                reverse('new_post'),
                data=form_data,
                follow=True
                )
            with self.subTest(file=uploaded.name):
                self.assertEqual(
                    Post.objects.count(),
                    count,
                    msg
                    )
                if(uploaded.name != 'small.txt'):
                    self.assertRedirects(
                        response,
                        reverse('index'),
                        msg_prefix=('После отправки поста, '
                                    'не попали на главную страницу')
                        )

    def test_edit_post(self):
        """Пост имзенен, запись в БД сохранена, новый пост не создан."""
        post_count = Post.objects.count()
        file = (
            (self.new_gif_file, 'Тестовое изменение5642',
             'Пост не был изменен'),
            (self.new_txt_file, 'Тестовое изменение2',
             'Пост с добавлением txt был изменен')
        )
        post_id = self.User.posts.first().id
        rvs = reverse('post_edit', kwargs={'username': self.User.username,
                      'post_id': post_id})
        for uploaded, text, msg in file:
            with self.subTest(file=uploaded):
                form_data = {
                    'text': text,
                    'image': uploaded
                }
                response = self.authorized_client.post(
                    rvs,
                    data=form_data,
                    follow=True
                    )
                self.assertEqual(
                    self.User.posts.first().text,
                    'Тестовое изменение5642',
                    msg
                    )
                self.assertEqual(
                    Post.objects.count(),
                    post_count,
                    'Пост был добавлен или удален, а не изменен'
                    )
                if uploaded.name != 'new_small.txt':
                    self.assertRedirects(
                        response,
                        reverse('post', kwargs={
                            'username': self.User.username,
                            'post_id': post_id
                            }),
                        msg_prefix=('После изменения не попали'
                                    ' на страницу с постом')
                        )

    def test_add_comment(self):
        """Комментарий добавлен верно."""
        form_data = {
                'text': 'Тестовый текст' * 5
                }
        cnt_comments = self.post.comments.all().count()
        rvs = reverse('add_comment', kwargs={'username': self.User.username,
                      'post_id': self.post.id})
        self.authorized_client.post(
                    rvs,
                    data=form_data,
                    follow=True
                    )
        self.assertEqual(self.post.comments.all().count(), cnt_comments + 1,
                         'Комментарий не был добавлен')
        self.guest_client.post(
                    rvs,
                    data=form_data,
                    follow=True
                    )
        self.assertFalse(self.post.comments.all().count() > (cnt_comments + 1),
                         'Комментарий был добавлен гостем')
