import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

SLUG = 'test_slug'
SLUG_2 = 'test_slug_2'
USERNAME = 'test-author'
USERNAME_2 = 'authorized_user'
FOLLOW_URL = reverse('posts:follow_index')
MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_2_URL = reverse('posts:group_list', args=[SLUG_2])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_FOLLOW = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW = reverse('posts:profile_unfollow', args=[USERNAME])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
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
        cls.group_2 = Group.objects.create(
            description='Тестовое описание группы 2.',
            slug=SLUG_2,
            title='Тестовая группа 2',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author_of_post,
            group=cls.group,
            image=cls.uploaded,
            text='Тестовый пост',
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.authorized_user)
        cls.author = Client()
        cls.author.force_login(cls.author_of_post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_context_check_index_group_list_profile_post_detail(self):
        """Проверка правильности контекста index,
           group_list, profile, post_detail"""
        Follow.objects.get_or_create(user=self.authorized_user,
                                     author=self.post.author)
        cases = [
            [FOLLOW_URL, 'page_obj'],
            [MAIN_URL, 'page_obj'],
            [GROUP_URL, 'page_obj'],
            [PROFILE_URL, 'page_obj'],
            [self.POST_DETAIL_URL, 'post']
        ]
        for url, context in cases:
            with self.subTest(url=url):
                response = self.another.get(url)
                if context == 'page_obj':
                    self.assertEqual(len(response.context[context]), 1)
                    post = response.context[context][0]
                else:
                    post = response.context.get('post')
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.image, self.post.image)
                self.assertEqual(post.id, self.post.id)

    def test_post_not_added_in_another_group_(self):
        """Пост не добавляется в другую группу/ленту"""
        cases = [
            [GROUP_2_URL, self.another],
            [FOLLOW_URL, self.author]
        ]
        for url, visitor in cases:
            with self.subTest(url=url):
                Follow.objects.get_or_create(user=self.authorized_user,
                                             author=self.post.author)
                self.assertNotIn(
                    self.post,
                    visitor.get(url).context['page_obj']
                )

    def test_author_in_profile_page_context(self):
        """Автор в контексте профиля"""
        self.assertEqual(
            self.another.get(PROFILE_URL).context['author'],
            self.author_of_post
        )

    def test_group_in_group_list_context(self):
        """Группа в контексте Групп-ленты без искажения атрибутов"""
        group = self.another.get(GROUP_URL).context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.id, self.group.id)

    def test_checking_cache(self):
        '''Проверка кеша'''
        cache_before = self.guest.get(MAIN_URL).content
        Post.objects.all().delete()
        cache_after = self.guest.get(MAIN_URL).content
        self.assertEqual(cache_before, cache_after)
        cache.clear()
        cache_new = self.guest.get(MAIN_URL).content
        self.assertNotEqual(cache_before, cache_new)

    def test_adding_subscription(self):
        '''Добавление подписки'''
        self.another.get(PROFILE_FOLLOW)
        self.assertTrue(
            Follow.objects.get(
                user=self.authorized_user, author=self.post.author
            )
        )

    def test_removing_subscription(self):
        '''Удаление подписки'''
        Follow.objects.create(user=self.authorized_user,
                              author=self.post.author)
        self.another.get(PROFILE_UNFOLLOW)
        self.assertFalse(
            Follow.objects.filter(
                user=self.authorized_user, author=self.post.author
            ).exists()
        )

    def test_checking_number_of_posts_per_page(self):
        '''Проверка количества постов на странице'''
        Post.objects.all().delete()
        posts_on_last_page = 1
        posts_num = settings.NUMB_POSTS_PAGE + posts_on_last_page
        Post.objects.bulk_create(
            Post(
                author=self.author_of_post,
                group=self.group,
                text=f'Текст поста №{i+1}'
            ) for i in range(posts_num)
        )
        Follow.objects.create(user=self.authorized_user,
                              author=self.author_of_post)
        cases = [
            [FOLLOW_URL, settings.NUMB_POSTS_PAGE],
            [f'{FOLLOW_URL}?page=2', posts_on_last_page],
            [MAIN_URL, settings.NUMB_POSTS_PAGE],
            [f'{MAIN_URL}?page=2', posts_on_last_page],
            [GROUP_URL, settings.NUMB_POSTS_PAGE],
            [f'{GROUP_URL}?page=2', posts_on_last_page],
            [PROFILE_URL, settings.NUMB_POSTS_PAGE],
            [f'{PROFILE_URL}?page=2', posts_on_last_page],
        ]
        for url, expected_count in cases:
            with self.subTest(url=url, expected_count=expected_count):
                self.assertEqual(
                    len(self.another.get(url).context['page_obj']),
                    expected_count
                )
