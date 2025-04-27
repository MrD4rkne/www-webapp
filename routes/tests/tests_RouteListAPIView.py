from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from routes.models import Route

class RouteListAPIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('routes.api_views.Route.objects.filter')
    @patch('routes.api_views.RouteSerializer')
    def test_list_routes_for_authenticated_user(self, mock_serializer, mock_filter):
        # Mock the queryset returned by Route.objects.filter
        mock_route = MagicMock(spec=Route)
        mock_filter.return_value = [mock_route]

        # Mock the serializer's data
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = [{'id': 1, 'name': 'Test Route'}]

        response = self.client.get('/api/routes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{'id': 1, 'name': 'Test Route'}])

        mock_filter.assert_called_once_with(author=self.user)
        mock_serializer.assert_called_once_with([mock_route], many=True)

    @patch('routes.api_views.Route.objects.filter')
    def test_list_routes_no_routes_found(self, mock_filter):
        # Mock an empty queryset
        mock_filter.return_value = []

        response = self.client.get('/api/routes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        mock_filter.assert_called_once_with(author=self.user)

    def test_list_routes_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get('/api/routes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_unauthenticated_user(self):
        self.client.logout()
        response = self.client.post('/api/routes/', {'name': 'New Route'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch('routes.api_views.RouteCreateSerializer')
    @patch('routes.api_views.images_models.Image')
    def test_create_route_success(self, mock_image_model, mock_serializer_class):
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'id': 1, 'name': 'New Route'}
        mock_image = mock_image_model.objects.get.return_value
        mock_image.can_access.return_value = True

        data = {'name': 'New Route', 'image': 123}
        response = self.client.post('/api/routes/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'id': 1, 'name': 'New Route'})

        called_args, called_kwargs = mock_serializer_class.call_args
        self.assertIn('data', called_kwargs)
        self.assertEqual(dict(called_kwargs['data'].lists()), {'name': ['New Route'], 'image': ['123']})
        mock_serializer.is_valid.assert_called_once()
        mock_image_model.objects.get.assert_called_once_with(id='123')
        mock_image.can_access.assert_called_once_with(self.user)
        mock_serializer.save.assert_called_once_with(author=self.user)

    @patch('routes.api_views.RouteCreateSerializer')
    def test_create_route_invalid_serializer(self, mock_serializer_class):
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = {'name': ['This field is required.']}

        data = {'image': 123}
        response = self.client.post('/api/routes/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'name': ['This field is required.']})
        called_args, called_kwargs = mock_serializer_class.call_args
        self.assertIn('data', called_kwargs)
        self.assertEqual(dict(called_kwargs['data'].lists()), {'image': ['123']})
        mock_serializer.is_valid.assert_called_once()

    @patch('routes.api_views.RouteCreateSerializer')
    @patch('routes.api_views.images_models.Image')
    def test_create_route_image_not_found(self, mock_image_model, mock_serializer_class):
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        mock_image_model.DoesNotExist = Exception
        mock_image_model.objects.get.side_effect = mock_image_model.DoesNotExist

        data = {'name': 'New Route', 'image': 123}
        response = self.client.post('/api/routes/', data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Image not found"})
        called_args, called_kwargs = mock_serializer_class.call_args
        self.assertIn('data', called_kwargs)
        self.assertEqual(dict(called_kwargs['data'].lists()), {'name': ['New Route'], 'image': ['123']})
        mock_serializer.is_valid.assert_called_once()
        mock_image_model.objects.get.assert_called_once_with(id='123')

    @patch('routes.api_views.RouteCreateSerializer')
    @patch('routes.api_views.images_models.Image')
    def test_create_route_image_no_access(self, mock_image_model, mock_serializer_class):
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        mock_image = mock_image_model.objects.get.return_value
        mock_image.can_access.return_value = False

        data = {'name': 'New Route', 'image': 123}
        response = self.client.post('/api/routes/', data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Image not found"})
        called_args, called_kwargs = mock_serializer_class.call_args
        self.assertIn('data', called_kwargs)
        self.assertEqual(dict(called_kwargs['data'].lists()), {'name': ['New Route'], 'image': ['123']})
        mock_serializer.is_valid.assert_called_once()
        mock_image_model.objects.get.assert_called_once_with(id='123')
        mock_image.can_access.assert_called_once_with(self.user)