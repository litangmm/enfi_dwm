from rest_framework import serializers
from .models import ModelFile
from .models import DockerFile
from .models import Image
from .models import Container


class ModelFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelFile
        fields = "__all__"
        read_only_fields = ('id',)


class DockerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerFile
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id',
                  'name',
                  'description',
                  'docker_image_id',
                  'dockerfile',
                  'modelfile']


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = "__all__"


class DockerImageSerializer(serializers.Serializer):
    """
    DockerImage序列化类 镜像id 创建时间 状态 状态详情 大小 虚拟大小 容器数量
    """
    id = serializers.CharField(max_length=200)
    created = serializers.CharField(max_length=200)
    state = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=200)
    size = serializers.IntegerField()
    virtualsize = serializers.IntegerField()
    tags = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )
    # containers = serializers.IntegerField()


class DockerContainerSerializer(serializers.Serializer):
    """
    DockerContainer序列化类 容器id image对象 创建时间 状态 状态详情
    """
    id = serializers.CharField(max_length=200)
    image = DockerImageSerializer()
    created = serializers.IntegerField()
    state = serializers.CharField(max_length=200, required=False)
    status = serializers.CharField(max_length=200, required=False)


class DockerPortSerializer(serializers.Serializer):
    """
    DockerPort序列化类 内部接口 外部接口 网络类型
    """
    private = serializers.IntegerField()
    public = serializers.IntegerField()
    type = serializers.CharField(max_length=100)


class ReturnImageSerializer(serializers.Serializer):
    image = ImageSerializer()
    docker_image = DockerImageSerializer()
