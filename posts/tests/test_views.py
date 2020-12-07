from django.core.cache import cache
from django.urls import reverse
from django import forms

from .settings import Settings
from posts.models import Follow, Group, Post


class ViewsTests(Settings):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Название_2',
            description='Текст_2',
            slug='test-slug2',
        )
        cls.group2 = Group.objects.get(title='Название_2')

    def test_img_tag(self):
        """На страницах есть тег img."""
        reverse_names = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.User.username}),
            reverse('post', kwargs={'username': self.User.username,
                                    'post_id': self.post.id})
        ]
        for reverse_name in reverse_names:
            with self.subTest(name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertContains(
                    response, '<img',
                    msg_prefix=f'На {reverse_name} отсутсвует тег img'
                    )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = [
            ['index.html', reverse('index')],
            ['new_post.html', reverse('new_post')],
            ['new_post.html', reverse(
                'post_edit',
                kwargs={'username': 'test', 'post_id': self.post.id})],
            ['groups.html', reverse('groups')],
            ['group.html', reverse('group', kwargs={'slug': self.group.slug})],
            ['profile.html', reverse(
                'profile', kwargs={'username': self.User.username}
                )],
            ['flatpages/default.html', reverse('about')],
            ['flatpages/default.html', reverse('spec')],
            ['follow.html', reverse('follow_index')],
            ['post.html',
             reverse('post', kwargs={'username': self.User.username,
                                     'post_id': self.post.id})]
        ]

        for value in templates_pages_names:
            template, reverse_name = value
            with self.subTest(template=template, reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    (f'Шаблон на странице {reverse_name}'
                     f'не соответсвует {template}')
                     )

    def test_posts_page_context(self):
        """Шаблон index, group, profile сформирован с правильным контекстом.
        Пост отображается в index, group, profile.
        """
        name_reverse = {
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.User.username})
        }
        for reverse_name in name_reverse:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_text = response.context['page'][0].text
                post_author = response.context['page'][0].author
                post_group = response.context['page'][0].group
                post_image = response.context['page'][0].image

                self.assertEqual(post_text, 'Тестовый текст'*5)
                self.assertEqual(post_author, self.User)
                self.assertEqual(post_group, self.group)
                self.assertIsNotNone(post_image)

    def test_post_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.User.username,
                                    'post_id': self.post.id})
            )
        self.assertEqual(response.context['post'].text, 'Тестовый текст'*5)
        self.assertEqual(response.context['post'].author, self.User)
        self.assertEqual(response.context['post'].group, self.group)
        self.assertIsNotNone(response.context['post'].image)
        self.assertEqual(response.context['author'], self.User)
        self.assertEqual(response.context['count'], 1)

    def test_groups_context(self):
        """Шаблон groups сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('groups'))
        group_title = response.context['groups'][0].title
        group_slug = response.context['groups'][0].slug
        group_id = response.context['groups'][0].id
        group_description = response.context.get('groups')[0].description

        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_slug, self.group.slug)
        self.assertEqual(group_description, self.group.description)
        self.assertEqual(group_id, 1)

    def test_new_post_context(self):
        """Шаблон new_post, post_edit сформирован с правильным контекстом."""
        reverse_name = [
            reverse('new_post'),
            reverse('post_edit', kwargs={'username': self.User.username,
                                         'post_id': self.post.id})
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for rev_name in reverse_name:
            response = self.authorized_client.get(rev_name)
            for value, expected in form_fields.items():
                with self.subTest(value=value, expected=expected):
                    form_field = response.context['form'].fields.get(value)
                    self.assertIsInstance(
                        form_field, expected,
                        f'{rev_name} имеет неправильный контекст'
                        )

    def test_post_not_in_other_group(self):
        """Пост находится в группе, для которой он предназначен."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': ViewsTests.group2.slug})
        )
        self.assertEqual(
            len(response.context['page']), 0, 'Пост попал в другую группу'
            )

    def test_pagination_posts_page(self):
        """Paginator для index, group, profile работает верно."""
        Post.objects.all().delete()
        number_of_posts = 13
        for _ in range(number_of_posts):
            Post.objects.create(
                text='Тестовый текст' * 5,
                author=self.User,
                group=self.group
            )
        name_reverse = [
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.User.username})
        ]
        for reverse_name in name_reverse:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, 200,
                    f'{reverse_name} работает некорректно'
                    )
                self.assertEqual(
                    len(response.context['page']), 10,
                    f'{reverse_name} отображает неверное кол-во постов'
                    )

                response = self.authorized_client.get(
                    reverse_name+'?page=2'
                    )
                self.assertEqual(
                    response.status_code, 200,
                    f'{reverse_name+"?page=2"} работает некорректно'
                    )
                self.assertEqual(
                    len(response.context['page']), 3,
                    (f'{reverse_name+"?page=2"} отображает '
                     'неверное кол-во постов')
                    )

    def test_paginaton_groups(self):
        """Paginator для groups работает верно."""
        Group.objects.all().delete()
        number_of_groups = 13
        for i in range(number_of_groups):
            Group.objects.create(
                title='Название_'+str(i),
                description='Текст_'+str(i),
                slug='test-slug_'+str(i),
            )
        response = self.authorized_client.get(reverse('groups'))
        self.assertEqual(
            response.status_code, 200,
            f'{reverse("groups")} работает некорректно'
            )
        self.assertEqual(
            len(response.context['groups']), 10,
            f'{reverse("groups")} отображает неверное кол-во постов')

        response = self.authorized_client.get(
                    reverse('groups')+'?page=2'
                    )
        self.assertEqual(
            response.status_code, 200,
            f'{reverse("groups")+"?page=2"} работает некорректно')
        self.assertEqual(
            len(response.context['groups']), 3,
            f'{reverse("groups")+"?page=2"} отображает неверное кол-во постов'
            )

    def test_cache_index(self):
        """Cache работает верно."""
        client = self.authorized_client
        response = client.get(reverse('index'))
        content = response.content
        Post.objects.create(
                text='Тестовый текст' * 5,
                author=self.User
            )
        response = client.get(reverse('index'))
        self.assertEqual(content, response.content, 'Кеширование не работает')
        cache.clear()
        response = client.get(reverse('index'))
        self.assertNotEqual(content, response.content,
                            'Кеширование неисправно')

    def test_flatpages_context(self):
        """Flatpages сформированны с правильным контекстом."""
        title_reverse = {
            'about my tech': reverse('spec'),
            'about': reverse('about')
        }
        for title, reverse_name in title_reverse.items():
            with self.subTest(title=title, reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['flatpage'].title,
                    title,
                    f'Страница {reverse_name} имеет неверный title')
                self.assertEqual(
                    response.context['flatpage'].content,
                    '<h1>content</h1>',
                    f'Страница {reverse_name} имеет неверный content'
                    )

    def test_add_follow(self):
        """Подписка работает."""
        count = self.User.follower.count()
        self.authorized_client.get(
               reverse('profile_follow',
                       kwargs={'username': self.User2.username})
            )
        self.assertEqual(self.User.follower.count(), count + 1,
                         'Подписка не работает')
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.User2.username})
            )
        self.assertFalse(self.User.follower.count() > (count + 1),
                         'Нельзя дважды подписаться на одного автора')
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.User.username})
             )
        self.assertFalse(self.User.follower.count() > (count + 1),
                         'Нельзя подписываться на самого себя!')
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.User2.username})
            )
        self.assertEqual(self.User.follower.count(), count,
                         'Отписка не работает')

    def test_add_post_for_subscribe(self):
        """Записи подписок появляются."""
        Follow.objects.all().delete()
        response = self.authorized_client_2.get(reverse('follow_index'))
        count_posts = response.context['paginator'].count
        self.assertEqual(count_posts, 0, 'Вывод постов подписок некорректный')
        self.authorized_client_2.get(
            reverse('profile_follow', kwargs={'username': self.User.username})
            )
        for _ in range(13):
            Post.objects.create(
                text='Тестовый текст',
                author=self.User
            )
        response = self.authorized_client_2.get(reverse('follow_index'))
        count_posts = response.context['paginator'].count
        self.assertEqual(count_posts, self.User.posts.all().count(),
                         'Вывод постов подписок некорректный')
        response = self.authorized_client_3.get(reverse('follow_index'))
        count_posts = response.context['paginator'].count
        self.assertEqual(count_posts, 0,
                         'Посты попали к пользователю без подписок')
