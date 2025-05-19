from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from routes.models import Route, Point
from images.models import Image
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


class RouteAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        self.image = Image.objects.create(
            id=1,
            name="Test image description",
            author=self.user,
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            is_public=True
        )

        self.route = Route.objects.create(id=1, name="Test Route", author=self.user, image=self.image)
        self.pointA = Point.objects.create(id=1, lat=12, lon=16, route=self.route, order=1)
        self.pointB = Point.objects.create(id=2, lat=22, lon=26, route=self.route, order=2)

        self.other_route = Route.objects.create(
            id=2,
            name="Other Route",
            author=self.other_user,
            image=self.image
        )

        self.points_data = [
            {"id": self.pointA.id, "lat": self.pointA.lat, "lon": self.pointA.lon, "order": self.pointA.order},
            {"id": self.pointB.id, "lat": self.pointB.lat, "lon": self.pointB.lon, "order": self.pointB.order},
        ]

        self.route_data = {
            "id": self.route.id,
            "name": self.route.name,
            "image": {
                "id": self.image.id,
                "name": self.image.name,
                "url": self.image.image.url,
                "is_public": self.image.is_public,
                'width': self.image.image.width,
                'height': self.image.image.height,
            },
            "author": {
                "username": self.user.username,
            },
            "points": self.points_data,
        }

        self.route_url = f"/api/routes/{self.route.id}/"
        self.other_route_url = f"/api/routes/{self.other_route.id}/"
        self.nonexistent_route_url = "/api/routes/999/"

    def test_get_route_details_as_author_success(self):
        self.client.force_login(self.user)
        response = self.client.get(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.route_data)

    def test_get_route_details_as_other_user_success(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.route_data)

    def test_get_route_details_not_found(self):
        self.client.force_login(self.user)
        response = self.client.get(self.nonexistent_route_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Route not found")

    def test_get_route_details_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_route_success(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())

    def test_delete_route_not_found(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.nonexistent_route_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Route not found")

    @patch('routes.models.Route.can_modify')
    def test_delete_route_permission_denied(self, mock_can_modify):
        mock_can_modify.return_value = False
        self.client.force_login(self.user)

        response = self.client.delete(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "You do not have permission to modify this route")
        self.assertTrue(Route.objects.filter(id=self.route.id).exists())

    def test_delete_other_user_route(self):
        self.client.force_login(self.other_user)
        response = self.client.delete(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Route.objects.filter(id=self.route.id).exists())

    def test_delete_route_unauthorized(self):
        self.client.logout()
        response = self.client.delete(self.route_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Route.objects.filter(id=self.route.id).exists())