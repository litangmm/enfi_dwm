from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response

from dwmodel.models import DockerFile, ModelFile
from dwmodel.pagination import StandardResultsSetPagination
from dwmodel.serializers import DockerFileSerializer, ModelFileSerializer


class DockerFileList(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    queryset = DockerFile.objects.all()
    serializer_class = DockerFileSerializer
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DockerFileDetail(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    queryset = DockerFile.objects.all()
    serializer_class = DockerFileSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ModelFileList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = ModelFile.objects.all()
    serializer_class = ModelFileSerializer
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ModelFileDetail(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    queryset = ModelFile.objects.all()
    serializer_class = ModelFileSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
