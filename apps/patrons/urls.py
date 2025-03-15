from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatronViewSet

router = DefaultRouter()
router.register('', PatronViewSet, basename='patron')

app_name = 'patrons'

urlpatterns = [
    path('', include(router.urls)),
]
