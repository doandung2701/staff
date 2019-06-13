source ../tmp/env
sed -i -e 's/13.67.55.66/'$publicIPWeb'/g' webapps/ROOT/WEB-INF/classes/cas_en_US.properties
sed -i -e 's:/home/cuongvm12:'$HOME':g' webapps/ROOT/WEB-INF/classes/config.properties
