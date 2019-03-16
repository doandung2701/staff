import os
from xml.dom import minidom
def main(file_path):
    file_path = os.path.expanduser(file_path)
    xmldoc = minidom.parse(file_path)
    itemlist = xmldoc.getElementsByTagName('object')
    for item in itemlist:
        name = item.attributes['name'].value

        print('name = ', name)

    print(len(itemlist))

if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file_path", help="file_path")
    args= vars(ap.parse_args())
    main(args["file_path"])
