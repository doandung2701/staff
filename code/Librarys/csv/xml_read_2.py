import xml.etree.ElementTree as ET 
import os
def main(file_path):
    file_path = os.path.expanduser(file_path) 
    tree = ET.parse(file_path)  
    root = tree.getroot()
    folder, filename, path, source, size, segmented = root[:6]
    # print(root[0])
    print('folder, filename, path, source, size, segmented = ', folder, filename, path, source, size, segmented)
    print()
    print('folder.text, filename.text, path.text, source.text, size.text , segmented.text = ', folder.text, filename.text, path.text, source.text, size.text , segmented.text )
    # print(root['folder'])

    for ob in root.findall('object'):
        name, bndbox = ob[0], ob[4]
        print('name.text, bndbox', name.text, bndbox)
        location = xmin, ymin, xmax, ymax = [int(e.text) for e in bndbox[:]]
        print('location: ', location)



if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file_path", help="file_path")
    args= vars(ap.parse_args())
    main(args["file_path"])