from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response

from dwmodel.models import DockerFile, ModelFile, Image
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


class ModelFileDetail(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView):
    queryset = ModelFile.objects.all()
    serializer_class = ModelFileSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        createImage = Image.objects.filter(modelfile__id=instance.id)

        responseData = {
            'id': instance.id,
            'description': instance.description,
            'file': {
                'size': instance.file.size,
                'path': instance.file.url
            },
            'images': createImage.count(),
            'create_time': instance.create_time,
            'name': instance.file.url.split('/')[-1].split('.')[0],
        }
        return Response(responseData)
        # return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
