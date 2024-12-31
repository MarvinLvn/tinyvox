from pathlib import Path

import pandas as pd
from tqdm import tqdm

from chat_toolkit.cleaner import *
from chat_toolkit.parser import parse_chat_file


def clean_cha(cha_paths, DATA_PATH, PREPARED_PATH):
    cleaner = ChatCleaner()
    for cha_path in tqdm(cha_paths):
        cha_path = PREPARED_PATH / Path(cha_path).relative_to(DATA_PATH)
        cha_file = parse_chat_file(cha_path)
        for dirty_s in cha_file.utterances:
            dirty_s.content = cleaner.clean(dirty_s.content)
        output_path = Path(cha_path).with_name(Path(cha_path).stem + '_cleaned.cha')
        cha_file.write(output_path, dependent_tier=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    PAIRS_PATH = Path('/scratch2/mlavechin/ASR_longforms/pairs/matched.txt')
    DATA_PATH = Path('/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora')
    PREPARED_PATH = Path('/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/prepared')
    matched = pd.read_csv(PAIRS_PATH, sep='\t')

    clean_cha(matched['transcript'], DATA_PATH, PREPARED_PATH)
