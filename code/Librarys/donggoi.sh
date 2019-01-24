project='zemcy_eye'
cd ..
tar -cvhf $project.tar  $project
folder=$project'_release'
rm -rf $folder
mkdir $folder
mv $project.tar $folder
cd $folder
tar -xvf $project.tar
rm $project.tar
cd $project
./setup.sh

