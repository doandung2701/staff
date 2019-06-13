sed -i -e 's/10.0.0.4/'$privateIPGW'/g' etc/EInvoiceGW.conf
sed -i -e 's/10.0.0.4/'$privateIPGW'/g' conf/einvoice_utils.properties
sed -i -e 's/10.0.0.4/'$privateIPGW'/g' conf/ws_https.properties
sed -i -e 's/10.0.0.4/'$privateIPGW'/g' conf/ws.properties
sed -i -e 's:/opt/jdk1.8.0_151/bin/java:/usr/bin/java:g' etc/EInvoiceGW.conf
