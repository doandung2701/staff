
#240x80
for VARIABLE in 60x20
do
    bash ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/run_no_vehicle_detection_vn_ch_size.sh -i data/datasets/n_splited_and_convert_parking_data/fold_0_split/fold_1/GreenParking/ -o tmp/output/ -c ~/tmp/output/results.csv -s $VARIABLE -g ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/no_vehicle_detection/$VARIABLE 

done