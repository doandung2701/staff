import filecmp
def compare_two(folder1, folder2):
    comparison = filecmp.dircmp(folder1, folder2)
    # comparison.report_full_closure()
    # print(comparison.common_files)
    # print(comparison.diff_files)
    # print(comparison.left_only)
    print(comparison.right_only)
    # return 
if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder1", help="folder1")
    ap.add_argument("--folder2", help="folder2")
    args= vars(ap.parse_args())
    compare_two(args["folder1"], args["folder2"])