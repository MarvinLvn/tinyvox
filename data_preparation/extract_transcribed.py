import os
import argparse
from pathlib import Path
import soundfile as sf
import numpy as np
import pandas as pd


def extract_audio_chunks(recordings_path, annotations_path, output_path):
    # TO DO


def main():
    parser = argparse.ArgumentParser(
        description='Extract audio chunks from .wav files based on .cha with phonetic tiers.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--pairs',
        type=str,
        required=True,
        help='Path to the file containing (.wav,.cha) pairs'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to the folder where output will be stored'
    )

    args = parser.parse_args()

    # Convert to absolute paths
    pairs = pd.read_csv(args.pairs, sep='\t')
    print(pairs)
    exit()


if __name__ == "__main__":
    main()