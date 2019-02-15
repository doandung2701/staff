if [$username == ''];
then
    username='cuongvm'
fi
if [$server == ''];
then
    server='10.198.54.231'
fi
url=$username'@'$server
local_folder=$username$server

sudo umount /home/cuong/Desktop/$local_folder
mkdir /home/cuong/Desktop/$local_folder
sshfs $url: /home/cuong/Desktop/$local_folder

ssh $url
