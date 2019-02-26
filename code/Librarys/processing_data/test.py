import os
def main(folder):
    for root, subFolders, files in os.walk(os.path.expanduser(folder)):
        print('#Root:',root)
        for item in files:
            if item.endswith(".jpg") :
                fileNamePath = str(os.path.join(root,item))
                print(fileNamePath)



if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", help="folder")
    args= vars(ap.parse_args())
    main(args["folder"])