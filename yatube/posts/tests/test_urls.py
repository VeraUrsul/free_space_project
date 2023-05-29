from http import client

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

SLUG = 'test_slug'
USERNAME = 'test-author'
USERNAME_2 = 'authorized_user'
FOLLOW_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
LOGIN_NEW_POST_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
LOGIN_FOLLOW_URL = f'{LOGIN_URL}?next={FOLLOW_URL}'
LOGIN_PROFILE_FOLLOW_URL = f'{LOGIN_URL}?next={PROFILE_FOLLOW_URL}'
LOGIN_PROFILE_UNFOLLOW_URL = f'{LOGIN_URL}?next={PROFILE_UNFOLLOW_URL}'
UNEXISTING_URL = '/unexisting_page/'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_of_post = User.objects.create_user(USERNAME)
        cls.authorized_user = User.objects.create_user(USERNAME_2)
        cls.group = Group.objects.create(
            description='Тестовое описание группы.',
            slug=SLUG,
            title='Тестовое название',
        )
        cls.post = Post.objects.create(
            author=cls.author_of_post,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.LOGIN_POST_EDIT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.authorized_user)
        cls.author = Client()
        cls.author.force_login(cls.author_of_post)

    def test_urls_exists_at_desired_location(self):
        """Страницы приложения доступные пользователю."""
        cases = [
            [FOLLOW_URL, self.another, client.OK],
            [FOLLOW_URL, self.guest, client.FOUND],
            [MAIN_URL, self.guest, client.OK],
            [NEW_POST_URL, self.another, client.OK],
            [NEW_POST_URL, self.guest, client.FOUND],
            [UNEXISTING_URL, self.guest, client.NOT_FOUND],
            [GROUP_URL, self.guest, client.OK],
            [PROFILE_URL, self.guest, client.OK],
            [PROFILE_FOLLOW_URL, self.another, client.FOUND],
            [PROFILE_FOLLOW_URL, self.author, client.FOUND],
            [PROFILE_FOLLOW_URL, self.guest, client.FOUND],
            [PROFILE_UNFOLLOW_URL, self.author, client.NOT_FOUND],
            [PROFILE_UNFOLLOW_URL, self.another, client.FOUND],
            [PROFILE_UNFOLLOW_URL, self.guest, client.FOUND],
            [self.POST_DETAIL_URL, self.guest, client.OK],
            [self.POST_EDIT_URL, self.author, client.OK],
            [self.POST_EDIT_URL, self.another, client.FOUND],
            [self.POST_EDIT_URL, self.guest, client.FOUND],
        ]
        for url, visitor, code in cases:
            with self.subTest(url=url, visitor=visitor, code=code):
                self.assertEqual(visitor.get(url).status_code, code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cases = [
            [FOLLOW_URL, self.another, 'posts/follow.html'],
            [MAIN_URL, self.guest, 'posts/index.html'],
            [NEW_POST_URL, self.another, 'posts/create_post.html'],
            [GROUP_URL, self.guest, 'posts/group_list.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'posts/post_detail.html'],
            [self.POST_EDIT_URL, self.author, 'posts/create_post.html'],
            [UNEXISTING_URL, self.guest, 'core/404.html'],
        ]
        for url, user, template in cases:
            with self.subTest(url=url):
                self.assertTemplateUsed(user.get(url), template)

    def test_redirect_create_post_edit_post_post_detail(self):
        """Перенаправление пользователей со
        страниц создания и редактирования поста, детали поста
        """
        cases = [
            [FOLLOW_URL, self.guest, LOGIN_FOLLOW_URL],
            [NEW_POST_URL, self.guest, LOGIN_NEW_POST_URL],
            [PROFILE_FOLLOW_URL, self.guest, LOGIN_PROFILE_FOLLOW_URL],
            [PROFILE_FOLLOW_URL, self.another, FOLLOW_URL],
            [PROFILE_FOLLOW_URL, self.author, FOLLOW_URL],
            [PROFILE_UNFOLLOW_URL, self.guest, LOGIN_PROFILE_UNFOLLOW_URL],
            [PROFILE_UNFOLLOW_URL, self.another, FOLLOW_URL],
            [self.POST_EDIT_URL, self.guest, self.LOGIN_POST_EDIT_URL],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
        ]
        for url, visitor, end_url in cases:
            with self.subTest(url=url, visitor=visitor, end_url=end_url):
                self.assertRedirects(visitor.get(url, follow=True),
                                     end_url)
