project='zemcy_eye'
cd ..
tar -cvf $project.tar  $project
folder=$project'_release'
rm -rf $folder
mkdir $folder
mv $project.tar $folder
cd $folder
rm -rf $project
tar -xvf $project.tar
rm $project.tar
cd $project
./setup.sh

