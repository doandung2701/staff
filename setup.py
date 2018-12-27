virtualenv -p python3 p3env
#source p3env/bin/activate to use this python
./p3env/bin/pip3 install -r requirements.txt
./p3env/bin/pip3 install -i https://test.pypi.org/simple/ zemcy
sudo apt-get install curl
curl -o src/videostream.py https://raw.githubusercontent.com/cuongvomanh/staff/master/videostream.py
curl -o vni-full-standard.zip https://drive.google.com/file/d/1pnh_2rx53O4LEe364bN2mmZ6qPyAnDxo/view?usp=sharing
sudo apt-get install unzip
rm -rf vni-full-standard.zip 
unzip vni-full-standard.zip
./see.sh
