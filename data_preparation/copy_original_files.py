import argparse
from pathlib import Path
import pandas as pd
import shutil
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(
        description='Simplify utterances by mapping from the input phonetic inventory to the target inventory in ipa/mapping.py and remove unwanted files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to the tinyvox folder'
    )
    parser.add_argument(
        '--original_path',
        type=str,
        default='/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora',
        help='Path to the folder where original files are'
    )

    args = parser.parse_args()
    args.data = Path(args.data)

    metadata_path = args.data / 'metadata.csv'
    metadata = pd.read_csv(metadata_path)
    original_files = metadata['original_audio_path'].unique()
    dest_dir = args.data / 'original'
    dest_dir.mkdir(parents=True, exist_ok=True)
    for original_file in tqdm(original_files):
        original_file = Path(original_file)
        new_filename = str(original_file.relative_to(args.original_path)).replace('/', '_')
        dest_path = dest_dir / new_filename
        shutil.copy(str(original_file), str(dest_path))

if __name__ == "__main__":
    main()
