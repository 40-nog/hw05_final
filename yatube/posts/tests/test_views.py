import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Group, Post, Follow
from django import forms
from django.core.cache import cache
User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user('user')
        cls.group = Group.objects.create(
            title='заголовок',
            slug='slug',
            description='описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='пост',
            group=cls.group,
            image=uploaded
        )
        cls.another_group = Group.objects.create(
            title='заголовок группы',
            slug='group_slug',
            description='описание группы')

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'user'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.id}'}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, PostsPagesTests.post.text)
        self.assertEqual(post.author, PostsPagesTests.post.author)
        self.assertEqual(post.group, PostsPagesTests.post.group)
        self.assertEqual(post.image, PostsPagesTests.post.image)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(
            response.context['group'].description,
            self.group.description
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_profile_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image
        )

    def test_post_detail_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_post_create_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertIsInstance(
            response.context['form'].fields['group'],
            forms.fields.ChoiceField
        )

    def test_post_edit_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertIsInstance(
            response.context['form'].fields['group'],
            forms.fields.ChoiceField
        )

    def test_new_post_added_to_main_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(response.context['page_obj'][0], Post.objects.all())

    def test_post_added_to_group_page(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertIn(self.post, response.context['posts'])

    def test_post_added_to_profile(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertIn(response.context['page_obj'][0], Post.objects.all())

    def test_post_not_added_to_other_group(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.another_group.slug}
            )
        )
        self.assertIsNot(self.post, response.context['posts'])

    def test_index_cache(self):
        posts = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='Новый пост',
            author=self.user
        )
        cached_posts = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertEqual(posts, cached_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='заголовок',
            slug='pag_slug',
            description='описание'
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text=f'пост {i}',
                group=cls.group
            )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()

    def test_pagination(self):
        first_page = 10
        second_page = 3
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(len(self.guest_client.get(page).context.get(
                    'page_obj')), first_page)
                self.assertEqual(len(self.guest_client.get(
                    page + '?page=2').context.get('page_obj')), second_page)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user('user')
        cls.following_user = User.objects.create_user(
            username='following_user'
        )
        cls.group = Group.objects.create(
            title='заголовок',
            slug='new_slug',
            description='описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='пост',
            group=cls.group,
        )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.following_client = Client()
        self.authorized_client.force_login(self.user)
        self.following_client.force_login(self.following_user)

    def test_follow(self):
        follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.following_user.username}
        )
        self.authorized_client.get(follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.following_user.username}
        )
        self.authorized_client.get(unfollow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_new_post_to_followers(self):
        follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.following_user.username}
        )
        self.authorized_client.get(follow, follow=True)
        self.post = Post.objects.create(
            text='Подписка',
            author=self.following_user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_not_for_unfollowers(self):
        response_not_follow = self.following_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response_not_follow.context['page_obj'])
