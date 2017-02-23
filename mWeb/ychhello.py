# coding=utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)
import web
import os
import sys
import pandas as pd
import subprocess
import json
import random
from web import form
import urllib2
import requests
import re
import socket
import time
#web.config.debug = False

urls = (
    '/dglearner/v1/getdevice', 'getdevice',
    '/dglearner/v1/reqresource', 'reqresource',
    '/dglearner/v1/uploadfile', 'uploadfile',
    '/dglearner/v1/train','train',
    '/dglearner/v1/showlog','showlog'
)
render = web.template.render('templates/')

'''
get the cluster's device info
'''
class getdevice:
    def GET(self):
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        req = urllib2.Request('http://'+IP+':5050/master/state?jsonp=angular.callbacks._5')
        response = urllib2.urlopen(req)
        deviceinfo = response.read()
        activated_slaves = re.findall(r'\"activated_slaves\":(.*?),', deviceinfo)[0]
        leader = re.findall(r'\"leader\":\"(.*?)\",', deviceinfo)[0]
        slaves = re.findall(r'\"slaves\":\[(.*?)\],', deviceinfo)
        total = re.findall(r'\"resources\":\{(.*?)\}', str(slaves))
        used = re.findall(r'\"used_resources\":\{(.*?)\}', str(slaves))

        slavedic = {}
        gpu_total = 0
        cpu_total = 0
        mem_total = 0.0
        disk_total =0.0
        gpu_used = 0
        cpu_used = 0
        mem_used = 0.0
        disk_used =0.0

        for sla_i in range(int(float(activated_slaves[0]))):
            gpu_total += int(float(re.findall(r'\"gpus\":(.*?),', str(total))[sla_i]))
            cpu_total += int(float(re.findall(r'\"cpus\":(.*?),', str(total))[sla_i]))
            mem_total += float(re.findall(r'\"mem\":(.*?),', str(total))[sla_i]) / 1024.0
            disk_total += float(re.findall(r'\"disk\":(.*?),', str(total))[sla_i]) / (1024.0*1024.0)
            gpu_used += int(float(re.findall(r'\"gpus\":(.*?),', str(used))[sla_i]))
            cpu_used += int(float(re.findall(r'\"cpus\":.*?(\d+)', str(used))[sla_i]))
            mem_used += float(re.findall(r'\"mem\":(.*?),', str(used))[sla_i]) / 1024.0
            disk_used += float(re.findall(r'\"disk\":(.*?),', str(used))[sla_i]) / (1024.0*1024.0)
            tmpdic = {}
            tmpdic['id'] =  re.findall(r'\"id\":\"(.*?)\",', str(slaves))[sla_i]
            tmpdic['active'] = re.findall(r'\"active\":(.*?),', str(slaves))[sla_i]
            tmpdic['ip'] = re.findall(r'\"hostname\":\"(.*?)\",', str(slaves))[sla_i]
            tmpdic['total_gpu'] = int(float(re.findall(r'\"gpus\":(.*?),', str(total))[sla_i]))
            tmpdic['total_cpu'] = int(float(re.findall(r'\"cpus\":(.*?),', str(total))[sla_i]))
            tmpdic['total_mem'] = '{0:.2f}'.format(float(re.findall(r'\"mem\":(.*?),', str(total))[sla_i]) / 1024.0)
            tmpdic['total_disk'] = '{0:.2f}'.format(float(re.findall(r'\"disk\":(.*?),', str(total))[sla_i]) / (1024.0*1024.0))
            tmpdic['used_gpu'] = int(float(re.findall(r'\"gpus\":(.*?),', str(used))[sla_i]))
            tmpdic['used_cpu'] = int(float(re.findall(r'\"cpus\":.*?(\d+)', str(used))[sla_i]))
            tmpdic['used_mem'] = '{0:.2f}'.format(float(re.findall(r'\"mem\":(.*?),', str(used))[sla_i]) / 1024.0)
            tmpdic['used_disk'] = '{0:.2f}'.format(float(re.findall(r'\"disk\":(.*?),', str(used))[sla_i]) / (1024.0*1024.0))
            slavedic['Slave'+str(sla_i)] = tmpdic

        totaldic = {'gpu_total':gpu_total, 'cpu_total':cpu_total, 'mem_total':'{0:.2f}'.format(mem_total), 'disk_total':'{0:.2f}'.format(disk_total)}
        useddic = {'gpu_used':gpu_used, 'cpu_used':cpu_used, 'mem_used':'{0:.2f}'.format(mem_used), 'disk_used':'{0:.2f}'.format(disk_used)}
        devicedic = {"activated_slaves":activated_slaves,"leader":leader,"totaldic":totaldic,"useddic":useddic,"slavedic":slavedic}
        devicedic_lookgood = "activated_slaves:\t\t"+activated_slaves+"\n\n" \
                             +"leader:\t\t\t\t"+leader+"\n\n" \
                             +"totaldic:\t\t\t\t"+str(totaldic)+"\n\n" \
                             +"useddic:\t\t\t\t"+str(useddic)+ "\n\n" \
                             +"Slave0:\t\t\t\t" + str(slavedic["Slave0"]) + "\n\n" \
                             +"Slave1:\t\t\t\t" + str(slavedic["Slave1"]) + "\n\n"

        return render.index(devicedic_lookgood, json.dumps(devicedic))

