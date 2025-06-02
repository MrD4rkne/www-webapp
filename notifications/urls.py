from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('sse/notifications/', views.SSENotificationsView.as_view(), name='sse_notifications'),
    path('sse/', views.SSEDemoView.as_view(), name='sse_demo'),
    path('sse/test/', views.SSETestView.as_view(), name='test'),
    path('sse/trigger-test-event/', views.TriggerTestEventView.as_view(), name='trigger_test_event'),
]
