import uuid

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.test_user = User.objects.create_user(
            username='test_user',
            email='test@gmail.com',
            password='test_pass'
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            text='Тестовая запись нового поста',
            group=Group.objects.create(
                title='Заголовок для тестовой группы',
                slug='test_slug',
                description='группа для нового поста',
            ),
            image=uploaded
        )
        cls.post_2 = Post.objects.create(
            author=cls.test_user,
            text='Тестовая запись нового поста 2',
            group=Group.objects.create(
                title='Заголовок для тестовой группы 2',
                slug='test_slug2',
                description='группа для нового поста 2',
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTest.test_user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.post.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args={PostViewsTest.test_user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args={PostViewsTest.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                args={PostViewsTest.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][-1]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0,
                         PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.test_user.username)
        self.assertEqual(post_group_0, PostViewsTest.post.group.title)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_group_pages_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.post.group.slug}
            )
        )
        group_objects = response.context['group']
        first_object = response.context['page_obj'][0]
        group_title_0 = group_objects.title
        group_slug_0 = group_objects.slug
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(group_title_0, PostViewsTest.post.group.title)
        self.assertEqual(group_slug_0, PostViewsTest.post.group.slug)
        self.assertEqual(post_text_0,
                         PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.test_user.username)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_profile_pages_show_correct_contexr(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                args={PostViewsTest.test_user}
            )
        )
        first_object = response.context['page_obj'][-1]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0,
                         PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.test_user.username)
        self.assertEqual(post_group_0, PostViewsTest.post.group.title)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_post_detail_pages_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                args={PostViewsTest.post.id}
            )
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0,
                         PostViewsTest.post.text)
        self.assertEqual(post_author_0, PostViewsTest.test_user.username)
        self.assertEqual(post_group_0, PostViewsTest.post.group.title)
        self.assertEqual(post_image_0, PostViewsTest.post.image)

    def test_post_edit_pages_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                args={PostViewsTest.post.id}
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_pages_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_post_appear_at(self):
        form_data = {
            'text': f'тестовая запись нового поста {uuid.uuid4()}',
            'group': self.post.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        template_url = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}))
        new_post = Post.objects.get(text=form_data.get('text'))
        self.assertTrue(new_post.group, self.post.group)
        response_another_group = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post_2.group.slug}
            )
        )
        self.assertNotIn(
            new_post,
            response_another_group.context['page_obj'].object_list)
        for url in template_url:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(
                    new_post,
                    response.context['page_obj'].object_list)

    def test_add_comment(self):
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            form_data,
            follow=True
        )
        self.assertContains(response, form_data['text'])
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            form_data,
            follow=True)
        self.assertNotContains(response_guest, form_data['text'])

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.test_user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='test_user',
            email='test@gmail.ru',
            password='test_pass',
        )
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug',
            description='группа для нового поста'
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.test_user,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.test_user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse('posts:index'): 'index',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): 'group',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.test_user}
            ): 'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 10
            )

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse('posts:index') + '?page=2': 'index',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2': 'group',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.test_user}
            ) + '?page=2': 'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3
            )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='follower',
            email='test_11@mail.ru',
            password='test_pass'
        )
        cls.user_following = User.objects.create_user(
            username='following',
            email='test22@mail.ru',
            password='test_pass'
        )
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовая запись для тестирования ленты'
        )

    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)
        follow_up = Follow.objects.first()
        self.assertEqual(follow_up.user, self.user_follower)
        self.assertEqual(follow_up.author, self.user_following)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_follower,
                author=self.user_following
            ).exists()
        )

    def test_unfollow(self):
        Follow.objects.get_or_create(
            user=self.user_follower,
            author=self.user_following
        )
        self.client_auth_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_auth_follower.get(
            reverse(
                'posts:follow_index'
            )
        )
        post_text_0 = response.context['page_obj'][0].text
        self.assertEqual(post_text_0, self.post.text)
        response = self.client_auth_following.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertNotContains(
            response,
            self.post.text
        )