'''
request the computint resources
'''
class reqresource:
    def POST(self):
        i = web.input()
        cpus = int(i.get('cpus'))
        gpus = int(i.get('gpus'))
        mem = float(i.get('mem'))
        disk = float(i.get('disk'))
        instances = i.get('instances')
        devinfo = i.get('devinfo')
        activated_slaves = int(float(re.findall(r'"activated_slaves": \"(.*?)\",',str(devinfo))[0]))
        #per slave's info, total and used
        total_cpu = re.findall(r'"total_cpu": (.*?),', str(devinfo))
        total_gpu = re.findall(r'"total_gpu": (.*?),', str(devinfo))
        total_disk = re.findall(r'"total_disk": \"(.*?)\",', str(devinfo)) 
        total_mem = re.findall(r'"total_mem": \"(.*?)\",', str(devinfo))
        used_cpu = re.findall(r'"used_cpu": (.*?),', str(devinfo))
        used_gpu = re.findall(r'"used_gpu": (.*?),', str(devinfo))
        used_disk = re.findall(r'"used_disk": \"(.*?)\",', str(devinfo))
        used_mem = re.findall(r'"used_mem": \"(.*?)\",', str(devinfo))
        for i in range(activated_slaves):
            if ((int(total_gpu[i])-int(used_gpu[i]) < gpus) or (int(total_cpu[i])-int(used_cpu[i]) < cpus) or (float(total_disk[i])-float(used_disk[i]) < float(disk)) or (float(total_mem[i])-float(used_mem[i]) < float(mem)/1024.0)):
                if i==(activated_slaves-1):
                    return render.index1('error',gpus)
                else:
                    continue
        
        # if the resource request is ok, return true and the 16 ID, then create the user's folder
        seed = "1234567890abcdefghijklmnopqrstuvwxyz"
        sa = []
        for i in range(16):
            sa.append(random.choice(seed))
        salt = ''.join(sa)
        ids = salt
        folderdir = '/home/ATS/file/'
        if not os.path.exists(folderdir+ids):
            os.makedirs(folderdir+ids)
        else:
            return json.dumps({'create error':1})
        if not os.path.exists(folderdir+ids + '/input'):
            os.makedirs(folderdir+ids + '/input')
        if not os.path.exists(folderdir+ids + '/output'):
            os.makedirs(folderdir+ids + '/output')
        if not os.path.exists(folderdir+ids + '/mountdir'):
            os.makedirs(folderdir+ids + '/mountdir')
        if not os.path.exists(folderdir+ids + '/premodel'):
            os.makedirs(folderdir+ids + '/premodel')

        confstr = str(ids)+','+str(cpus)+','+str(gpus)+','+str(mem)+','+str(disk)+','+str(instances)
        with open('/home/ATS/file/'+ids+'/conf.txt', 'wb') as f:
            f.write(confstr)
        f.close()

        '''
        get ip and gpus, write it to gpu_map.txt , start with ALL 0,0,0,0
        '''
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        req = urllib2.Request('http://'+IP+':5050/master/state?jsonp=angular.callbacks._5')
        response = urllib2.urlopen(req)
        deviceinfo = response.read()
        activated_slaves = re.findall(r'\"activated_slaves\":(.*?),', deviceinfo)[0]
        slaves = re.findall(r'\"slaves\":\[(.*?)\],', deviceinfo)
        total = re.findall(r'\"resources\":\{(.*?)\}', str(slaves))
        used = re.findall(r'\"used_resources\":\{(.*?)\}', str(slaves))
        devlist = []
        for sla_i in range(int(float(activated_slaves[0]))):
            tmpdic = {}
            tmpdic['id'] =  re.findall(r'\"id\":\"(.*?)\",', str(slaves))[sla_i]
            tmpdic['ip'] = re.findall(r'\"hostname\":\"(.*?)\",', str(slaves))[sla_i]
            tmpdic['total_gpu'] = int(float(re.findall(r'\"gpus\":(.*?),', str(total))[sla_i]))
            tmpdic['used_gpu'] = int(float(re.findall(r'\"gpus\":(.*?),', str(used))[sla_i]))
            devlist.append(tmpdic)


        if not os.path.exists(folderdir+'gpu_map.txt'):    # when click first time!
            for devi in range(len(devlist)):
                with open(folderdir+'gpu_map.txt', 'a+') as f:
                    f.write(devlist[devi]['ip'])
                    for j in range(devlist[devi]['used_gpu']):
                        f.write(',2')
                    for k in range(int(gpus)):
                        f.write(',1')
                    for i in range(devlist[devi]['total_gpu']-devlist[devi]['used_gpu']-int(gpus)):
                        f.write(',0')
                    f.write('\n')
                    f.close()
        else:
            os.system("cat '' > %sgpu_map.txt"%(folderdir))
            count_j = 0
            for devi in range(len(devlist)):
                with open(folderdir+'gpu_map.txt', 'a+') as f:
                    f.write(devlist[devi]['ip'])
                    for j in range(devlist[devi]['used_gpu']):
                        f.write(',2')
                        count_j = j    
                    if count_j == (int(devlist[devi]['total_gpu'])-1):
                        pass
                    else:
                        for k in range(int(gpus)):
                            f.write(',1')
                    for i in range(devlist[devi]['total_gpu']-devlist[devi]['used_gpu']-int(gpus)):
                        f.write(',0')
                    f.write('\n')
                    f.close()

        return render.index1(ids,gpus)

