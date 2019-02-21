import os
def main(folder):
    for root, subFolder, files in os.walk(folder):
        print('#Root:',root)
        print('#subFolder:',subFolder)
        # print('#files:',files)
        for item in files:
            if item.endswith(".jpg") :
                fileNamePath = str(os.path.join(root,subFolder,item))
                print(fileNamePath)



if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", help="folder")
    args= vars(ap.parse_args())
    main(args["folder"])