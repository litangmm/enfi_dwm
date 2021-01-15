from django.db import models
from datetime import datetime

class ModelFile(models.Model):
    id = models.IntegerField(primary_key=True)
    file = models.FileField(upload_to='file/models/')
    create_time = models.DateTimeField(auto_created=True, default=datetime.now, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.description


class DockerFile(models.Model):
    id = models.IntegerField(primary_key=True)
    file = models.FileField(upload_to='file/dockerfiles/')
    description = models.TextField()

    def __str__(self):
        return self.description


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    modelfile = models.ForeignKey(ModelFile, related_name='modelfile', on_delete=models.CASCADE)
    dockerfile = models.ForeignKey(DockerFile, related_name='dockerfile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    docker_image_id = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.description


class Container(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    docker_container_id = models.CharField(max_length=100, blank=True, default='')
    port_in = models.IntegerField(default=80)
    port_out = models.IntegerField(default=80)

    def __str__(self):
        return self.description
