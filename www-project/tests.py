import os
from unittest.mock import patch, mock_open
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from images.models import Image

@override_settings(MEDIA_ROOT='/tmp/test_media/')
class ProtectedMediaTests(TestCase):
    def setUp(self):
        super().setUp()
        self.author = User.objects.create_user(username='author', password='12345')
        self.other_user = User.objects.create_user(username='other_user', password='12345')

        # Create images
        self.public_image = Image.objects.create(
            name='Public Image',
            image='public_image.jpg',
            author=self.author,
            is_public=True
        )
        self.private_image = Image.objects.create(
            name='Private Image',
            image='private_image.jpg',
            author=self.author,
            is_public=False
        )

    @patch('builtins.open', new_callable=mock_open, read_data='file_content')
    @patch('os.path.exists', return_value=True)
    def test_access_public_image(self, mock_exists, mock_file):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('protected_media', args=['public_image.jpg']))
        self.assertEqual(response.status_code, 200)
        mock_file.assert_called_once_with('/tmp/test_media/public_image.jpg', 'rb')

    @patch('builtins.open', new_callable=mock_open, read_data='file_content')
    @patch('os.path.exists', return_value=True)
    def test_access_private_image_as_author(self, mock_exists, mock_file):
        self.client.force_login(self.author)
        response = self.client.get(reverse('protected_media', args=['private_image.jpg']))
        self.assertEqual(response.status_code, 200)
        mock_file.assert_called_once_with('/tmp/test_media/private_image.jpg', 'rb')

    @patch('os.path.exists', return_value=True)
    def test_access_private_image_as_other_user(self, mock_exists):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('protected_media', args=['private_image.jpg']))
        self.assertEqual(response.status_code, 404)

    @patch('os.path.exists', return_value=False)
    def test_access_non_existent_image(self, mock_exists):
        self.client.force_login(self.author)
        response = self.client.get(reverse('protected_media', args=['non_existent.jpg']))
        self.assertEqual(response.status_code, 404)

    @patch('os.path.exists', return_value=False)
    def test_redirect_on_non_existing_image(self, mock_exists):
        self.client.logout()
        response = self.client.get(reverse('protected_media', args=['non_existent.jpg']))
        self.assertEqual(response.status_code, 302)

    @patch('os.path.exists', return_value=True)
    def test_redirect_on_public_image(self, mock_exists):
        response = self.client.get(reverse('protected_media', args=['public_image.jpg']))
        self.assertEqual(response.status_code, 302)

    @patch('os.path.exists', return_value=True)
    def test_redirect_on_private_image(self, mock_exists):
        response = self.client.get(reverse('protected_media', args=['private_image.jpg']))
        self.assertEqual(response.status_code, 302)