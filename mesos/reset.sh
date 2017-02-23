#!/bin/bash

# This script is used to reset cluster to original installed state

interface=$(ip route | grep default | cut -d" " -f5)
address=$(ip addr | grep 'state UP' -A2 | grep ${interface} | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
#hostname=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
hostname=$address
echo "using network interface: ${interface}"
echo "using ip address: ${address}"
echo "using hostname: ${hostname}"


echo "update ipvsadm default setting(/etc/default/ipvsadm)"
sudo sh -c "cat >/etc/default/ipvsadm <<EOF
# ipvsadm

# if you want to start ipvsadm on boot set this to true
AUTO=false

# daemon method (none|master|backup)
DAEMON=none

# use interface (eth0,eth1...)
IFACE=${interface}

# syncid to use
SYNCID=1
EOF"

echo "update haproxy default setting(/etc/default/haproxy)"
sudo sh -c "cat >/etc/default/haproxy <<EOF
# Set ENABLED to 1 if you want the init script to start haproxy.
ENABLED=1
# Add extra flags here.
#EXTRAOPTS="-de -m 16"
EOF"

echo "configure zookeeper(/etc/zookeeper/conf/zoo.cfg)"
sudo sh -c "cat >/etc/zookeeper/conf/zoo.cfg <<EOF
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/var/lib/zookeeper
clientPort=2181
server.1=${address}:2888:3888
EOF"

echo "set zookeeper myid(/var/lib/zookeeper/myid)"
rm -rf /var/lib/zookeeper/* /etc/zookeeper/myid
sudo echo "1" >/var/lib/zookeeper/myid
sudo service zookeeper restart


sudo rm -rf /etc/mesos-slave/*
sudo rm -rf /etc/mesos-master/*
echo "configure mesos-master(/etc/mesos-master) and mesos-slave(/etc/mesos-slave)"
mkdir -p /etc/marathon/conf /etc/mesos-slave/resources

sudo echo "zk://${address}:2181/mesos" >/etc/mesos/zk

sudo echo "1" >/etc/mesos-master/quorum
sudo echo "${hostname}" >/etc/mesos-master/hostname
sudo echo "${hostname}" >/etc/mesos-master/ip
sudo echo "/home/dell/mesos" >/etc/mesos-master/work_dir

sudo echo "${hostname}" >/etc/mesos-slave/hostname
sudo echo "${hostname}" >/etc/mesos-slave/ip
sudo echo "/home/dell/mesos" >/etc/mesos-slave/work_dir
sudo echo "[1500-40000]" >/etc/mesos-slave/resources/ports
sudo echo "cgroups/devices,gpu/nvidia,disk/du,docker/runtime,filesystem/linux" >/etc/mesos-slave/isolation
#sudo echo "docker,mesos" >/etc/mesos-slave/containerizers
sudo rm -rf /var/lib/mesos/meta/*

sudo rm -rf /home/dell/mesos/*
#sudo rm -rf /home/dell/mesos/slaves
sudo service mesos-master restart
sudo service mesos-slave restart

echo "clear cassandra"
#sudo rm -f /var/lib/cassandra/* -R

echo "configure marathon(/etc/marathon/conf)"
sudo echo "${hostname}" >/etc/marathon/conf/hostname
sudo echo "zk://${address}:2181/mesos" >/etc/marathon/conf/master
sudo echo "zk://${address}:2181/marathon" >/etc/marathon/conf/zk
sudo echo "8080" >/etc/marathon/conf/http_port
sudo echo "gpu_resources" >/etc/marathon/conf/enable_features
sudo service marathon restart

echo "check upstart status: "
initctl list | grep -E "zookeeper|mesos-master|mesos-slave|marathon"

