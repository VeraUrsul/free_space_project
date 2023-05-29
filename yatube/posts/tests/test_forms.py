import shutil
import tempfile
from http import client

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Comment, Group, Post, User

SLUG = 'test_slug'
USERNAME = 'test-author'
USERNAME_2 = 'authorized_user'
LOGIN_URL = reverse('users:login')
MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
LOGIN_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_URL_2 = reverse('posts:profile', args=[USERNAME_2])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF_1 = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3A'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_of_post = User.objects.create_user(USERNAME)
        cls.authorized_user = User.objects.create_user(USERNAME_2)
        cls.edited_group = Group.objects.create(
            description='Описание тестовой группы для редактирования поста',
            slug='test_edit_slug',
            title='Тестовая группа для редактирования поста'
        )
        cls.group = Group.objects.create(
            description='Тестовое описание группы.',
            slug=SLUG,
            title='Тестовое название',
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=SMALL_GIF_1,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author_of_post,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded_2,
        )
        cls.form = PostForm()
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.LOGIN_POST_EDIT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.pk])
        cls.LOGIN_COMMENT_URL = f'{LOGIN_URL}?next={cls.COMMENT_URL}'
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.authorized_user)
        cls.author = Client()
        cls.author.force_login(cls.author_of_post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_user_create_post(self):
        '''Авторизованный пользователь создает запись в Post.'''
        posts_before = set(Post.objects.all())
        uploaded_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=SMALL_GIF_1,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Текст нового поста',
            'image': uploaded_1,
        }
        response = self.another.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        posts = set(Post.objects.all()).difference(posts_before)
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(self.authorized_user, post.author)
        self.assertEqual(form_data['group'], post.group.id)
        self.assertEqual(
            post.image.name,
            f'{settings.IMAGE_PLACEMENT}{uploaded_1.name}'
        )
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(response.status_code, client.OK)
        self.assertRedirects(response, PROFILE_URL_2)

    def test_guest_create_post(self):
        '''Неавторизованный пользователь не может создать пост,
        он перенаправляется на страницу авторизации.'''
        posts_before = set(Post.objects.all())
        self.assertRedirects(self.guest.post(NEW_POST_URL), LOGIN_NEW_POST_URL)
        posts = set(Post.objects.all()).difference(posts_before)
        self.assertEqual(len(posts), 0)

    def test_author_post_edit_form(self):
        '''Автор редактирует запись в Post.'''
        uploaded_3 = SimpleUploadedFile(
            name='small_3.gif',
            content=SMALL_GIF_1,
            content_type='image/gif'
        )
        form_data = {
            'group': self.edited_group.id,
            'text': 'Отредактированный текст поста',
            'image': uploaded_3,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(self.post.author, post.author)
        self.assertEqual(form_data['group'], post.group.id)
        self.assertEqual(
            post.image.name,
            f'{settings.IMAGE_PLACEMENT}{uploaded_3.name}'
        )
        self.assertEqual(form_data['text'], post.text)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_authorized_user_guest_edit_post(self):
        '''Любой пользователь, кроме автора, не может отредактировать пост,
        он перенаправляется на страницу просмотра поста.'''
        cases = [
            [self.guest, self.LOGIN_POST_EDIT_URL],
            [self.another, self.POST_DETAIL_URL],
        ]
        for visitor, url in cases:
            with self.subTest(visitor=visitor, url=url):
                self.assertRedirects(visitor.get(self.POST_EDIT_URL), url)
                post = Post.objects.get(id=self.post.id)
                self.assertEqual(self.post.author, post.author)
                self.assertEqual(self.post.group.id, post.group.id)
                self.assertEqual(self.post.image.name, post.image.name)
                self.assertEqual(self.post.text, post.text)

    def test_post_edit_page_show_correct_context(self):
        """Проверка контекста шаблонов create_post и post_edit."""
        form_fields = {
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
            'group': forms.fields.ChoiceField,
        }
        cases = [
            NEW_POST_URL,
            self.POST_EDIT_URL,
        ]
        for url in cases:
            response = self.author.get(url)
            result_form = response.context.get('form').fields
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = result_form.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_correct_context_of_comment_form_on_post_detail(self):
        """Проверка контекста формы комментария на странице поста"""
        form_fields = {'text': forms.fields.CharField}
        response = self.another.get(self.POST_DETAIL_URL)
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])

    def test_guest_creating_new_comment(self):
        '''Неавторизованный пользователь не может создать комментарий,
        он перенаправляется на страницу авторизации.'''
        comments_before = set(Comment.objects.all())
        self.assertRedirects(self.guest.post(self.COMMENT_URL),
                             self.LOGIN_COMMENT_URL)
        comments = set(Comment.objects.all()).difference(comments_before)
        self.assertEqual(len(comments), 0)

    def test_authorized_user_creating_new_comment(self):
        '''Создание комментария авторизованным пользователем.'''
        comments_before = set(Comment.objects.all())
        form_data = {'text': 'Текст комментария'}
        self.another.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        comments = set(Comment.objects.all()) - comments_before
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(self.post, comment.post)
        self.assertEqual(self.authorized_user, comment.author)
