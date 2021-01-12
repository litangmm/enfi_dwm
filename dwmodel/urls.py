from django.urls import path, include, re_path
from .views import ModelFileViewSet
from .views import DockerFileViewSet
from .views import ImageViewSet
from .views import ContainerViewSet
from .image_views import NewImageList, NewImageDetail
from .container_views import NewContainerList, NewContainerDetail
from .file_views import ModelFileList, ModelFileDetail, DockerFileList, DockerFileDetail
from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'dockerfile', DockerFileViewSet)
# router.register(r'modelfile', ModelFileViewSet)
# router.register(r'image', ImageViewSet)
# router.register(r'container', ContainerViewSet)

urlpatterns = [
    re_path(r'^image/$', NewImageList.as_view()),
    re_path(r'^image/(?P<pk>[0-9]+)/$', NewImageDetail.as_view()),
    re_path(r'^container/$', NewContainerList.as_view()),
    re_path(r'^container/(?P<pk>[0-9]+)/$', NewContainerDetail.as_view()),
    re_path(r'^modelfile/$', ModelFileList.as_view()),
    re_path(r'^modelfile/(?P<pk>[0-9]+)/$', ModelFileDetail.as_view()),
    re_path(r'^dockerfile/$', DockerFileList.as_view()),
    re_path(r'^dockerfile/(?P<pk>[0-9]+)/$', DockerFileDetail.as_view()),
    # path('', include(router.urls)),
]
