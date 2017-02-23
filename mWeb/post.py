# coding=utf-8
import urllib 
import urllib2
import json
import sys
import requests

def tst_upload(uploadurl):
    netf = '/home/ATS/upload/lenet_train_test.prototxt'
    solverf = '/home/ATS/upload/lenet_solver.prototxt'

    with open(netf) as f:
        netdata = f.read()
    f.close()
    with open(solverf) as f:
        solverdata = f.read()
    f.close()

    dic={"mid":"4kbh6yz5e19qzvzy", "netf":json.dumps({'fname':netf,'fdata':netdata}), "solverf":json.dumps({'fname':solverf,'fdata':solverdata})}
    data = urllib.urlencode(dic)
    req = urllib2.Request(uploadurl,data)
    res = urllib2.urlopen(req)
    print res.read()


def tst_post(posturl):
    values = {
    'cpus':1,
    'gpus':1,
    'mem':256,
    'disk':0,
    "instances":1
    }
    data = urllib.urlencode(values)
    req = urllib2.Request(posturl,data)
    res = urllib2.urlopen(req)
    print res.read()
    '''
    headers = {"Content-type":"application/json"}
    r = requests.post(posturl, data=json.dumps(cmd), headers=headers)
    print r.text
    '''

def tst_train(trainurl):
    trainid={"mid":"4kbh6yz5e19qzvzy"}
    data = urllib.urlencode(trainid)
    req = urllib2.Request(trainurl,data)
    res = urllib2.urlopen(req)
    print res.read()

if __name__ == '__main__':
    geturl='http://192.168.2.148:8084/dglearner/v1/getdevice'
    posturl='http://192.168.2.148:8084/dglearner/v1/reqresource'
    uploadurl='http://192.168.2.148:8084/dglearner/v1/uploadfile'
    trainurl='http://192.168.2.148:8084/dglearner/v1/train'
    inp = sys.argv[1]
    #tst_post(posturl)
    #tst_upload(uploadurl)
    #tst_train(trainurl)
    if inp == ('train'):
       tst_train(trainurl)
    elif inp == ('post'):
       tst_post(posturl)
    elif inp == ('upload'):
       tst_upload(uploadurl)
    else:
       print 'argvs error!'





