from django.test import TestCase
from django.contrib.auth.models import User
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from common.tests.helpers import ImageHelper

class ImageModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        # Create a test image
        self.image = Image.objects.create(
            name="Test Image",
            image=ImageHelper.get_image_file(name='test_image.jpg', ext='jpeg', size=(1920, 1080)),
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

    def test_are_valid_coordinates(self):
        # Test that the uploaded image has valid dimensions
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

