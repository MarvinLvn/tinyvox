import os
import argparse
from chat_toolkit.cha import CHATFile
from chat_toolkit.parser import parse_chat_file
from pathlib import Path
from tqdm import tqdm

def load_cha_files(folder_path):
    cha_files = []
    for file_path in tqdm(folder_path.glob('**/*.cha')):
        chat_file = parse_chat_file(file_path)
        if chat_file:
            cha_files.append(chat_file)
        else:
            print(f"Failed to parse {file_path}")
    return cha_files

def main():
    parser = argparse.ArgumentParser(description="Load .cha files recursively from a folder")
    parser.add_argument("folder_path", help="Path to the folder containing .cha files")
    args = parser.parse_args()

    args.folder_path = Path(args.folder_path)
    cha_files = load_cha_files(args.folder_path)
    print(f"Loaded {len(cha_files)} .cha files")

    for chat_file in cha_files:
        print(f"File: {chat_file.filename}")
        print(f"Number of utterances: {len(chat_file.utterances)}")
        print("---")

if __name__ == "__main__":
    main()