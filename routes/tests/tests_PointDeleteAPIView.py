from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from routes.models import Route, Point
from images.models import Image
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

class PointDeleteAPIViewTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test image
        self.image = Image.objects.create(
            name="Test Image",
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.user,
            is_public=True
        )

        # Create test route
        self.route = Route.objects.create(
            name="Test Route",
            image=self.image,
            author=self.user
        )

        # Create test point
        self.point = Point.objects.create(
            route=self.route,
            lat=10,
            lon=20,
            order=1
        )

        # Create route owned by other user
        self.other_route = Route.objects.create(
            name="Other Route",
            image=self.image,
            author=self.other_user
        )

        # Create point in other route
        self.other_point = Point.objects.create(
            route=self.other_route,
            lat=15,
            lon=25,
            order=1
        )

        # URLs for testing
        self.url = reverse('api_point_delete', kwargs={'route_id': self.route.id, 'point_id': self.point.id})
        self.other_url = reverse('api_point_delete', kwargs={'route_id': self.other_route.id, 'point_id': self.other_point.id})

    def test_delete_point_success(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Point.objects.filter(id=self.point.id).exists())

    def test_delete_point_route_not_found(self):
        url = reverse('api_point_delete', kwargs={'route_id': 9999, 'point_id': self.point.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Route not found"})
        self.assertTrue(Point.objects.filter(id=self.point.id).exists())

    def test_delete_point_not_found(self):
        url = reverse('api_point_delete', kwargs={'route_id': self.route.id, 'point_id': 9999})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Point not found"})

    @patch('routes.models.Route.can_modify')
    def test_delete_point_permission_denied(self, mock_can_modify):
        mock_can_modify.return_value = False

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error": "You do not have permission to modify this route"})
        self.assertTrue(Point.objects.filter(id=self.point.id).exists())