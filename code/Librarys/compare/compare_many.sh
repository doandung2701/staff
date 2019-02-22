if [$folder == ''];
then
    folder='.'
fi
if [$combine == ''];
then
    is_combine='True'
fi
libpath=~/MySetting/staff/code/Librarys
tmp_folder=~/tmp/trash/folder
rm -rf $tmp_folder
mkdir -p $tmp_folder
if $is_combine=='True'
    do
    for subfolder in $(ls -d */); do python $libpath/processing_data/preprocessing_and_combine_data.py --indir=$subfolder --outdir=$tmp_folder/$subfolder; done
    done
#python $libpath/combine_data.py --indir=$folder --outdir=$tmp_folder
python $libpath/compare/compare_many.py --folder=$tmp_folder
$libpath/compare/node_modules/.bin/http-server ~/MySetting/staff/code/Librarys/compare 
