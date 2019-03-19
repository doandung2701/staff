#!/bin/bash

config_path=''

# Check # of arguments
usage() {
	echo ""
	echo " Usage:"
	echo ""
	echo "   bash $0 -c config_path [-h] :"
	echo ""
	echo "   -c   Config path"
	echo "   -g   Log dir (default = outdir)"
	echo "   -h   Print this help information"
	echo ""
	exit 1
}

while getopts 'c:h' OPTION; do
	case $OPTION in
		c) config_path=$OPTARG;;
		g) log_dir=$OPTARG;;
		h) usage;;
	esac
done

if [ -z "$config_path"  ]; then echo "config_path not set."; usage; exit 1; fi


rm recognition/config.py
cp $config_path recognition/config.py

CUDA_VISIBLE_DEVICES='0'  python -u recognition/train.py --network r100 --loss arcface --dataset emore