from django.test import TestCase
from django.urls import reverse

from .. import urls

POST_ID = 1
SLUG = 'test_slug'
USERNAME = 'test_author'
ROUTES = [
    ['/', 'index', None],
    ['/create/', 'post_create', None],
    ['/follow/', 'follow_index', None],
    [f'/group/{SLUG}/', 'group_list', [SLUG]],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
    [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
]


class PostsRouteTests(TestCase):
    def test_routes(self):
        for url, route, params in ROUTES:
            with self.subTest(route=route, params=params):
                self.assertEqual(url, reverse(f'{urls.app_name}:{route}',
                                              args=params))
