from django.test import TestCase

from ..models import (Comment, COMMENT, Follow, Group, INFO_ABOUT_POST, Post,
                      SUBSCRIPTION, User)

SLUG = 'test_slug'
USERNAME = 'test-author'
USERNAME_2 = 'authorized_user'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_of_post = User.objects.create_user(USERNAME)
        cls.authorized_user = User.objects.create_user(USERNAME_2)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовой описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.author_of_post,
            text='Тестовый текст поста',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.authorized_user,
            text='Текст комментария',
        )
        cls.subscription = Follow.objects.get_or_create(
            user=cls.authorized_user,
            author=cls.post.author
        )
        cls.subscription = Follow.objects.get(user=cls.authorized_user,
                                              author=cls.post.author)

    def test_models_have_correct_object_name(self):
        '''Проверяем, что у моделей Group, Post, Comment,
        Follow корректно работает __str__.'''
        cases = {
            self.group: self.group.title,
            self.post: INFO_ABOUT_POST.format(
                text=self.post.text,
                author=self.post.author.username,
                group=self.post.group.title
            ),
            self.comment: COMMENT.format(
                text=self.comment.text,
                author=self.comment.author.username,
            ),
            self.subscription: SUBSCRIPTION.format(
                user=self.authorized_user.username,
                author=self.author_of_post.username,
            ),
        }
        for field, expected_object_name in cases.items():
            with self.subTest(field=type(self).__name__):
                self.assertEqual(expected_object_name, str(field))

    def test_group_verbose_name(self):
        """verbose_name класса Group в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_verbose_name(self):
        """verbose_name класса Post в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value)

    def test_comment_verbose_name(self):
        """verbose_name класса Comment в полях совпадает с ожидаемым."""
        field_verboses = {
            'post': 'Комментируемый пост',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_follow_verbose_name(self):
        """verbose_name класса Follow в полях совпадает с ожидаемым."""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """help_text в классе Post в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)
