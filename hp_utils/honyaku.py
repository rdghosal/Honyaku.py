import os, sys

def to_staggered(infile):
    """Outputs csv or text file with side-by-side translations to a staggered format"""

    # Retrieve directory and filename    
    dir_, filename = os.path.split(infile)
    outfile = "staggered_" + filename
    in_contents = []

    # Read as list in order to iterate through and format each line
    with open(infile, "r", encoding="utf-8") as fin:
        in_contents = fin.readlines()
    
    # Ensure .txt output
    outfile = os.path.splitext(outfile)[0] + ".txt"
    dest = os.path.join(dir_, outfile)

    # Write out CSV contents, using header to label each line
    with open(dest, "w", encoding="utf-8") as fout:
        title, headers = in_contents[0], in_contents[1].rstrip() # Strip newline
        headers = headers.split(",")
        fout.write(title)
        for line in in_contents[2:]:
            if line.find(",") > -1:
                jp, eng = line.split(",")[0], line.split(",")[1].rstrip() # Strip newline
                fout.write(headers[0] + ": " + jp + "\n")
                fout.write(headers[1] + ": " + eng + "\n")
                fout.write("\n")

    print(f"{outfile} written in {dir_}")


def main():
    if len(sys.argv) < 2:
        print("USAGE: python honyaku.py <folder_path>")
        sys.exit(-1)
    
    folder = sys.argv[1]
    files = os.listdir(folder)

    for f in files:
        abspath = os.path.join(folder, f)
        to_staggered(abspath)

    sys.exit(0)


if __name__ == "__main__":
    main()