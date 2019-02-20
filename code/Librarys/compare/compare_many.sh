if [$folder == ''];
then
    folder='.'
fi
python ~/MySetting/staff/code/Librarys/compare/compare_many.py --folder=$folder
http-server ~/MySetting/staff/code/Librarys/compare