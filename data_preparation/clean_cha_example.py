from pathlib import Path

import pandas as pd
from tqdm import tqdm

from chat_toolkit.cleaner import *
from chat_toolkit.parser import parse_chat_file


def clean_cha(cha_paths):
    cleaner = ChatCleaner()
    nb_missing = 0
    for cha_path in tqdm(cha_paths):
        print(cha_path)
        cha_file = parse_chat_file(cha_path)
        for dirty_s in cha_file.utterances:
            clean_s = cleaner.clean(dirty_s.content)
            print(f'{dirty_s.content} --> {clean_s}')
            #print(repr(dirty_s.content))
            dirty_s.content = clean_s
        nb_missing += cha_file.missing_timestamps
    print(f"nb missing = {nb_missing}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for sampling (default: 42)')
    args = parser.parse_args()

    matched = pd.read_csv(PAIRS_PATH, sep='\t')
    matched = matched.sample(n=500, random_state=args.seed)

    clean_cha(matched['transcript'])
