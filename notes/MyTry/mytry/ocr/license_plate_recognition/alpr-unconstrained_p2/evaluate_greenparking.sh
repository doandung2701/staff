bash run.sh -i data/datasets/n_splited_and_convert_parking_data/fold_0_split/fold_1/GreenParking/  -o /tmp/output -c ~/MyOutput/ocr/license_plate_recognition/alpr-unconstrained/origin/n_splited_and_convert_parking_data/fold_0_split/fold_1/GreenParking/results.csv


python ~/MySetting/staff/code/Librarys/evaluate/evaluate.py --indir=data/datasets/n_splited_and_convert_parking_data/fold_0_split/fold_1/GreenParking/ --preddir=~/MyOutput/ocr/license_plate_recognition/alpr-unconstrained/origin/n_splited_and_convert_parking_data/fold_0_split/fold_1/GreenParking/ >> ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/origin_model_for_fold_0_split_fold_1_Greenparking.txt

