import csv
def main(file_path):
    csv_file=open(file_path, "r")
    reader = csv.reader(csv_file)
    for row in reader:
        print(" | ".join(row[:]))
if __name__=='__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file_path", help="file_path")
    args= vars(ap.parse_args())
    main(args["file_path"])
