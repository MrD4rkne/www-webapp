from django.test import TestCase
from django.contrib.auth.models import User
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.base import File

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

    def test__author__can_access_public_image(self):
        # Test that a public image can be accessed by any user
        self.assertTrue(self.image.can_access(self.user))
        self.assertTrue(self.image.can_access(self.other_user))

    def test_can_access_private_image(self):
        # Test that a private image can only be accessed by its author
        self.image.is_public = False
        self.image.save()
        self.assertTrue(self.image.can_access(self.user))
        self.assertFalse(self.image.can_access(self.other_user))

    @staticmethod
    def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = PILImage.new("RGB", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def test_are_valid_coordinates(self):
        # Test that the uploaded image has valid dimensions
        self.image.image = self.get_image_file(name='test_image.jpg', ext='jpeg', size=(1920, 1080))
        self.image.save()

        self.assertEqual(self.image.image.width, 1920)
        self.assertEqual(self.image.image.height, 1080)

        self.assertTrue(self.image.are_valid_coordinates(0,0))
        self.assertTrue(self.image.are_valid_coordinates(10, 5))
        self.assertTrue(self.image.are_valid_coordinates(1920, 1080))

        self.assertFalse(self.image.are_valid_coordinates(1080, 1920))
        self.assertFalse(self.image.are_valid_coordinates(1921, 1080))
        self.assertFalse(self.image.are_valid_coordinates(1920, 1081))
        self.assertFalse(self.image.are_valid_coordinates(-1, 0))
        self.assertFalse(self.image.are_valid_coordinates(0, -1))
        self.assertFalse(self.image.are_valid_coordinates(1920, -1))
        self.assertFalse(self.image.are_valid_coordinates(-1, 1080))
        self.assertFalse(self.image.are_valid_coordinates(-1, -1))

