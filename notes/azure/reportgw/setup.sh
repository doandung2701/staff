sudo apt update
sudo apt install zip
sudo apt install openjdk-8-jdk
sudo apt install subversion
svn export https://github.com/cuongvomanh/staff/trunk/notes/azure/reportgw
mv reportgw tmp
unzip tomcat8775.zip
cd tomcat8775

vim ../tmp/env
source ../tmp/env
bash ../tmp/env_setup.sh
