if [$username == ''];
then
    username='cuongvm'
fi
server=$username'@10.198.54.231'
local_folder=$username'GPU'

sudo umount /home/cuong/Desktop/$local_folder
mkdir /home/cuong/Desktop/$local_folder
sshfs $server: /home/cuong/Desktop/$local_folder

ssh $server
