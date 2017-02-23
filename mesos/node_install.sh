#!/bin/bash

echo "set repository of java/mesos/marathon component"
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv E56151BF

DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
CODENAME=$(lsb_release -cs)

sudo echo "deb http://repos.mesosphere.com/${DISTRO} ${CODENAME} main" | sudo tee /etc/apt/sources.list.d/mesosphere.list

echo "install required components"
sudo apt-get -y update
sudo apt-get -y install mesos marathon chronos haproxy keepalived python-pip libffi-dev python-dev
sudo pip install setuptools markupsafe ansible --upgrade

mkdir -p /etc/marathon/conf
