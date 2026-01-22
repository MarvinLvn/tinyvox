from ipa.mapping import simplifier
from ipa.categories import forbidden_characters
import pandas as pd
import argparse
import numpy as np
import panphon as panphon
import regex as re
from pathlib import Path

# Decisions about whether to include corpora/files were taken by listening to randomly sampled utterances
# and verifying if they're aligned with the audio.
forbidden_corpora = ['Hunkeler', 'PAIDUS-German', 'PAIDUS-Spanish', 'PhonBLA', 'VYSA', 'Warnier']
forbidden_files = ['/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Aaron/010806.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000702.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000723.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000803.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000818.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000906.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000923a.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/000923b.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/001010.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/001022.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/001119.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/001128.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010007.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010019.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010108.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010116.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010220b.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Micah/010319.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Nick/010303.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Nick/010317.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Paxton/001108.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Paxton/010021.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Paxton/010119b.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rachel/000720.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010202b.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010224.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010316.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010327.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010404.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010408.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010414.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Eng-NA/Davis/Rebecca/010417.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/000719.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/000907.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/000921.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/001004.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/001101.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Baptiste/011108.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Emma/010103.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Emma/010117.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Emma/011004.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Esteban/010016.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/010624.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/011010.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/011103.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/011116.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/020000.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/KernFrench/Jules/020029.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/Lyon/Theotime/11019a.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/Lyon/Theotime/20027a.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/French/Lyon/Theotime/20027b.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Romance/Portuguese/Ramalho/2-3/A23.wav',
                   '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora/phon/Biling/ChildL2/040026.wav']

def simplify_phones(phones, ft, simplifier):
    if pd.isna(phones):
        return ''

    # Remove successive white spaces
    phones = ' '.join(phones.split())
    # Split according to white space (words/breathing patterns)
    word_list = phones.split(' ')

    # Segment into IPA
    word_list = [ft.ipa_segs(word) for word in word_list]

    # Simplify
    word_list = [
        ' '.join([
            simplifier[phone] for phone in word
        ])
        for word in word_list if len(word) > 0
    ]
    return ' | '.join(word_list) + ' |' # Add final | since it marks word/breathing pattern boundaries

def main():
    parser = argparse.ArgumentParser(
        description='Simplify utterances by mapping from the input phonetic inventory to the target inventory in ipa/mapping.py and remove unwanted files',
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
    data['phones'] = data['phones'].str.replace(r'\s+', ' ', regex=True)
    data = data[(data['phones'].notna()) & (data['phones'] != '') & (data['phones'] != ' ')]
    pattern = '|'.join(map(re.escape, forbidden_characters))
    data = data[~data['phones'].str.contains(pattern, regex=True)]

    # 2) Map to the target inventory
    ft = panphon.FeatureTable()
    data['simplified_phones'] = data['phones'].apply(lambda x: simplify_phones(x, ft, simplifier))

    # 3) Remove empty sentences
    data = data[data['simplified_phones'].notna() & (data['simplified_phones'] != '')]

    # 4) Remove forbidden corpora
    bef_len = len(data.corpus.unique())
    data = data[~data.corpus.isin(forbidden_corpora)]
    aft_len = len(data.corpus.unique())
    assert bef_len - aft_len == len(forbidden_corpora)

    # 5) Remove forbidden files
    bef_len = len(data.audio_path.unique())
    data = data[~data.audio_path.isin(forbidden_files)]
    aft_len = len(data.audio_path.unique())
    assert bef_len - aft_len == len(forbidden_files)

    # 6) Remove utterances > 10sec
    data = data[data['duration'] < 10000]

    # 7) Remove utterances < .05sec (50ms)
    data = data[data['duration'] > 50]

    # 8) Remove kids older than 8 yo
    data = data[data['age_months'] < 96]
    curr_duration = data['duration'].sum() / (1000*60*60)

    print("Went from %.1f hours of data to %.1f." % (original_duration, curr_duration))
    data.to_csv(args.data.parent / 'utterances2.csv', sep='\t', index=False)
    print(f"Wrote {args.data.parent / 'utterances2.csv'}.")

if __name__ == "__main__":
    main()
