import requests
import tarfile
import json

from .setting import DOCKER_BASE_URL as BASE_URL


#
# def create_image_tar(rootPath, dockerfilePath):
#     with tarfile.open(rootPath, 'w') as tar:
#         tar.add(dockerfilePath)
#     return rootPath


# 1.镜像管理
# 1.1 创建镜像 file+dockerfile
def create_image(modelfile, dockerfile, tag):
    url = '{0}/build'.format(BASE_URL)
    querystring = {
        't': 'dw/{0}'.format(tag)
    }
    headers = {
        'Content-Type': 'application/x-tar'
    }
    response = requests.request(method='POST', headers=headers,
                                url=url, params=querystring,
                                data=modelfile)
    return response


# 1.2 删除镜像 byId
def delete_image(imageId):
    url = '{0}/images/{1}'.format(BASE_URL, imageId)
    response = requests.delete(url=url)
    return response


# 1.3 获取所有镜像信息
def list_images():
    url = '{0}/images/json'.format(BASE_URL)
    response = requests.get(url=url)
    return response


# 1.4 获取单个镜像信息 byId
def inspect_image(imageId):
    url = '{0}/images/{1}/json'.format(BASE_URL, imageId)
    response = requests.get(url=url)
    return response


# 1.5 导出镜像 byId
def export_image(imageId):
    url = '{0}/images/{1}/get'.format(BASE_URL, imageId)
    response = requests.get(url=url)
    return response


# 2.容器管理
# 2.1 创建容器 镜像id+ports
def create_container(name, imageId, ports):
    url = '{0}/containers/create'.format(BASE_URL)

    querystring = {"name": name}
    payload = json.dumps({
        "Image": imageId,
        "HostConfig": {
            "PortBindings": {
                ports[0] + '/tcp': [
                    {
                        "HostPort": ports[1]
                    }
                ]
            }
        }
    })
    headers = {
        'content-type': "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    res = response.text
    return response


# 2.2 获取所有容器信息
def list_containers():
    url = '{0}/containers/json'.format(BASE_URL)
    response = requests.get(url)
    return response


# 2.2 获取单个容器信息 byId
def inspect_container(containerId):
    url = '{0}/containers/{1}/json'.format(BASE_URL, containerId)
    response = requests.get(url)
    return response


# 2.3 启动容器 byId
def start_container(containerId):
    url = '{0}/containers/{1}/start'.format(BASE_URL, containerId)
    response = requests.post(url)
    return response


# 2.4 暂停容器 byId
def pause_container(containerId):
    url = '{0}/containers/{1}/pause'.format(BASE_URL, containerId)
    response = requests.post(url)
    return response


# 2.5 停止容器 byId
def stop_container(containerId):
    url = '{0}/containers/{1}/stop'.format(BASE_URL, containerId)
    response = requests.post(url)
    return response


# 2.6 重启容器 byId
def restart_container(containerId):
    url = '{0}/containers/{1}/restart'.format(BASE_URL, containerId)
    response = requests.post(url)
    return response


# 2.7 杀死容器 byId
def kill_container(containerId):
    url = '{0}/containers/{1}/kill'.format(BASE_URL, containerId)
    response = requests.post(url)
    return response


# 2.8 移除容器 byId
def remove_container(containerId):
    url = '{0}/containers/{1}'.format(BASE_URL, containerId)
    response = requests.delete(url)
    return response


# 2.9 获取log byId
def logs_containers(containerId):
    url = '{0}/containers/{1}/logs'.format(BASE_URL, containerId)
    response = requests.get(url)
    return response
