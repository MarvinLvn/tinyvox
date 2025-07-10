import os
import argparse
from pathlib import Path
import soundfile as sf
import numpy as np
from tqdm import tqdm
import pandas as pd

def extract_audio_chunk(recording_path, onset, offset, output_path):
   try:
       start_ms, end_ms = onset, offset

       # Open the audio file
       with sf.SoundFile(recording_path) as audio_file:
           # Convert milliseconds to samples
           sample_rate = audio_file.samplerate
           start_sample = int((start_ms / 1000) * sample_rate)
           end_sample = int((end_ms / 1000) * sample_rate)
           n_samples = end_sample - start_sample

           # Seek to the start position and read only the chunk we need
           audio_file.seek(start_sample)
           chunk = audio_file.read(n_samples)

           # Save the chunk
           sf.write(output_path, chunk, sample_rate)
           return 0  # Success

   except Exception as e:
       return 1  # Failure

def main():
    parser = argparse.ArgumentParser(
        description='Extract audio chunks from utterances2.csv',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--data', required=True,
                        help='Path to utterances2.csv containing phonetically transcribed utterances.')
    parser.add_argument('--out', required=True,
                        help='Path to output folder where extracted audio chunks will be saved.')
    args = parser.parse_args()
    args.out = Path(args.out)
    (args.out / 'audio').mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(args.data, sep='\t')
    metadata = []
    tot_failed = 0
    for idx, row in tqdm(data.iterrows()):
        dest_name = '_'.join([row['database'], row['corpus'],
                              Path(row['audio_path']).stem,
                              str(int(row['onset'])), str(int(row['offset']))
                              ]
                             ) + '.wav'
        output_path = args.out / 'audio' / dest_name
        is_failed = extract_audio_chunk(row['audio_path'], row['onset'], row['offset'], output_path)
        tot_failed += is_failed
        if is_failed == 0:
            metadata.append(
                {
                    'audio_filename': dest_name,
                    'original_audio_path': row['audio_path'],
                    'original_transcript_path': row['transcript_path'],
                    'language': row['language'],
                    'gender': row['gender'],
                    'file_design': row['file_design'],
                    'file_group': row['file_group'],
                    'file_activity': row['file_activity'],
                    'age_months': row['age_months'],
                    'phones': row['simplified_phones']
                }
            )

    metadata = pd.DataFrame(metadata)
    metadata.to_csv(args.out / 'metadata.csv', index=False)
    print(f"{100*tot_failed/len(data)} utterances failed to extract (out of audio bounds).")
    print("Done.")

if __name__ == "__main__":
    main()