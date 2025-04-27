from django.test import TestCase
from django.contrib.auth.models import User
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        # Create a test image
        self.image = Image.objects.create(
            name="Test Image",
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.user,
            is_public=True
        )

    def test_image_creation(self):
        # Test that the image is created correctly
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(self.image.name, "Test Image")
        self.assertEqual(self.image.author, self.user)
        self.assertTrue(self.image.is_public)

    def test_can_access_public_image(self):
        # Test that a public image can be accessed by any user
        self.assertTrue(self.image.can_access(self.user))
        self.assertTrue(self.image.can_access(self.other_user))

    def test_can_access_private_image(self):
        # Test that a private image can only be accessed by its author
        self.image.is_public = False
        self.image.save()
        self.assertTrue(self.image.can_access(self.user))
        self.assertFalse(self.image.can_access(self.other_user))

    def test_are_valid_coordinates(self):
        # Test the coordinate validation logic
        from unittest.mock import patch, PropertyMock

        with patch.object(type(self.image.image), "width", new_callable=PropertyMock) as mock_width, \
             patch.object(type(self.image.image), "height", new_callable=PropertyMock) as mock_height:
            mock_width.return_value = 100
            mock_height.return_value = 50
        self.assertTrue(self.image.are_valid_coordinates(10, 20))
        self.assertFalse(self.image.are_valid_coordinates(110, 20))
        self.assertFalse(self.image.are_valid_coordinates(10, 60))