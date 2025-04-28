from django.test import TestCase
from django.contrib.auth.models import User
from routes.models import Route, Point
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class RouteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        self.image = Image.objects.create(
            name="Test Image",
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.user,
            is_public=True
        )

        self.route = Route.objects.create(
            name="Test Route",
            image=self.image,
            author=self.user
        )

        self.point1 = Point.objects.create(
            route=self.route,
            lat=10,
            lon=20,
            order=1
        )

        self.point2 = Point.objects.create(
            route=self.route,
            lat=30,
            lon=40,
            order=2
        )

    def test_route_creation(self):
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(self.route.name, "Test Route")
        self.assertEqual(self.route.image, self.image)
        self.assertEqual(self.route.author, self.user)

    def test_can_modify(self):
        self.assertTrue(self.route.can_modify(self.user))
        self.assertFalse(self.route.can_modify(self.other_user))

    def test_get_points(self):
        points = self.route.get_points()
        self.assertEqual(points.count(), 2)
        self.assertIn(self.point1, points)
        self.assertIn(self.point2, points)

    def test_route_str(self):
        self.assertEqual(str(self.route), "Test Route")

    def test_route_point_relationship(self):
        self.assertEqual(self.route.points.count(), 2)
        self.assertEqual(self.point1.route, self.route)
        self.assertEqual(self.point2.route, self.route)


class PointModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.image = Image.objects.create(
            name="Test Image",
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            author=self.user,
            is_public=True
        )

        self.route = Route.objects.create(
            name="Test Route",
            image=self.image,
            author=self.user
        )

        self.point = Point.objects.create(
            route=self.route,
            lat=10,
            lon=20,
            order=1
        )

    def test_point_creation(self):
        self.assertEqual(Point.objects.count(), 1)
        self.assertEqual(self.point.lat, 10)
        self.assertEqual(self.point.lon, 20)
        self.assertEqual(self.point.order, 1)
        self.assertEqual(self.point.route, self.route)

    def test_point_str(self):
        self.assertEqual(str(self.point), "Point <10, 20: 1>")

    def test_point_ordering(self):
        point2 = Point.objects.create(
            route=self.route,
            lat=30,
            lon=40,
            order=0
        )

        points = list(Point.objects.filter(route=self.route))
        self.assertEqual(points[0], point2)
        self.assertEqual(points[1], self.point)