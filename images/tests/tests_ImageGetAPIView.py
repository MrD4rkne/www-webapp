from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from images.models import Image
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import path, include

class ImageViewTests(APITestCase):
    urlpatterns = [
        path('api/images', include('images.api_urls')),
    ]


    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # Create a user
        self.author = User.objects.create_user(username='testuser', password='12345')
        self.user = User.objects.create_user(username='testuser2', password='12345')

        # Create an image
        self.public_image = Image.objects.create(
            name='Test Image',
            image='path/to/image.jpg',
            author=self.author,
            is_public=True
        )

        self.expected_public_image_data = {
            'id': self.public_image.id,
            'name': self.public_image.name,
            'url': self.public_image.image.url,
            'author':{
                'username': self.author.username
            },
            'is_public': True
        }

        self.private_image = Image.objects.create(
            name='Private Image',
            image='path/to/private_image.jpg',
            author=self.author,
            is_public=False
        )

        self.expected_private_image_data = {
            'id': self.private_image.id,
            'name': self.private_image.name,
            'url': self.private_image.image.url,
            'author':{
                'username': self.author.username
            },
            'is_public': False
        }

    def test_get_public_image_as_anonymous_user(self):
        self.client.logout()

        response = self.client.get(f'/api/images/{self.public_image.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_public_image_data)

    def test_get_public_image_as_author_user(self):
        self.client.force_login(self.author)

        response = self.client.get(f'/api/images/{self.public_image.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_public_image_data)

    def test_get_public_image_as_other_user(self):
        self.client.force_login(self.user)

        response = self.client.get(f'/api/images/{self.public_image.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_public_image_data)

    def test_get_private_image_as_anonymous_user(self):
        self.client.logout()

        response = self.client.get(f'/api/images/{self.private_image.id}')

        self.assertEqual(response.status_code, 404)

    def test_get_private_image_as_author_user(self):
        self.client.force_login(self.author)

        response = self.client.get(f'/api/images/{self.private_image.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_private_image_data)

    def test_get_private_image_as_other_user(self):
        self.client.force_login(self.user)

        response = self.client.get(f'/api/images/{self.private_image.id}')

        self.assertEqual(response.status_code, 404)