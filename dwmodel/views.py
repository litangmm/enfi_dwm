from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
import json

from .models import ModelFile
from .models import DockerFile
from .models import Image
from .models import Container
from .serializers import DockerFileSerializer
from .serializers import ModelFileSerializer
from .serializers import ImageSerializer
from .serializers import ContainerSerializer
# from .serializers import DockerImageSerializer
# from .serializers import DockerContainerSerializer
# from .serializers import ReturnImageSerializer
from rest_framework.response import Response
from .docker_requests import inspect_image, \
    create_image, delete_image, \
    create_container, inspect_container, \
    start_container, stop_container, \
    restart_container, kill_container, pause_container, remove_container


def getNeedValue(sourceObject, needKeys):
    returnJson = {}
    for needKey in needKeys:
        subkeys = needKey.split('.')
        needValue = sourceObject
        for subkey in subkeys:
            needValue = needValue.get(subkey)
            if not needValue: break
        returnJson[needKey] = needValue
    return returnJson


class DockerFileViewSet(viewsets.ModelViewSet):
    queryset = DockerFile.objects.all()
    serializer_class = DockerFileSerializer


class ModelFileViewSet(viewsets.ModelViewSet):
    queryset = ModelFile.objects.all()
    serializer_class = ModelFileSerializer

# TODO 需要检查name 不能相同
class ImageViewSet(viewsets.ViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def getReturnImageData(self, image):
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

    def list(self, request):
        modelfile = request.query_params.get('modelfile')
        images = Image.objects.all()
        if modelfile:
            images = Image.objects.filter(modelfile=modelfile)
            if images.count() < 1:
                return Response({'message': 'not found'}, status.HTTP_404_NOT_FOUND)
        returnImageDatas = []
        for image in images:
            returnImageData = self.getReturnImageData(image)
            # returnImageSerializer.is_valid()
            returnImageDatas.append(returnImageData)
        return Response(returnImageDatas)

    def create(self, request):
        # 1. 解析请求 (model_id,dockerfile_id,name,description)
        requestForm = request.data
        id = requestForm.get('id')
        name = requestForm.get('name')
        description = requestForm.get('description')
        dockerfileId = requestForm.get('dockerfile')
        modelfileId = requestForm.get('modelfile')
        modelfile = get_object_or_404(ModelFile.objects.all(), pk=modelfileId)
        dockerfile = get_object_or_404(DockerFile.objects.all(), pk=dockerfileId)
        # 2. 根据请求发送 创建镜像请求，获取返回的 docker_image_id
        response = create_image(modelfile.file, dockerfile.file, name)
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

    def retrieve(self, request, pk=None):
        image = get_object_or_404(self.queryset, pk=pk)
        returnImageData = self.getReturnImageData(image)
        return Response(returnImageData)

    def update(self, request, pk=None):
        return Response({}, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        image = get_object_or_404(Image.objects.all(), pk=pk)
        description = request.data.get('description')
        image.description = description
        image.save()
        return Response({"message": "成功修改"}, status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        image = get_object_or_404(Image.objects.all(), pk=pk)
        docker_image_id = image.docker_image_id
        response = delete_image(docker_image_id)
        if response.status_code == 200:
            image.delete()
            return Response(response.json(), response.status_code)
        elif response.status_code == 404:
            image.delete()
            return Response(response.json(), response.status_code)
        elif response.status_code == 409:
            return Response(response.json(), response.status_code)
        else:
            return Response(response.json(), response.status_code)


# TODO 需要检查name 不能相同
class ContainerViewSet(viewsets.ViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer

    def getReturnContainerData(self, container):
        """
        根据 container 构建返回的 对象
        :param container:
        :return:
        """
        responseJson = inspect_container(containerId=container.docker_container_id).json()
        needKeys = ['Id', 'Created', 'State', 'Image', 'LogPath', 'RestartCount', 'NetworkSettings.Ports']
        returnJson = getNeedValue(
            sourceObject=responseJson,
            needKeys=needKeys
        )
        containerSerializer = ContainerSerializer(container)
        return {
            'container': containerSerializer.data,
            'docker_container': returnJson,
        }

    def list(self, request):
        containers = Container.objects.all()
        returnContainerDatas = []
        for container in containers:
            returnContainerData = self.getReturnContainerData(container)
            returnContainerDatas.append(returnContainerData)
        return Response(returnContainerDatas)

    def create(self, request):
        requestForm = request.data
        # 1. 解析请求 imageId(镜像id) ports(端口对象) name(容器名称) description(描述)
        image_id = requestForm.get('image')
        port_in = requestForm.get('port_in')
        port_out = requestForm.get('port_out')
        name = requestForm.get('name')
        if Container.objects.filter(name=name).count() > 0:
            return Response({'message': '已经存在name为{0}的容器'.format(name)}, status.HTTP_409_CONFLICT)
        if Container.objects.filter(port_out=port_out).count() > 0:
            return Response({'message': '已经存在port_out为{0}的容器'.format(port_out)}, status.HTTP_409_CONFLICT)
        description = requestForm.get('description')
        image = Image.objects.get(pk=image_id)
        docker_image_id = image.docker_image_id
        # 2. 使用 imageid ports name 发送请求，创建容器
        response = create_container(
            name=name,
            imageId=docker_image_id,
            ports=[port_in, port_out],
        )
        # 3. 得到返回的请求
        # 4. 解析请求

        #   4.1 创建失败 返回
        if response.status_code > 300:
            return Response(response.json(), response.status_code)
        #   4.2 创建成功
        else:
            docker_container_id = response.json().get("Id")
            container = ContainerSerializer(data={
                'image': image_id,
                'name': name,
                'description': description,
                'docker_container_id': docker_container_id,
                'port_in': port_in,
                'port_out': port_out,
            })
            container.is_valid()
            container.save()
            return Response(container.data, status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        container = get_object_or_404(self.queryset, pk=pk)
        response = self.getReturnContainerData(container)
        return Response(response, 200)

    def update(self, request, pk=None):
        return Response({}, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        container = get_object_or_404(Container.objects.all(), pk=pk)
        description = request.data.get('description')
        action = request.data.get('action')
        if description:
            container.description = description
        if action:
            docker_container_id = container.docker_container_id
            if action == 'start':
                response = start_container(docker_container_id)
                return Response(response, status.HTTP_200_OK)

            elif action == 'pause':
                response = pause_container(docker_container_id)
                return Response(response, status.HTTP_200_OK)

            elif action == 'stop':
                response = stop_container(docker_container_id)
                return Response(response, status.HTTP_200_OK)

            elif action == 'restart':
                response = restart_container(docker_container_id)
                return Response(response, status.HTTP_200_OK)

            else:
                return Response(
                    {'message': '未知的action{}'.format(action)},
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'message': '未知的action{} desc'.format(action, description)},
                status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, pk=None):  # TODO 与image删除实现不一样，是否存在问题
        container = get_object_or_404(Container.objects.all(), pk=pk)
        docker_container_id = container.docker_container_id
        response = remove_container(docker_container_id)
        if response.status_code < 300:
            container.delete()
            return Response(response.json(), response.status_code)
        return Response(response.json(), response.status_code)
