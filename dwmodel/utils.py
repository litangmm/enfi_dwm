import os
import shutil
import tarfile
import time


def createTargetTar(modelPath, dockerfilePath):
    dir1 = 'temp/{0}'.format(time.time_ns())
    res = None
    try:
        os.mkdir(dir1)
    except Exception as result:
        print(result)
    else:
        tar = None
        try:
            res = shutil.copy(modelPath, '{0}/{1}'.format(dir1, modelPath.split('/')[-1]))
            tar = tarfile.open(res, 'a')
            tar.add(dockerfilePath, arcname='Dockerfile')
        except Exception as result:
            print(result)
            res = ''
        finally:
            if tar:
                tar.close()
    print(res)
    return res, dir1
