import filecmp
def main(folder1, folder2, folder3):
    comparison = filecmp.dircmp(folder1, folder3)
    comparison.report_full_closure()
if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder1", help="folder1")
    ap.add_argument("--folder2", help="folder2")
    ap.add_argument("--folder3", help="folder3")
    args= vars(ap.parse_args())
    print(args)
    main(args["folder1"], args["folder2"], args["folder3"])