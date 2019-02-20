import os
import filecmp
import json
def main(folder):
    compare_dict = {}
    subs = next(os.walk(folder))[1]
    n_sub = len(subs)
    for i in range(n_sub):
        sub1 =subs[i]
        files = next(os.walk(sub1))[2]
        n_file = len(files)
        compare_dict[sub1] = n_file
        for j in range(i+1, n_sub):
            sub2 = subs[j]
            comparison = filecmp.dircmp(sub1, sub2)
            n_common = len(comparison.common_files)
            compare_dict[sub1+'&'+sub2] = n_common
    json_strg = json.dumps(compare_dict)
    print(json_strg)
    with open(os.environ['HOME'] + '/MySetting/staff/code/Librarys/compare/data.json', 'w') as outfile:
        json.dump(json_strg, outfile)
    
    # print(compare_dict)
if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", help="folder")
    args= vars(ap.parse_args())
    print(args)
    main(args["folder"])