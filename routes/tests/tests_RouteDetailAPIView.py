from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from routes.models import Route, Point
from images.models import Image

class RouteDetailAPIViewTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="<PASSWORD>")
        self.client.login(username="testuser", password="testpassword")

        # Create a test route
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.image = Image.objects.create(
            id=1,
            name="Test image description",
            author=self.user,
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
        self.route = Route.objects.create(id=1, name="Test Route", author=self.user, image_id=1)
        self.pointA = Point.objects.create(id=1, lat=12, lon=16, route=self.route, order=1)
        self.pointB = Point.objects.create(id=2, lat=22, lon=26, route=self.route, order=2)

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
            },
            "author": {
                "username": self.user.username,
            },
            "points": self.points_data,
        }

    def test_get_route_details_as_author_success(self):
        # Test retrieving route details successfully
        self.client.force_login(self.user)
        response = self.client.get(f"/api/routes/{self.route.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.route_data)

    def test_get_route_details_as_not_author(self):
        # Test retrieving route details successfully
        self.client.force_login(self.other_user)
        response = self.client.get(f"/api/routes/{self.route.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Route not found")

    def test_get_route_details_not_found(self):
        # Test retrieving a non-existent route
        response = self.client.get("/api/routes/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Route not found")

    def test_get_route_details_unauthorized(self):
        # Test retrieving route details without authentication
        self.client.logout()
        response = self.client.get(f"/api/routes/{self.route.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)