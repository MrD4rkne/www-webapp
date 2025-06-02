from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("images/", include("images.urls")),
    path("routes/", include("routes.urls")),
    path("accounts/", include("accounts.urls")),
    path("boards/", include("boards.urls")),
    path("", include("notifications.urls")),
    path("admin/", admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/routes/', include('routes.api_urls')),
    path('api/images/', include('images.api_urls')),
    path('api/boards/', include('boards.api_urls')),

    path('media/<path:path>', views.protected_media, name='protected_media'),

    path("", views.get_index, name="home")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)