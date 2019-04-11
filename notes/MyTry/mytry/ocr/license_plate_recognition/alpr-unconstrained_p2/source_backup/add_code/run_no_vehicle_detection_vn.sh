#!/bin/bash

check_file() 
{
	if [ ! -f "$1" ]
	then
		return 0
	else
		return 1
	fi
}

check_dir() 
{
	if [ ! -d "$1" ]
	then
		return 0
	else
		return 1
	fi
}


# Check if Darknet is compiled
check_file "darknet/libdarknet.so"
retval=$?
if [ $retval -eq 0 ]
then
	echo "Darknet is not compiled! Go to 'darknet' directory and 'make'!"
	exit 1
fi

lp_model="data/lp-detector/wpod-net_update1.h5"
input_dir=''
output_dir=''
csv_file=''


# Check # of arguments
usage() {
	echo ""
	echo " Usage:"
	echo ""
	echo "   bash $0 -i input/dir -o output/dir -c csv_file.csv [-h] [-l path/to/model]:"
	echo ""
	echo "   -i   Input dir path (containing JPG or PNG images)"
	echo "   -o   Output dir path"
	echo "   -c   Output CSV file path"
	echo "   -l   Path to Keras LP detector model (default = $lp_model)"
	echo "   -g   Log dir (default = outdir)"
	echo "   -h   Print this help information"
	echo ""
	exit 1
}

while getopts 'i:o:c:l:g:h' OPTION; do
	case $OPTION in
		i) input_dir=$OPTARG;;
		o) output_dir=$OPTARG;;
		c) csv_file=$OPTARG;;
		l) lp_model=$OPTARG;;
		g) log_dir=$OPTARG;;
		h) usage;;
	esac
done

if [ -z "$input_dir"  ]; then echo "Input dir not set."; usage; exit 1; fi
if [ -z "$output_dir" ]; then echo "Ouput dir not set."; usage; exit 1; fi
if [ -z "$csv_file"   ]; then echo "CSV file not set." ; usage; exit 1; fi
if [ -z "$log_dir"    ]; then $log_dir=$outdir         ; fi


# Check if input dir exists
check_dir $input_dir
retval=$?
if [ $retval -eq 0 ]
then
	echo "Input directory ($input_dir) does not exist"
	exit 1
fi

# Check if output dir exists, if not, create it
check_dir $output_dir
retval=$?
if [ $retval -eq 1 ]
then
	rm -rf $output_dir
fi
mkdir -p $output_dir

# Check if log dir exists, if not, create it
check_dir $log_dir
retval=$?
if [ $retval -eq 1 ]
then
	rm -rf $log_dir
fi
mkdir -p $log_dir

# End if any error occur
set -e

# Detect vehicles
python ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/no_vehicle_dectection.py $input_dir $output_dir
# for f in $input_dir/*.jpg;
# for fullpath in $input_dir/*.jpg
# do
#     filename="${fullpath##*/}"                      # Strip longest match of */ from start
#     dir="${fullpath:0:${#fullpath} - ${#filename}}" # Substring from 0 thru pos of filename
#     base="${filename%.[^.]*}"                       # Strip shortest match of . plus at least one non-dot char from end
#     ext="${filename:${#base} + 1}"                  # Substring from len of base thru end
#     # if [[ -z "$base" && -n "$ext" ]]; then          # If we have an extension and no base, it's really the base
#         # base=".$ext"
#         # ext=""
#     # fi
#     echo -e "$fullpath:\n\tdir  = \"$dir\"\n\tbase = \"$base\"\n\text  = \"$ext\""
# 	new_path=$output_dir/$base'_car.png'
# 	echo 'new_path = ' $new_path
# 	cp $fullpath $new_path


# done

# Detect license plates
python license-plate-detection.py $output_dir $lp_model

# OCR
python ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/license-plate-ocr.py $output_dir
# Draw output and generate list
python gen-outputs.py $input_dir $output_dir > $csv_file

shopt -s nullglob

lp_files=($output_dir/*_lp.png)
echo 'n_lp' ${#lp_files[@]}
imgs=($output_dir/*car.png)
echo 'n_img' ${#imgs[@]}


pred_filename="${csv_file##*/}"
pred_dir="${csv_file:0:${#csv_file} - ${#pred_filename}}"
# rm $output_dir'/evaluate_log.txt'
# rm $output_dir'/detection_evaluate_log.txt'
echo 'log_dir: '$log_dir
python ~/MySetting/staff/code/Librarys/evaluate/evaluate.py --indir=$input_dir --preddir=$pred_dir >> $log_dir'/evaluate_log.txt'
python ~/MySetting/staff/code/Librarys/evaluate/detection_evaluate.py --indir=$input_dir --preddir=$output_dir >> $log_dir'/detection_evaluate_log.txt'

# Clean files and draw output
# rm $output_dir/*_lp.png
rm $output_dir/*car.png
rm $output_dir/*_cars.txt
rm $output_dir/*_lp.txt
rm $output_dir/*_str.txt
