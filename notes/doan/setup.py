apt update
apt install sudo
sudo apt update && apt install -y libsm6 libxext6 libxrender-dev
sudo apt-get install libglib2.0-0

sudo apt install virtualenv
virtualenv -p python3 p3env
#source p3env/bin/activate to use this python
./p3env/bin/pip3 install -r requirements.txt
./p3env/bin/pip3 install -i https://test.pypi.org/simple/ zemcy==0.0.8
sudo apt-get install curl
curl -o src/videostream.py https://raw.githubusercontent.com/cuongvomanh/staff/master/videostream.py

# rm -f vni-full-standard.zip 
# curl -o vni-full-standard.zip https://drive.google.com/file/d/1pnh_2rx53O4LEe364bN2mmZ6qPyAnDxo/view?usp=sharing
# sudo apt-get install unzip
# unzip vni-full-standard.zip
# rm -f vni-full-standard.zip 
./see.sh
