# coding=utf-8
import sys
import os
import argparse

def DoMount(sdir, ddir):
    #os.system("echo \"ych.123\" | sudo -S docker ps")
    cmd = ("echo 'dell@2016'|sudo -S sshfs -o cache=yes,allow_other %s %s" %(sdir,ddir))
    try:
        res = os.system(cmd)
        if res == 0:
            print "DoMount return success!"
        else:
            print "error"
    except Exception,e:
        print Exception, ":", e

def DoUnmount(ddir):
    #"fusemount –u /home/user/code"
    cmd = ("sudo fusermount -u %s" %(ddir))
    try:
        res = os.system(cmd)
        if res == 0:
            print "DoUnmount return success!"
        else:
            print "error"
    except Exception,e:
        print Exception, ":", e

def CreateFolder(owner, date):
    if owner == None or date == None:
        return 
    else:
        owner_date = owner + '_' + date
        if not os.path.exists(owner_date):
            os.makedirs(owner_date)
            print "creat folder %s successful!" %owner_date
        else:
            print "folder %s was already existed!" %owner_date
            return
        if not os.path.exists(owner_date + '/input'):
            os.makedirs(owner_date + '/input')
        if not os.path.exists(owner_date + '/output'):
            os.makedirs(owner_date + '/output')
        if not os.path.exists(owner_date + '/mountdir'):
            os.makedirs(owner_date + '/mountdir')

def parse_args():
    parser = argparse.ArgumentParser(description='AutoTrainsystem')
    parser.add_argument('--owner', dest='owner', help='the folder\'s owner')
    parser.add_argument('--date', dest='date', help='the creating date')
    parser.add_argument('--sdir', dest='sdir', help='the remote server\'s data dir')
    parser.add_argument('--ddir', dest='ddir', help='the host\'s data dir')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print args.owner,args.date,args.sdir,args.ddir
    CreateFolder(args.owner,args.date)
    DoMount(args.sdir,args.ddir)    #--sdir=superhui@192.168.1.127:/home/superhui/AutoTrainsys/m_data --ddir=/home/dell/chaohuiyu/AutoTrainsys/ych_170210/mountdir
    #DoUnmount()

'''
python Createfolder.py --owner=ych --date=170213 --sdir=superhui@192.168.5.115:/home/superhui/AutoTrainsys/m_data --ddir=/home/dell/chaohuiyu/AutoTrainsys/ych_170213/mountdir
'''


