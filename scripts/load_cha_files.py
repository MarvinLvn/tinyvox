import os
import argparse
from chat_toolkit.cha import CHATFile
from chat_toolkit.parser import parse_chat_file
from pathlib import Path
from tqdm import tqdm

def load_cha_files(folder_path):
    cha_files = []
    i = 0
    for file_path in tqdm(folder_path.glob('**/*.cha')):
        print(file_path)

        chat_file = parse_chat_file(file_path)
        print(chat_file.is_automatic)
        if chat_file:
            cha_files.append(chat_file)
            #chat_file.print_header()
        else:
            print(f"Failed to parse {file_path}")

        i += 1
    return cha_files

def main():
    parser = argparse.ArgumentParser(description="Load .cha files recursively from a folder")
    parser.add_argument("folder_path", help="Path to the folder containing .cha files")
    args = parser.parse_args()

    args.folder_path = Path(args.folder_path)
    cha_files = load_cha_files(args.folder_path)
    print(f"Loaded {len(cha_files)} .cha files")


if __name__ == "__main__":
    main()