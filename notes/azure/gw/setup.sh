sudo apt update
sudo apt install zip
sudo apt install openjdk-8-jdk
sudo apt install subversion
svn export https://github.com/cuongvomanh/staff/trunk/notes/azure/gw
mv gw tmp
unzip EInvoiceGW.zip
cd EInvoiceGW
vim ../tmp/env
source ../tmp/env
bash ../tmp/env_setup.sh
