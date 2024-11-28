import os
import argparse
import pandas as pd
import shutil


def copy_audio_files(recordings_path, annotations_path, mapping_csv, output_path):
    df = pd.read_csv(mapping_csv)
    mapping = {row['recording_filename']: row['raw_filename'].replace('.cha', '.wav').split('/')
               for _, row in df.iterrows()}

    os.makedirs(output_path, exist_ok=True)

    for ann_file in os.listdir(annotations_path):
        if not ann_file.endswith('.csv'): continue

        recording_id = '_'.join(ann_file.split('_')[:4])
        if recording_id not in mapping:
            print(f"Warning: No mapping found for {ann_file}")
            continue

        speaker, basename = mapping[recording_id]
        wav_path = os.path.join(recordings_path, 'raw', speaker, basename)

        if not os.path.exists(wav_path):
            print(f"Warning: Could not find recording {wav_path}")
            continue

        try:
            output_file = os.path.join(output_path, ann_file[:-4] + '.wav')
            shutil.copy2(wav_path, output_file)
            print(f"Successfully copied: {ann_file[:-4]}")

        except Exception as e:
            print(f"Error processing {wav_path}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Copy audio files with new naming convention.')
    parser.add_argument('--recordings', type=str, required=True,
                        help='Path to the recordings directory')
    parser.add_argument('--annotations', type=str, required=True,
                        help='Path to the annotations directory')
    parser.add_argument('--mapping', type=str, required=True,
                        help='Path to annotations.csv mapping file')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory for copied files')

    args = parser.parse_args()
    copy_audio_files(args.recordings, args.annotations, args.mapping, args.output)


if __name__ == "__main__":
    main()