import argparse
from pathlib import Path
import pandas as pd
import json

def main():
    parser = argparse.ArgumentParser(
        description='Extract phonetic inventory from metadata.csv',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--path', required=True,
                        help='Path to TinyVox (which contains metadata.csv).')

    args = parser.parse_args()
    args.path = Path(args.path)

    data = pd.read_csv(args.path / 'metadata.csv')
    all_phones = data['phones'].dropna()
    all_phonemes = ' '.join(all_phones).split()
    unique_phonemes = set(all_phonemes) - {'|'}

    json_file = args.path / 'unique_phonemes.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sorted(unique_phonemes), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()