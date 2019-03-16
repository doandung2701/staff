python train-detector.py --model models/eccv-model-scracth --name 20190403-1406 --train-dir data/datasets/n_splited_and_convert_packing_data/fold_0_split/fold_0/car_long/  --output-dir models/20190403-1406 -op Adam -lr .001 -its 100000 -bs 32

bash run.sh -i data/datasets/n_splited_and_convert_parking_data/fold_0_split/fold_1/car_long/ -l models/20192702-1822/20192702-1822_final.h5 -o /tmp/output -c ~/MyOutput/ocr/license_plate_recognition/alpr-unconstrained/20192702-1822/n_splited_and_convert_parking_data/fold_0_split/fold_1/car_long/results.csv

python ~/MySetting/staff/code/Librarys/evaluate/evaluate.py --indir=data/datasets/n_splited_and_convert_parking_data/fold_0_split/fold_1/car_long/ --preddir=~/MyOutput/ocr/license_plate_recognition/alpr-unconstrained/20192702-1822/n_splited_and_convert_parking_data/fold_0_split/fold_1/car_long/ >> ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/20192702-1822_model_for_fold_0_split_fold_0_car_long.txt
