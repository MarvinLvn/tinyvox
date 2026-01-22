from pathlib import Path
import pandas as pd
from tqdm import tqdm
import argparse
from chat_toolkit.parser import parse_chat_file

# Example call to extract pairs of (.wav, .cha) that have been phonetically transcribed
# python data_preparation/create_pairs.py --data_path /scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora --output_dir phonetically_transcribed_pairs --required_tiers pho xwb xpho

def match_files(data_path, required_tiers=None):
    print("Parsing CHAT files.")
    cha_files = data_path.glob('**/*.cha')

    all_chat_files = [
        chat_file for chat_file in tqdm(
            (parse_chat_file(f) for f in cha_files),
            desc="Parsing CHAT files"
        ) if chat_file is not None
    ]

    invalid_tier_filenames = []
    if required_tiers:
        print(f"Filtering for files containing tiers: {', '.join(required_tiers)}")
        filtered_files = [(chat_file, any(tier in chat_file.found_tiers for tier in required_tiers))
                          for chat_file in all_chat_files]
        valid_tier_files = [file for file, has_tier in filtered_files if has_tier]
        all_chat_files = valid_tier_files
        invalid_tier_filenames = [str(file.filename) for file, has_tier in filtered_files if not has_tier]

    # Filter automatic transcripts
    chat_files = [f for f in all_chat_files if not f.is_automatic]
    automatic_filenames = [f.filename for f in all_chat_files if f.is_automatic]

    # Match files
    matched = []
    unmatched = []
    corpus_list = list(data_path.glob('**/*.zip'))

    print("Matching audio files with their transcript")
    for zip_file in tqdm(corpus_list, desc="Processing corpora"):
        corpus_dir = zip_file.with_suffix('')

        # Build WAV files dictionary
        wav_files = {}
        for wav_path in corpus_dir.glob('**/*.wav'):
            wav_files.setdefault(wav_path.stem, []).append(wav_path)

        # Match CHAT files
        corpus_chat_files = [f for f in chat_files if f.filename.is_relative_to(corpus_dir)]
        for chat_file in corpus_chat_files:
            chat_stem = Path(chat_file.filename).stem
            if chat_stem in wav_files:
                matching_wavs = wav_files[chat_stem]
                valid_matches = [w for w in matching_wavs
                                 if set(str(w.parent).split('/')).issuperset(
                        set(str(chat_file.filename.parent).split('/')))]

                if valid_matches:
                    same_dir_matches = [w for w in valid_matches
                                        if w.parent == chat_file.filename.parent]
                    if len(chat_file.utterances) > 0:
                        if len(same_dir_matches) == 1:
                            matched.append({
                                'transcript': str(chat_file.filename),
                                'audio': str(same_dir_matches[0]),
                                'corpus': corpus_dir.name
                            })
                        else:
                            matched.append({
                                'transcript': str(chat_file.filename),
                                'audio': str(valid_matches[0]),
                                'corpus': corpus_dir.name
                            })
                else:
                    unmatched.append(str(chat_file.filename))
            else:
                unmatched.append(str(chat_file.filename))

    return matched, unmatched, automatic_filenames, invalid_tier_filenames


def save_results(output_dir, matched, unmatched, automatic, invalid_tier):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Save matched pairs
    pd.DataFrame(matched).to_csv(
        output_dir / 'matched.txt',
        sep='\t',
        index=False
    )

    # Save unmatched and automatic files
    with open(output_dir / 'unmatched.txt', 'w') as f:
        f.write('\n'.join(unmatched))

    with open(output_dir / 'automatic.txt', 'w') as f:
        f.write('\n'.join(str(p) for p in automatic))

    with open(output_dir / 'invalid_tier.txt', 'w') as f:
        f.write('\n'.join(str(p) for p in invalid_tier))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Match CHAT files with their corresponding audio files')
    parser.add_argument('--data_path', type=str,
                        default='/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora',
                        help='Path to the downloaded corpora')
    parser.add_argument('--output_dir', type=str, default='phonetically_transcribed_pairs',
                        help='Directory to save output files')
    parser.add_argument('--required_tiers', type=str, nargs='+',
                        help='List of dependent tiers that must be present in the CHAT files (e.g., xphon xmod)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode with limited data')
    args = parser.parse_args()

    # Convert data_path to Path object
    data_path = Path(args.data_path)

    # Handle debug mode
    if args.debug:
        print("Running in DEBUG mode")
        # Optionally override data_path in debug mode
        debug_path = Path('/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora_small')
        if debug_path.exists():
            data_path = debug_path
            print(f"Using debug data path: {data_path}")

    print(f"Using data path: {data_path}")

    # Run file matching process
    matched, unmatched, automatic, invalid_tier = match_files(data_path, args.required_tiers)

    # Save results
    save_results(args.output_dir, matched, unmatched, automatic, invalid_tier)

    # Print summary
    print("\nResults Summary:")
    print(f"Matched pairs: {len(matched)}")
    print(f"Invalid tiers (if provided): {len(invalid_tier)}")
    print(f"Unmatched transcripts: {len(unmatched)}")
    print(f"Automatic transcripts: {len(automatic)}")


if __name__ == '__main__':
    main()
