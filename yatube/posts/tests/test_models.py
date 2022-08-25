from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='группа',
            slug='слаг',
            description='описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Короткий пост',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text='Не более 15 символов может уместиться в превью'
        )

    def test_models_have_correct_object_names(self):
        """У модели Post корректно работает __str__."""
        self.assertEqual(str(self.long_post)[:15], "Не более 15 сим")
        self.assertEqual(str(self.post), "Короткий пост")


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='группа',
            slug='слаг',
            description='описание',
        )

    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
