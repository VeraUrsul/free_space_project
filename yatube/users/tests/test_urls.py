from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import User

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ROUTES = [
            {
                'url': '/auth/signup/',
                'template': 'users/signup.html',
            },
            {
                'url': '/auth/logout/',
                'template': 'users/logged_out.html',
                'need_auth': True,
            },
            {
                'url': '/auth/login/',
                'template': 'users/login.html',
                'need_auth': True,
            },
            {
                'url': '/auth/password_reset/',
                'template': 'users/password_reset_form.html',
                'need_auth': True,
            },
            {
                'url': '/auth/password_reset/done/',
                'template': 'users/password_reset_done.html',
                'need_auth': True,
            },
            {
                'url': '/auth/reset/<uidb64>/<token>/',
                'template': 'users/password_reset_confirm.html',
                'need_auth': True,
            },
            {
                'url': '/auth/reset/done/',
                'template': 'users/password_reset_complete.html',
                'need_auth': True,
            },
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = User.objects.create_user(
            username='authorized_user'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)

    def test_urls_exists_at_desired_location(self):
        """Страницы приложения users доступные пользователю."""
        for route in self.ROUTES:
            with self.subTest(url=route['url']):
                if route.get('need_auth'):
                    current_client = self.authorized_client
                else:
                    current_client = self.guest_client
                response = current_client.get(route['url'])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url_(self):
        """Страница /unexisting_page/ недоступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for route in self.ROUTES:
            with self.subTest(url=route['url'], template=route['template']):
                if route.get('need_auth'):
                    current_client = self.authorized_client
                else:
                    current_client = self.guest_client
                response = current_client.get(route['url'])
                self.assertTemplateUsed(response, route['template'])
