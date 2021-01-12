import json

from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from dwmodel.docker_requests import inspect_image, create_image, delete_image, inspect_container, create_container, \
    remove_container, start_container, pause_container, stop_container, restart_container, unpause_container
from dwmodel.models import Container
from dwmodel.pagination import StandardResultsSetPagination
from dwmodel.serializers import ImageSerializer, ContainerSerializer
from rest_framework import generics, status

from dwmodel.views import getNeedValue


def getReturnContainerData(container):
    """
    根据 container 构建返回的 对象
    :param container:
    :return:
    """
    responseJson = inspect_container(containerId=container.docker_container_id).json()
    needKeys = ['Id', 'Created', 'State.Status', 'LogPath', 'RestartCount', 'NetworkSettings.Ports']
    returnJson = getNeedValue(
        sourceObject=responseJson,
        needKeys=needKeys
    )
    containerSerializer = ContainerSerializer(container)
    return {
        'container': containerSerializer.data,
        'docker_container': returnJson,
    }


class NewContainerList(generics.GenericAPIView, ListModelMixin):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sort = self.request.query_params.get('sorted', None)
        name = self.request.query_params.get('name', None)
        image = self.request.query_params.get('image', None)
        port_in = self.request.query_params.get('port_in', None)
        port_out = self.request.query_params.get('port_out', None)
        queryset = Container.objects.all()
        if sort is not None:
            queryset = queryset.order_by(sort)
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if image is not None:
            queryset = queryset.filter(image=image)
        if port_in is not None:
            queryset = queryset.filter(port_in=port_in)
        if port_out is not None:
            queryset = queryset.filter(port_in=port_out)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # 1. 解析请求 (model_id,dockerfile_id,name,description)
        requestForm = request.data
        name = requestForm.get('name')
        image_id = requestForm.get('image')
        port_in = requestForm.get('port_in')
        port_out = requestForm.get('port_out')
        description = requestForm.get('description')

        if Container.objects.filter(name=name).count() > 0:
            return Response({'message': '已经存在name为{0}的容器'.format(name)}, status.HTTP_409_CONFLICT)
        if Container.objects.filter(port_out=port_out).count() > 0:
            return Response({'message': '已经存在port_out为{0}的容器'.format(port_out)}, status.HTTP_409_CONFLICT)

        image = Container.objects.get(pk=image_id)
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


class NewContainerDetail(generics.GenericAPIView):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer

    def get(self, request, *args, **kwargs):
        container = self.get_object()
        returnImageData = getReturnContainerData(container)
        return Response(returnImageData)

    def put(self, request, *args, **kwargs):
        return Response(
            data={'message': '暂不支持PUT更新，请使用PATCH进行部分更新'},
            status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        container = self.get_object()
        description = request.data.get('description')
        action = request.data.get('action')
        if description:
            container.description = description
            container.save()
        if action:
            docker_container_id = container.docker_container_id
            if action == 'start':
                response = start_container(docker_container_id)
            elif action == 'pause':
                response = pause_container(docker_container_id)
            elif action == 'unpause':
                response = unpause_container(docker_container_id)
            elif action == 'stop':
                response = stop_container(docker_container_id)
            elif action == 'restart':
                response = restart_container(docker_container_id)
            else:
                return Response(
                    {'message': '未知的action{}'.format(action)},
                    status.HTTP_400_BAD_REQUEST
                )
            if response.text != '':
                return Response(response.json(), response.status_code)
            else:
                return Response('', response.status_code)
        else:
            return Response(
                {'message': '未知的action{} desc'.format(action, description)},
                status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        container = self.get_object()
        docker_container_id = container.docker_container_id
        response = remove_container(docker_container_id)
        if response.status_code < 500:
            container.delete()
        return Response(response.json(), response.status_code)