'''
submit the net.prototxt  solver.prototxt  pyhton_layer.py
'''
class uploadfile:
    def GET(self):
        i = web.input()
        '''
        1. check the file name [.prototxt, .py ...]
        '''
        mid = i.get("mid")
        gpus = i.get("gpus")
        return render.indexupload(mid,gpus)

    def POST(self):
        filedir = '/home/ATS/file/'
        i = web.input()
        mid = i.get('mid')
        netf = i.get('netfname')
        solverf = i.get('solverfname')
        netfdata = i.get('netfdata')
        solverfdata = i.get('solverfdata')
        layerf = i.get('layerfname')
        layerfdata = i.get('layerfdata')
        gpus = i.get("gpus")
        lmdbf = i.get("lmdbf")
        
        wtdic = {}
        wtdic[netf] = netfdata
        wtdic[solverf] = solverfdata
        wtdic[layerf] = layerfdata

        new_net = "net: \"/mnt/home/ATS/traindir/" + mid + "/input/"    # pick out file/
        new_snapshot = "snapshot_prefix: \"/mnt/home/ATS/traindir/" + mid + "/output/"
        wtdic[solverf] = wtdic[solverf].replace("net: \"", new_net)
        wtdic[solverf] = wtdic[solverf].replace("snapshot_prefix: \"", new_snapshot)
        new_tsource1 = "\"path\":[\"/mnt/home/ATS/traindir/" + mid + "/mountdir/"
        new_tsource2 = "\"module: \"/mnt/home/ATS/traindir/" + mid + "/input/"
        wtdic[netf] = wtdic[netf].replace("\"path\":[\"", new_tsource1)
        wtdic[netf] = wtdic[netf].replace("module: \"", new_tsource2)
                  
        if os.path.exists(filedir + mid):
            try:
                for ks,vs in wtdic.items():
                    fdir = filedir+mid+'/input/'+ks
                    fout = open(fdir, 'wb')
                    fout.write(wtdic[ks])
                    fout.close()
                oscmd = "wget -r -nH -N -P /home/ATS/file/"+mid+"/mountdir/ %s"%(lmdbf)    #monite download Train Data using API , too slow,  use mount
                return oscmd
                os.system(oscmd)
                return render.indextrain(mid,gpus)
            except Exception, e:  
                return render.indextrain("error", gpus)
        else:
            return render.indextrain("error", gpus)



