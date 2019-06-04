rm -rf ~/Working/Viettel/tomcat/apache-tomcat-8.5.41/webapps/AzureSearchSample-0.0.1-SNAPSHOT.war
rm -rf ~/Working/Viettel/tomcat/apache-tomcat-8.5.41/webapps/AzureSearchSample-0.0.1-SNAPSHOT
mvn package
cp  target/AzureSearchSample-0.0.1-SNAPSHOT.war ~/Working/Viettel/tomcat/apache-tomcat-8.5.41/webapps/
cp -r target/AzureSearchSample-0.0.1-SNAPSHOT ~/Working/Viettel/tomcat/apache-tomcat-8.5.41/webapps/
~/Working/Viettel/tomcat/apache-tomcat-8.5.41/bin/startup.sh
tail -f -n 100 ~/Working/Viettel/tomcat/apache-tomcat-8.5.41/logs/catalina.out
