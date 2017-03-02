#wget http://192.168.2.119:/cuda/cuda8.0/cuda-repo-ubuntu1404-8-0-local_8.0.44-1_amd64.deb
#wget http://192.168.2.119:/cuda/cuda8.0/cudnn-8.0-linux-x64-v5.1.tgz

sudo  dpkg -i cuda-repo-ubuntu1404-8-0-local_8.0.44-1_amd64.deb
sudo apt-get update 
sudo apt-get install cuda -y

#scp -r zdb@192.168.2.111:/mnt/data1/zdb/data/downloads/test_cudnn/change_cudnn.sh .
tar xf cudnn-8.0-linux-x64-v5.1.tgz
mkdir -p cudnn_v51
mv cuda cudnn_v51

sudo sh change_cudnn.sh 51

