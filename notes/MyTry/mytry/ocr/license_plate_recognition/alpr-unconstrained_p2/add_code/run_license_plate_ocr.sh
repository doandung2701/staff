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
	echo "   -d   annotation dir path "
	echo "   -o   Output dir path"
	echo "   -c   Output CSV file path"
	echo "   -l   Path to Keras LP detector model (default = $lp_model)"
	echo "   -g   Log dir (default = outdir)"
	echo "   -s   out_size"
	echo "   -h   Print this help information"
	echo ""
	exit 1
}

while getopts 'i:o:c:l:g:s:d:h' OPTION; do
	case $OPTION in
		i) input_dir=$OPTARG;;
		o) output_dir=$OPTARG;;
		c) csv_file=$OPTARG;;
		l) lp_model=$OPTARG;;
		g) log_dir=$OPTARG;;
		s) out_size=$OPTARG;;
        d) des_dir=$OPTARG;;
		h) usage;;
	esac
done

if [ -z "$input_dir"  ]; then echo "Input dir not set."; usage; exit 1; fi
if [ -z "$output_dir" ]; then echo "Ouput dir not set."; usage; exit 1; fi
if [ -z "$csv_file"   ]; then echo "CSV file not set." ; usage; exit 1; fi
# if [ -z "$out_size"   ]; then echo "out_size not set." ; usage; exit 1; fi
if [ -z "$des_dir"   ]; then echo "des_dir not set." ; usage; exit 1; fi
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

for f in $input_dir/*.jpg; do cp $f $output_dir/$(basename $f .jpg)_lp.jpg; done
for f in $output_dir/*.jpg; do convert $f $output_dir/$(basename $f .jpg).png;done

# OCR
python ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/license-plate-ocr.py $output_dir
# Draw output and generate list
python ~/MySetting/staff/notes/MyTry/mytry/ocr/license_plate_recognition/alpr-unconstrained_p2/add_code/gen-outputs.py $input_dir $output_dir > $csv_file

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
python ~/MySetting/staff/code/Librarys/evaluate/evaluate.py --indir=$des_dir --preddir=$pred_dir >> $log_dir'/evaluate_log.txt'

# Clean files and draw output
# rm $output_dir/*_lp.png
rm $output_dir/*car.png
rm $output_dir/*_cars.txt
# rm $output_dir/*_lp.txt
rm $output_dir/*_str.txt
