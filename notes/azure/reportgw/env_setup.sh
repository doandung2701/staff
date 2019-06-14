sed -i -e 's/10.60.108.210/'$publicIPReportGW'/g' conf/report_config.properties
sed -i -e 's/10.60.108.210/'$publicIPReportGW'/g' etc/config.properties
sed -i -e 's/10.60.108.210/'$publicIPReportGW'/g' etc/ReportGW.conf
sed -i -e 's:/u01/hddt:'$HOME':g' conf/report_config.properties
