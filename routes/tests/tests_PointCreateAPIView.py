from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from routes.models import Route, Point
from images.models import Image
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


class PointCreateAPIViewTests(TestCase):
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

        # URL for testing
        self.url = reverse('api_point_create', kwargs={'route_id': self.route.id})

        # Valid point data
        self.valid_point_data = {
            'lat': 10,
            'lon': 20
        }

    @patch('images.models.Image.are_valid_coordinates')
    def test_create_point_success(self, mock_are_valid_coordinates):
        mock_are_valid_coordinates.return_value = True

        response = self.client.post(self.url, self.valid_point_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Point.objects.count(), 1)

        point = Point.objects.first()
        self.assertEqual(point.lat, self.valid_point_data['lat'])
        self.assertEqual(point.lon, self.valid_point_data['lon'])
        self.assertEqual(point.route, self.route)
        self.assertEqual(point.order, 1)

    def test_create_point_route_not_found(self):
        url = reverse('api_point_create', kwargs={'route_id': 9999})

        response = self.client.post(url, self.valid_point_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Route not found"})
        self.assertEqual(Point.objects.count(), 0)

    def test_create_point_invalid_data(self):
        invalid_data = {'lat': 10}  # Missing 'lon'

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('lon', response.data)
        self.assertEqual(Point.objects.count(), 0)

    @patch('routes.models.Route.can_modify')
    @patch('images.models.Image.are_valid_coordinates')
    def test_create_point_permission_denied(self, mock_are_valid_coordinates, mock_can_modify):
        mock_are_valid_coordinates.return_value = True
        mock_can_modify.return_value = False

        response = self.client.post(self.url, self.valid_point_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error": "You do not have permission to modify this route"})
        self.assertEqual(Point.objects.count(), 0)

    @patch('images.models.Image.are_valid_coordinates')
    def test_create_point_invalid_coordinates(self, mock_are_valid_coordinates):
        mock_are_valid_coordinates.return_value = False

        response = self.client.post(self.url, self.valid_point_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid coordinates"})
        self.assertEqual(Point.objects.count(), 0)

    @patch('images.models.Image.are_valid_coordinates')
    def test_create_point_order_incrementation(self, mock_are_valid_coordinates):
        mock_are_valid_coordinates.return_value = True

        # Create existing point
        Point.objects.create(
            route=self.route,
            lat=5,
            lon=5,
            order=1
        )

        response = self.client.post(self.url, self.valid_point_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Point.objects.count(), 2)

        new_point = Point.objects.get(lat=self.valid_point_data['lat'], lon=self.valid_point_data['lon'])
        self.assertEqual(new_point.order, 2)