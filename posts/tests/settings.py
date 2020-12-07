import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.flatpages.models import FlatPage
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.conf import settings

from posts.models import Group, Post


class Settings(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.gettempdir()
        get_user = get_user_model()
        user = get_user.objects.create(username='test')
        user2 = get_user.objects.create(username='test2')
        user3 = get_user.objects.create(username='test3')
        cls.User = user
        cls.User2 = user2
        cls.User3 = user3
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(user2)
        cls.authorized_client_3 = Client()
        cls.authorized_client_3.force_login(user3)

        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
            )
        cls.txt = (
            b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'
            )
        cls.gif_file = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
            )
        cls.txt_file = SimpleUploadedFile(
            name='small.txt',
            content=cls.txt,
            content_type='text/plain'
            )
        cls.new_gif_file = SimpleUploadedFile(
            name='new_small.gif',
            content=cls.gif,
            content_type='image/gif'
            )
        cls.new_txt_file = SimpleUploadedFile(
            name='new_small.txt',
            content=cls.txt,
            content_type='text/plain'
            )

        Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы'
        )
        Post.objects.create(
            text='Тестовый текст' * 5,
            author=user,
            group=Group.objects.first(),
            image=SimpleUploadedFile(
                name='small_.gif',
                content=cls.gif,
                content_type='image/gif'
                )
        )

        cls.post = Post.objects.first()
        cls.group = Group.objects.first()

        site = Site.objects.get(pk=1)
        flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about',
            content='<h1>content</h1>'
        )
        flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<h1>content</h1>'
        )
        flat_about.sites.add(site)
        flat_tech.sites.add(site)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
