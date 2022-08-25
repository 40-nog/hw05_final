from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from .test_models import PostModelTest
from django.core.cache import cache


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='заголовок',
            slug='slug',
            description='описание'
        )
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='пост',
        )
        cls.non_author = User.objects.create_user(username='non_author')

    def setUp(self):
        cache.clear()
        # Создаем экземпляр клиента
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_null_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_post_create_avaliable_for_authorized_client(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_page_avaliable_for_author(self):
        response = self.authorized_client.get(
            f'/posts/{PostModelTest.post.id}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_pages_avaliable_for_all_clients(self):
        pages = [
            '/',
            '/group/slug/',
            '/profile/user/',
            f'/posts/{PostModelTest.post.id}/',
        ]
        for page in pages:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_edit_page_unavaliable_for_not_author(self):
        response = self.non_author_client.get(
            f'/posts/{PostModelTest.post.id}/edit/'
        )
        self.assertEqual(response.status_code, 302)

    def test_for_public_pages(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/user/': 'posts/profile.html',
            f'/posts/{PostModelTest.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_only_authorized(self):
        templates_url_names = {
            '/create/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.non_author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_only_author(self):
        templates_url_names = {
            f'/posts/{PostModelTest.post.id}/edit/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
