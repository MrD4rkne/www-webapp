from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('sse/notifications/', views.SSENotificationsView.as_view(), name='sse_notifications')
]
