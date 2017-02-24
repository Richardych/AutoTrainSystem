import os
import subprocess
import sys

if __name__ == '__main__':
    gpus = sys.argv[1]
    mid = sys.argv[2]
    gpuparam = sys.argv[3]
    ip = ""
    st_map = 0
    map_res = []
    cmd = "/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d \"addr:\""
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout,stderr = p.communicate()

    j = 0
    k = 0
    for i in range(len(stdout.strip())-1):
        if stdout.strip()[i] == '1' and stdout.strip()[i+1] == '9':
            j = i
        if stdout.strip()[i] == '\n':
            k = i
    if k<j:
        ip = stdout.strip()[j:]
    else:
        ip = stdout.strip()[j:k]

    with open('/home/ATS/gpu_map.txt') as f:
        lines = f.readlines()
        for li in lines:
            li = li[:-1]
            li_ip = li.strip().split(',')[0]
            if li_ip == ip:
                map_res = li.split(',')[1:]
                break
        for i in range(len(map_res)):
            if ((i<len(map_res)-1) and map_res[i]=='2' and map_res[i+1]=='0') or (map_res[i]=='2' and i == len(map_res)-1 ):
                st_map = int(i+1) - int(gpus)
                break
    device_cmd = ""
    dg = 0
    
    for i in range(int(st_map),int(st_map)+int(gpus)):    #2,1,1,0  i=1,2
        device_cmd = device_cmd + " --device /dev/nvidia"+ str(i) +":/dev/nvidia"+str(dg)
        dg = dg + 1


    cmd_docker = "sudo docker run -v /home/:/mnt/home --device /dev/nvidia-uvm:/dev/nvidia-uvm  --device /dev/nvidiactl:/dev/nvidiactl %s 192.168.2.13:5000/caffe:cuda7v4_ych /bin/bash /root/train.sh %s %s" %(device_cmd, mid, gpuparam)
    os.system(cmd_docker)








