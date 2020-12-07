from django.urls import reverse

from .settings import Settings


class UrlTests(Settings):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_status_name = {
            '/': [200, 200, reverse('index')],
            '/group/': [200, 200, reverse('groups')],
            '/group/test-slug/': [
                200, 200, reverse('group',
                                  kwargs={'slug': UrlTests.group.slug})
                ],
            '/new/': [200, 302, reverse('new_post')],
            '/about-author/': [200, 200, reverse('about')],
            '/about-spec/': [200, 200, reverse('spec')],
            '/test/': [
                200, 200,
                reverse('profile', kwargs={'username': UrlTests.User.username})
                ],
            '/test/1/': [
                200, 200,
                reverse('post', kwargs={'username': UrlTests.User.username,
                                        'post_id': UrlTests.post.id})
            ],
            '/test/1/edit/': [
                200, 302,
                reverse(
                    'post_edit', kwargs={'username': UrlTests.User.username,
                                         'post_id': UrlTests.post.id})
            ],
            '/test/1/comment/': [
                302, 302,
                reverse('add_comment',
                        kwargs={'username': UrlTests.User.username,
                                'post_id': UrlTests.post.id})
                        ],
            '/follow/': [200, 302, reverse('follow_index')],
            '/test2/follow/': [
                302, 302,
                reverse('profile_follow',
                        kwargs={'username': UrlTests.User2.username})
                ],
            '/test2/unfollow/': [
                302, 302,
                reverse('profile_unfollow',
                        kwargs={'username': UrlTests.User2.username})
                ]
        }

    def test_urls_equally_reverse(self):
        """URL-адрес соответсвует с именем."""
        for url, value in UrlTests.url_status_name.items():
            name = value[2]
            with self.subTest(url=url, name=name):
                self.assertEqual(
                    name, url,
                    f'URL-адрес {url} не соответсует name'
                    )

    def test_page_not_found(self):
        """Отсутсвующая страница имеет верный status code."""
        response = self.authorized_client.get('/TestUrlForNotFound/')
        self.assertEqual(
            response.status_code, 404,
            'Неверный status_code для отсутсвующей страницы'
            )

    def test_urls_status_for_authorized(self):
        """URL-адрес возвращает верный status_code для пользователя-автора."""
        for url, value in UrlTests.url_status_name.items():
            auth_code = value[0]
            with self.subTest(url=url, code=auth_code):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code, auth_code,
                    (f'Проверьте страницу <<{url}>>'
                     'для авторизованного пользователя')
                    )

    def test_urls_status_for_guest(self):
        """URL-адрес возвращает верный status_code для гостя."""
        for url, value in UrlTests.url_status_name.items():
            guest_code = value[1]
            with self.subTest(url=url, code=guest_code):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, guest_code,
                    (f'Проверьте страницу <<{url}>>'
                     'для гостевого пользователя')
                     )

    def test_redirect_guest(self):
        """Страницы имеют соответствующий redirect для гостя."""
        username = UrlTests.User.username
        post_id = UrlTests.post.id
        redirects = {
            reverse('login') + '?next=' +
            reverse('new_post'): reverse('new_post'),
            reverse('login') + '?next=' +
            reverse('post_edit', kwargs={'username': username,
                                         'post_id': post_id}):
            reverse('post_edit', kwargs={'username': username,
                                         'post_id': post_id}),
            reverse('login') + '?next=' +
            reverse('add_comment', kwargs={'username': username,
                                           'post_id': post_id}):
            reverse('add_comment', kwargs={'username': username,
                                           'post_id': post_id}),
            reverse('login') + '?next=' +
            reverse('profile_follow', kwargs={'username': username}):
            reverse('profile_follow', kwargs={'username': username}),
            reverse('login') + '?next=' +
            reverse('profile_unfollow', kwargs={'username': username}):
            reverse('profile_unfollow', kwargs={'username': username}),
            reverse('login') + '?next=' +
            reverse('profile_follow', kwargs={'username': username}):
            reverse('profile_follow', kwargs={'username': username}),
            reverse('login') + '?next=' +
            reverse('follow_index'): reverse('follow_index'),
        }
        for url, name in redirects.items():
            with self.subTest(url=url, name=name):
                response = self.guest_client.get(name)
                self.assertRedirects(
                    response, url,
                    msg_prefix=f'Страница {name} имеет неверный редирект'
                    )

    def test_redirect_other_user(self):
        """Post_edit имеет соответствующий redirect для не автора поста."""
        rvs = reverse('post_edit', kwargs={'username': UrlTests.User.username,
                                           'post_id': UrlTests.post.id})
        response = self.authorized_client_2.get(rvs)
        self.assertRedirects(
            response,
            reverse('post', kwargs={'username': UrlTests.User.username,
                                    'post_id': UrlTests.post.id}),
            msg_prefix=f'Страница {rvs} имеет неверный редирект'
            )
