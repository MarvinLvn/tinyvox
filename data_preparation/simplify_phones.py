from ipa.mapping import simplifier
from ipa.categories import forbidden_characters
import pandas as pd
import argparse
import numpy as np
import panphon as panphon
import regex as re
from pathlib import Path

def simplify_phones(phones, ft, simplifier):
    if pd.isna(phones):
        return ''
    phones = ft.ipa_segs(phones)
    phones = [simplifier[sound] for sound in phones]
    return ' '.join(phones)

def main():
    parser = argparse.ArgumentParser(
        description='Simplify utterances by mapping from the input phonetic inventory to the target inventory in ipa/mapping.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to the file utterances.csv file'
    )

    args = parser.parse_args()
    args.data = Path(args.data)

    nb_output = len(np.unique(list(simplifier.values())))
    print(f"Found a mapping with {nb_output} output categories.")
    print(f"I will remove all utterances containing these forbidden strings: {forbidden_characters}.")

    data = pd.read_csv(args.data, sep='\t')
    original_duration = data['duration'].sum() / (1000*60*60)

    # 1) Remove forbidden characters
    data = data[data['phones'].notna() & (data['phones'] != '')]
    pattern = '|'.join(map(re.escape, forbidden_characters))
    data = data[~data['phones'].str.contains(pattern, regex=True)]

    # 2) Map to the target inventory
    ft = panphon.FeatureTable()
    data['simplified_phones'] = data['phones'].apply(lambda x: simplify_phones(x, ft, simplifier))

    # 3) Remove empty sentences
    data = data[data['simplified_phones'].notna() & (data['simplified_phones'] != '')]
    curr_duration = data['duration'].sum() / (1000*60*60)

    print("Went from %.1f hours of data to %.1f." % (original_duration, curr_duration))
    data.to_csv(args.data.parent / 'utterances2.csv', sep='\t', index=False)
    print(f"Wrote {args.data.parent / 'utterances2.csv'}.")

if __name__ == "__main__":
    main()
