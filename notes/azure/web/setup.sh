sudo apt update
sudo apt install zip
sudo apt install openjdk-8-jdk
sudo apt install subversion
svn export https://github.com/cuongvomanh/staff/trunk/notes/azure/web
mv web tmp
unzip tomcat9999_azure_search.zip
cd tomcat9999_azure_search
vim ../tmp/env
source ../tmp/env
bash ../tmp/env_setup.sh

