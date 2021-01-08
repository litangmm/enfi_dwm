from django.urls import path, include
from .views import ModelFileViewSet
from .views import DockerFileViewSet
from .views import ImageViewSet
from .views import ContainerViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dockerfile', DockerFileViewSet)
router.register(r'modelfile', ModelFileViewSet)
router.register(r'image', ImageViewSet)
router.register(r'container', ContainerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
