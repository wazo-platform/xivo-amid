Dockerfile for XiVO amid

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-amid github.com/wazo-pbx/xivo-amid

Or directly in the sources in contribs/docker

    docker build -t xivo-amid .
  
## Usage

To run the container, do the following:

    docker run -v /conf/amid:/etc/xivo/xivo-amid -t xivo-amid

On interactive mode :

    docker run -it xivo-amid /bin/bash

After launch xivo-amid-service in /root directory.

    xivo-amid -d -f

## Infos

- Using docker version 1.4.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'
