from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='test_user',
            email='test@gmail.com',
            password='test_pass'
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            text='Тестовая запись нового поста',
        )
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug',
            description='группа для нового поста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.test_user)

    def test_available_urls_guest(self):
        urls_name = (
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/posts/{PostsURLTests.post.id}/',
            f'/profile/{PostsURLTests.test_user}/',
        )
        for url in urls_name:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_urls_user(self):
        urls_name = (
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/posts/{PostsURLTests.post.id}/',
            f'/profile/{PostsURLTests.test_user}/',
            f'/posts/{PostsURLTests.post.id}/edit/',
            '/create/',
        )
        for url in urls_name:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_login_and_private_url(self):
        urls_name = (
            f'/posts/{PostsURLTests.post.id}/edit/',
            '/create/',
        )
        for url in urls_name:
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    ('/auth/login/?next=' + url)
                )
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template_client(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostsURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostsURLTests.test_user}/': 'posts/profile.html',
            f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostsURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/posts/true/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
