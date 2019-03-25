for f in *.csv;do a=${f//[.csv]/};python ../add_code/review_result.py --input_path=$(pwd)/$f --output_path=../report-20192503-1055/$a.jpg; done

#train
python ~/MySetting/staff/notes/MyTry/mytry/face_projects/insightface/add_code/train.py --data-dir=/home/cuongvm/Resources/datasets/faces/vn_celeb_face_recognition_lfw10/ --model-path=/home/cuongvm/tmp/tmpinsight2/model.pkl --idx2path=/home/cuongvm/tmp/tmpinsight2/idx2path.pkl --vector-dir=/home/cuongvm/tmp/tmpinsight2/vector/

#main
for t in 1.22 1.24 1.26 1.28 1.30 1.32 1.20 1.18;do  python ~/MySetting/staff/notes/MyTry/mytry/face_projects/insightface/add_code/main_v2.py --data-dir=/home/cuongvm/Resources/datasets/faces/vn_celeb_face_recognition_lfw_final_test/ --model-path=/home/cuongvm/tmp/tmpinsight2/model.pkl --idx2path=/home/cuongvm/tmp/tmpinsight2/idx2path.pkl --known-vector-dir=/home/cuongvm/tmp/tmpinsight2/vector/ --ver-vector-dir=/home/cuongvm/tmp/tmpinsight2/vector_test/ --threshold=$t --k=5 --output=/home/cuongvm/MySetting/staff/notes/MyTry/mytry/face_projects/insightface/submission_20192503-1055/${t//['.']/''}.csv --batch-size=1000 --tree-path=/home/cuongvm/tmp/tmpinsight2/tree.pkl; done