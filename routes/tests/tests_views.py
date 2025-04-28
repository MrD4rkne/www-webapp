from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from routes.models import Route, Point
from images.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from common.tests.helpers import ImageHelper
import json


class RouteViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        self.image = Image.objects.create(
            name="Test Image",
            image=ImageHelper.get_image_file(name='test_image.jpg', ext='jpeg', size=(1920, 1080)),
            author=self.user,
            is_public=True
        )

        self.route = Route.objects.create(
            name="Test Route",
            image=self.image,
            author=self.user
        )

        self.point1 = Point.objects.create(route=self.route, lat=10, lon=20, order=1)
        self.point2 = Point.objects.create(route=self.route, lat=30, lon=40, order=2)

        self.other_route = Route.objects.create(
            name="Other Route",
            image=self.image,
            author=self.other_user
        )

        self.create_route_url = reverse('create_route_view', kwargs={'image_id': self.image.id})
        self.list_routes_url = reverse('get_routes_view')
        self.route_detail_url = reverse('get_route_view', kwargs={'route_id': self.route.id})
        self.delete_route_url = reverse('delete_route', kwargs={'route_id': self.route.id})
        self.create_point_url = reverse('create_point', kwargs={'route_id': self.route.id})
        self.delete_point_url = reverse('delete_point', kwargs={'route_id': self.route.id, 'point_id': self.point1.id})
        self.reorder_points_url = reverse('reorder_points', kwargs={'route_id': self.route.id})

    # Testy dla create_route_view

    def test_create_route_view_get(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.create_route_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/create.html')

    def test_create_route_view_post_success(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'name': 'New Test Route'}
        response = self.client.post(self.create_route_url, data)

        new_route = Route.objects.filter(name='New Test Route').first()
        self.assertIsNotNone(new_route)
        self.assertRedirects(response, reverse('get_route_view', kwargs={'route_id': new_route.id}))

    def test_create_route_view_image_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('create_route_view', kwargs={'image_id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Image not found", status_code=404)

    def test_create_route_invalid_name(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'name': ''}
        response = self.client.post(self.create_route_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/create.html')
        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_create_route_name_not_provided(self):
        self.client.login(username="testuser", password="testpassword")
        data = {}
        response = self.client.post(self.create_route_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/create.html')
        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_create_route_view_unauthorized(self):
        response = self.client.get(self.create_route_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.create_route_url}')

    def test_get_routes_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.list_routes_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/list.html')
        self.assertIn('routes', response.context)
        self.assertEqual(len(response.context['routes']), 1)

    def test_get_routes_view_unauthorized(self):
        response = self.client.get(self.list_routes_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.list_routes_url}')

    # Testy dla get_route_view

    def test_get_route_view_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.route_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/detail.html')
        self.assertEqual(response.context['route'], self.route)
        self.assertEqual(len(response.context['points']), 2)

    def test_get_route_view_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('get_route_view', kwargs={'route_id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Route not found", status_code=404)

    def test_get_route_view_unauthorized(self):
        response = self.client.get(self.route_detail_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.route_detail_url}')

    # Testy dla delete_route

    def test_delete_route_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.delete_route_url)

        self.assertRedirects(response, reverse('get_routes_view'))
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())

    def test_delete_route_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('delete_route', kwargs={'route_id': 99999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Route not found", status_code=404)

    def test_delete_route_permission_denied(self):
        self.client.login(username="otheruser", password="otherpassword")
        response = self.client.post(self.delete_route_url)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "You do not have permission to modify this route", status_code=403)
        self.assertTrue(Route.objects.filter(id=self.route.id).exists())

    def test_delete_route_unauthorized(self):
        response = self.client.post(self.delete_route_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.delete_route_url}')

    def test_create_point_success(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'lat': 50, 'lon': 60}
        response = self.client.post(self.create_point_url, data)

        self.assertRedirects(response, self.route_detail_url)
        self.assertTrue(Point.objects.filter(route=self.route, lat=50, lon=60).exists())
        self.assertEqual(Point.objects.filter(route=self.route).count(), 3)

    def test_create_point_route_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('create_point', kwargs={'route_id': 99999})
        data = {'lat': 50, 'lon': 60}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Route not found", status_code=404)

    def test_create_point_permission_denied(self):
        self.client.login(username="otheruser", password="otherpassword")
        data = {'lat': 50, 'lon': 60}
        response = self.client.post(self.create_point_url, data)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "You do not have permission to modify this route", status_code=403)

    def test_create_point_invalid_form(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'lat': 'invalid', 'lon': 60}
        response = self.client.post(self.create_point_url, data)

        self.assertEqual(response.status_code, 400)

    def test_create_point_invalid_cords(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'lat': 1920 + 1, 'lon': 0}
        response = self.client.post(self.create_point_url, data)

        self.assertEqual(response.status_code, 400)

    def test_delete_point_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.delete_point_url)

        self.assertRedirects(response, self.route_detail_url)
        self.assertFalse(Point.objects.filter(id=self.point1.id).exists())

    def test_delete_point_route_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('delete_point', kwargs={'route_id': 99999, 'point_id': self.point1.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Route not found", status_code=404)

    def test_delete_point_point_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('delete_point', kwargs={'route_id': self.route.id, 'point_id': 99999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Point not found", status_code=404)

    def test_delete_point_permission_denied(self):
        self.client.login(username="otheruser", password="otherpassword")
        response = self.client.post(self.delete_point_url)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "You do not have permission to modify this route", status_code=403)

    def test_reorder_points_success(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            'order': [
                {'id': self.point1.id, 'order': 2},
                {'id': self.point2.id, 'order': 1}
            ]
        }
        response = self.client.post(
            self.reorder_points_url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 204)
        self.point1.refresh_from_db()
        self.point2.refresh_from_db()
        self.assertEqual(self.point1.order, 2)
        self.assertEqual(self.point2.order, 1)

    def test_reorder_points_route_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('reorder_points', kwargs={'route_id': 99999})
        data = {
            'order': [
                {'id': self.point1.id, 'order': 2},
                {'id': self.point2.id, 'order': 1}
            ]
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Route not found", status_code=404)

    def test_reorder_points_permission_denied(self):
        self.client.login(username="otheruser", password="otherpassword")
        data = {
            'order': [
                {'id': self.point1.id, 'order': 2},
                {'id': self.point2.id, 'order': 1}
            ]
        }
        response = self.client.post(
            self.reorder_points_url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "You do not have permission to modify this route", status_code=403)

    def test_reorder_points_invalid_data_format(self):
        self.client.login(username="testuser", password="testpassword")
        data = {'invalid': 'data'}
        response = self.client.post(
            self.reorder_points_url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid data format", status_code=400)

    def test_reorder_points_point_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            'order': [
                {'id': 99999, 'order': 1},
                {'id': self.point2.id, 'order': 2}
            ]
        }
        response = self.client.post(
            self.reorder_points_url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Point with id 99999 not found", status_code=404)