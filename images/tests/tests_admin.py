from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from images.admin import ImageAdmin
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class MockRequest:
    def __init__(self, user=None):
        self.user = user


class ImageAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ImageAdmin(Image, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.factory = RequestFactory()
        self.image_data = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_exclude_author_field(self):
        self.assertIn('author', self.admin.exclude)

    def test_save_new_image_sets_author(self):
        request = MockRequest(user=self.user)
        obj = Image(name="Test Image", image=self.image_data)

        class MockForm:
            def __init__(self):
                self.cleaned_data = {}

        form = MockForm()

        self.admin.save_model(request, obj, form, False)

        self.assertEqual(obj.author, self.user)

    def test_update_existing_image_preserves_author(self):
        other_user = User.objects.create_user(username="otheruser", password="password")
        existing_image = Image.objects.create(
            name="Existing Image",
            image=self.image_data,
            author=other_user
        )

        request = MockRequest(user=self.user)

        class MockForm:
            def __init__(self):
                self.cleaned_data = {}

        form = MockForm()

        self.admin.save_model(request, existing_image, form, True)

        self.assertEqual(existing_image.author, other_user)