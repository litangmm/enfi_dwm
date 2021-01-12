import json

from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from dwmodel.docker_requests import inspect_image, create_image, delete_image
from dwmodel.models import Image, ModelFile, DockerFile
from dwmodel.pagination import StandardResultsSetPagination
from dwmodel.serializers import ImageSerializer
from rest_framework import generics, status

from dwmodel.views import getNeedValue


def getReturnImageData(image):
    """
    根据 image 构建返回的 对象
    :param image:
    :return:
    """
    responseJson = inspect_image(imageId=image.docker_image_id).json()
    needKeys = ['Id', 'RepoTags', 'Created', 'Os', 'Size', 'VirtualSize', 'Metadata']
    returnJson = getNeedValue(
        sourceObject=responseJson,
        needKeys=needKeys)
    imageSerializer = ImageSerializer(image)
    return {
        'image': imageSerializer.data,
        'docker_image': returnJson,
    }


class NewImageList(generics.GenericAPIView, ListModelMixin):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sort = self.request.query_params.get('sorted', None)
        name = self.request.query_params.get('name', None)
        modelfile = self.request.query_params.get('modelfile', None)
        dockerfile = self.request.query_params.get('dockerfile', None)
        queryset = Image.objects.all()
        if sort is not None:
            queryset = queryset.order_by(sort)
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if modelfile is not None:
            queryset = queryset.filter(modelfile=modelfile)
        if dockerfile is not None:
            queryset = queryset.filter(dockerfile=dockerfile)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # 1. 解析请求 (model_id,dockerfile_id,name,description)
        requestForm = request.data
        name = requestForm.get('name')
        description = requestForm.get('description')
        dockerfileId = requestForm.get('dockerfile')
        modelfileId = requestForm.get('modelfile')

        if Image.objects.filter(name=name).count() > 0:
            return Response({'message': '已经存在name为{0}的容器'.format(name)}, status.HTTP_409_CONFLICT)
        modelfile = get_object_or_404(ModelFile.objects.all(), pk=modelfileId)
        dockerfile = get_object_or_404(DockerFile.objects.all(), pk=dockerfileId)
        # 2. 根据请求发送 创建镜像请求，获取返回的 docker_image_id
        response = create_image(modelfile.file.name, dockerfile.file.name, name)
        docker_image_id = None
        if response.status_code > 300:
            return Response(response.json(), status=response.status_code)
        else:
            responses = response.text.split('\r\n')
            for resp in responses:
                respjson = json.loads(resp)
                if respjson.get('aux'):
                    docker_image_id = respjson.get('aux').get('ID')
                    break
            # 3. 更新数据库（插入数据 image:
            image = ImageSerializer(data={
                'modelfile': modelfileId,
                'dockerfile': dockerfileId,
                'name': name,
                'description': description,
                'docker_image_id': docker_image_id,
            })
            image.is_valid()
            image.save()
            return Response(image.data, status=status.HTTP_201_CREATED)


class NewImageDetail(generics.GenericAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        image = self.get_object()
        returnImageData = getReturnImageData(image)
        return Response(returnImageData)

    def put(self, request, *args, **kwargs):
        return Response(
            data={'message': '暂不支持PUT更新，请使用PATCH进行部分更新'},
            status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        image = self.get_object()
        description = request.data.get('description')
        image.description = description
        image.save()
        return Response({"message": "成功修改"}, status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        image = self.get_object()
        docker_image_id = image.docker_image_id
        response = delete_image(docker_image_id)
        if response.status_code < 400:
            image.delete()
        return Response(response.json(), response.status_code)
