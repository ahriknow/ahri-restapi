# Ahri Restapi

## Create restapi by view, support mysql、mongo, etc.

## Build the image

```Dockerfile
FROM python:3.8
MAINTAINER "ahri"<ahriknow@ahriknow.cn>
ADD ./ /project/Ahriknow
COPY pip.conf /etc/pip.conf
WORKDIR /project/Ahriknow
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 9000
ENTRYPOINT ["gunicorn", "-w", "2", "-b", "0.0.0.0:9000", "AhriRestapi.wsgi"]
```

## Run a container

```bash
docker container run --name restapi -p 80:9000 -d ahriknow/restapi:v20200413
```

-   `--name restapi` 容器名为 restapi
-   `-p 80:9000` 将容器 9000 端口映射到宿主机 80 端口
-   `-d` 后台运行
-   `ahriknow/restapi:v20200413` 镜像

## Python requirements.txt

```py
asgiref==3.2.7
Django==3.0.5
django-cors-headers==3.2.1
djangorestframework==3.11.0
gunicorn==20.0.4
pymongo==3.10.1
PyMySQL==0.9.3
pytz==2019.3
shortuuid==1.0.1
sqlparse==0.3.1
```

## 请求地址

[https://api.ahriknow.com/restapi/](https://api.ahriknow.com/restapi/)

## 管理地址

[https://www.ahriknow.com/#/admin/restapi-project](https://www.ahriknow.com/#/admin/restapi-project)

## Powered By ahri 20200413
