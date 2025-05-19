from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from images.models import Image
from rest_framework.test import APIClient
from django.urls import path, include
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageListAPIViewTests(APITestCase):
    urlpatterns = [
        path('api/images/', include('images.api_urls')),
    ]

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # Create users
        self.author = User.objects.create_user(username='author', password='12345')
        self.other_user = User.objects.create_user(username='other_user', password='12345')

        # Create images
        self.public_image = Image.objects.create(
            name='Public Image',
            image=SimpleUploadedFile("path/to/public_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.author,
            is_public=True
        )

        self.public_image_data ={
            'id': self.public_image.id,
            'name': self.public_image.name,
            'url': self.public_image.image.url,
            'is_public': True,
            'width': self.public_image.image.width,
            'height': self.public_image.image.height,
        }

        self.private_image = Image.objects.create(
            name='Private Image',
            image=SimpleUploadedFile("path/to/private_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.author,
            is_public=False
        )

        self.private_image_data ={
            'id': self.private_image.id,
            'name': self.private_image.name,
            'url': self.private_image.image.url,
            'is_public': False,
            'width': self.private_image.image.width,
            'height': self.private_image.image.height,
        }

    def test_list_images_as_anonymous_user(self):
        self.client.logout()
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], self.public_image_data)

    def test_list_images_as_authenticated_user(self):
        self.client.force_login(self.author)
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        self.assertIn(self.public_image_data, response.data)
        self.assertIn(self.private_image_data, response.data)

    def test_list_images_as_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0], self.public_image_data)