class train:
    def GET(self):
        folderdir = '/home/ATS/file/'
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        i = web.input()
        mid = i.get("mid")
        gpus = i.get("gpus")
        
         
        if os.path.exists(folderdir+mid):
            gpuparam = ""
            for i in range(int(gpus)):    #GPU using start from 0,1... after gpu mapping
                gpuparam  = gpuparam + str(i) +","
            gpuparam = gpuparam[:-1]
 
            cmd_dw = "wget -r -nH -N -P /home/ATS/traindir/ http://192.168.2.148:8002/"+mid+";"    #download the UID to the slaves
            '''
            read gpu_map.txt and config the --device    1,1,0,0 or 2,1,1,0 means req 2 GPUs, 1100 means mapping start with nvidia0, and 2110 means start with nvidia1 
            '''
            cmd_st = "rm -f /home/ATS/gpu_map.txt ; wget -r -nH -P /home/ATS/ http://192.168.2.148:8002/gpu_map.txt /home/ATS/ http://192.168.2.148:8002/gpu_map.py ; "    # all slaves should have /home/ATS/

            cmd_py = "python /home/ATS/gpu_map.py %s %s %s"%(gpus,mid,gpuparam)
            cmd = cmd_dw + cmd_st + cmd_py
            with open(folderdir+mid+'/conf.txt', 'r') as conf:
                lines = conf.readlines()[-1]
            cpus = lines.split(',')[1]
            gpus = lines.split(',')[2]
            mem = lines.split(',')[3]
            disk = lines.split(',')[4]
            instances = lines.split(',')[5]
            payload = {"id": mid, "cmd": cmd, "cpus": int(cpus), "gpus": int(gpus), "mem": float(mem), "disk": float(disk), "instances": int(instances)}
            headers = {"Content-type":"application/json"}
            posturl = "http://" + IP + ":8080/v2/apps"    #in fact, mesos decide to distribute
            req = requests.post(posturl, data=json.dumps(payload), headers=headers)
            
            '''
            get ip and gpus, write it to gpu_map.txt , start with ALL 1,0,0,0 -> 2,0,0,0
            '''
            gpusf = open(folderdir+'gpu_map.txt')
            lines = gpusf.readlines()
            gpusf.close()
            os.system("cat '' > %sgpu_map.txt"%(folderdir))
            for li in lines:
                li = li[:-1]
                flags = li.strip().split(',')
                for fi in range(len(flags)):
                    if flags[fi]== '1':
                        flags[fi] = '2'
                li = ""

                for ii in range(len(flags)):
                    li = li + flags[ii] + ","
                li = li[:-1]
                gpusfed = open(folderdir+'gpu_map.txt', 'a+')
                gpusfed.write(li+'\n')
                gpusfed.close()
            
            return render.indexlog(mid)
        else:
            return render.indexlog("error")

class showlog:
    def GET(self):
        #http://192.168.2.148:8084/dglearner/v1/showlog?mid=123
        logdir = '/home/ATS/traindir/'
        i = web.input()
        tid = i.get('mid')
        logpath = logdir + str(tid) + '/output/log'
        if not os.path.exists(logpath):
            return render.refresh("waitting......")
        else:
            with open(logpath) as f:
                log = f.read()
            return render.refresh(log)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()  






'''
	command = 'python ' + '/home/deepglint/caffe/ych/' +'ych_gpu.py'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
'''
'''
<!--
<form method="post" action="">
    <label for="txt_name2">Training cmd:</label></br>
    <textarea name="traincmd" rows="5" cols="180" >./build/tools/caffe train --solver /home/deepglint/caffe/examples/mnist/lenet_solver.prototxt --gpu 0 2>&1 | tee /home/deepglint/caffe/ych/mnist.log</textarea><br></br>
</form>
<form method="post" action="track">
    <label for="txt_name1">Choose Save file path:</label></br>
    <input type="text" name="savepath" value="/home/deepglint/caffe/ych/"  size="79"><br></br>
    <label for="txt_name">Edit Log file name:</label></br>
    <input type="text" name="logfilename" value="mnist.log"  size="79"><br></br>
    <input type="submit" id="2" value="Start Training" />
</form>
-->
'''


