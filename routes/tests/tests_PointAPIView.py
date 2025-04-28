from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from routes.models import Route, Point
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class PointAPIViewTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        # Setup API client and authenticate
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
        self.url = reverse('api_point_detail', kwargs={'route_id': self.route.id, 'point_id': self.point.id})
        self.other_url = reverse('api_point_detail',
                                 kwargs={'route_id': self.other_route.id, 'point_id': self.other_point.id})

    def test_get_point_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lat'], self.point.lat)
        self.assertEqual(response.data['lon'], self.point.lon)
        self.assertEqual(response.data['order'], self.point.order)

    def test_get_point_from_other_user_route(self):
        response = self.client.get(self.other_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lat'], self.other_point.lat)
        self.assertEqual(response.data['lon'], self.other_point.lon)

    def test_get_point_route_not_found(self):
        url = reverse('api_point_detail', kwargs={'route_id': 9999, 'point_id': self.point.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Route not found"})

    def test_get_point_not_found(self):
        url = reverse('api_point_detail', kwargs={'route_id': self.route.id, 'point_id': 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Point not found"})