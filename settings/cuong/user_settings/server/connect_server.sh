if [$username == ''];
then
    username='cuongvm'
fi
if [$server == ''];
then
    server='10.198.54.231'
fi
url=$username'@'$server
echo $url
ssh $url