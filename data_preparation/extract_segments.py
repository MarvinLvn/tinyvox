import argparse
from pathlib import Path
import soundfile as sf
import numpy as np
from tqdm import tqdm
import pandas as pd
from pyannote.core import Segment, Timeline

# python data_preparation/extract_segments.py --data phonetically_transcribed_pairs/utterances2.csv --out TinyVox --rttm_folder ../voice_type_classifier/output_voice_type_classifier/TinyVox_rttm --debug

def extract_audio_chunk(recording_path, onset, offset, output_path):
   try:
       start_ms, end_ms = onset, offset

       # Open the audio file
       with sf.SoundFile(recording_path) as audio_file:
           # Convert milliseconds to samples
           sample_rate = audio_file.samplerate
           start_sample = int((start_ms / 1000) * sample_rate)
           end_sample = int((end_ms / 1000) * sample_rate)

           if start_sample >= len(audio_file) or end_sample > len(audio_file):
               return 1

           n_samples = end_sample - start_sample
           # Seek to the start position and read only the chunk we need
           audio_file.seek(start_sample)
           chunk = audio_file.read(n_samples)

           # Save the chunk
           sf.write(output_path, chunk, sample_rate)
           return 0  # Success

   except Exception as e:
       return 1  # Failure

def load_rttm(rttm_folder, debug=False):
    print("Loading RTTM files")
    rttm_data = []
    for rttm_file in tqdm(rttm_folder.glob('**/*.rttm')):
        try:
            data = pd.read_csv(rttm_file, sep=' ', header=None)
        except pd.errors.EmptyDataError:
            continue

        data=data[[1, 3, 4, 7]]
        data.columns = ['filepath', 'onset', 'duration', 'speaker_type']
        data = data[(data.speaker_type == 'KCHI') | (data.speaker_type == 'CHI')]
        data['speaker_type'] = 'KCHI' # We merge KCHI and CHI into one class
        data['subpath'] =  Path(rttm_file.relative_to(rttm_folder)).parent.with_suffix('.wav')
        data['offset'] = data['onset'] + data['duration']
        rttm_data.append(data)
        if debug:
            break
    rttm_data = pd.concat(rttm_data, ignore_index=True)
    return rttm_data

def create_annotation(data):
    segments = [Segment(onset, offset) for onset, offset in zip(data['onset'], data['offset'])]
    timeline = Timeline(segments=segments)
    return timeline.support()

def find_overlapping_utterances(manual_corpus, rttm_corpus):
    print("Computing overlap between manual and automatic annotation.")
    manual_corpus['onset'] /= 1000
    manual_corpus['offset'] /= 1000
    manual_corpus['with_vad_onset'] = np.nan
    manual_corpus['with_vad_offset'] = np.nan
    filepaths = rttm_corpus['subpath'].unique()
    for filepath in tqdm(filepaths):
        manual_data = manual_corpus[manual_corpus['subpath'] == filepath][['onset', 'offset', 'speaker_type']]
        rttm_data = rttm_corpus[rttm_corpus['subpath'] == filepath][['onset', 'offset', 'speaker_type']]
        rttm_timeline = create_annotation(rttm_data)
        for idx, row in manual_data.iterrows():
            manual_segment = Segment(row['onset'], row['offset'])
            subsegment = rttm_timeline.crop(manual_segment, mode='intersection').extent()
            if subsegment.start != subsegment.end:
                manual_corpus.loc[idx, 'with_vad_onset'] = 1000*subsegment.start
                manual_corpus.loc[idx, 'with_vad_offset'] = 1000*subsegment.end
    manual_corpus['onset'] *= 1000
    manual_corpus['offset'] *= 1000
    return manual_corpus

def main():
    parser = argparse.ArgumentParser(
        description='Extract audio chunks from utterances2.csv',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--data', required=True,
                        help='Path to utterances2.csv containing phonetically transcribed utterances.')
    parser.add_argument('--out', required=True,
                        help='Path to output folder where extracted audio chunks will be saved.')
    parser.add_argument('--rttm_folder', required=False, default=None,
                        help='Path to output folder containing VTC-generated .rttm files. If provided, will extract speech segments'
                             'based on the intersection from human (manual but can have imprecise boundaries) and VTC annotation (automatic).')
    parser.add_argument('--debug', action='store_true',
                        help='If activated, will load only one file (only used if --rttm_folder is provided).')

    args = parser.parse_args()
    args.out = Path(args.out)
    args.rttm_folder = Path(args.rttm_folder) if args.rttm_folder is not None else None
    (args.out / 'audio').mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(args.data, sep='\t')
    data_path = '/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora'
    data['subpath'] = data['audio_path'].apply(lambda path: Path(path).relative_to(data_path))
    if args.rttm_folder is not None:
        rttm_data = load_rttm(args.rttm_folder, args.debug)
        data = find_overlapping_utterances(data, rttm_data)
        (args.out / 'audio_with_vad').mkdir(parents=True, exist_ok=True)

    metadata = []
    tot_failed = 0
    print("Extracting segments...")
    for idx, row in tqdm(data.iterrows()):
        dest_name = '_'.join([str(row['subpath'].with_suffix('')).replace('/', '_'),
                              "{:08d}".format(int(row['onset'])),
                              "{:08d}".format(int(row['offset']))
                              ]
                             ) + '.wav'
        output_path = args.out / 'audio' / dest_name
        is_failed = extract_audio_chunk(row['audio_path'], row['onset'], row['offset'], output_path)
        tot_failed += is_failed
        if is_failed == 0:
            metadata_row = {
                    'audio_filename': dest_name,
                    'original_audio_path': row['audio_path'],
                    'original_transcript_path': row['transcript_path'],
                    'language': row['language'],
                    'gender': row['gender'],
                    'file_design': row['file_design'],
                    'file_group': row['file_group'],
                    'file_activity': row['file_activity'],
                    'age_months': row['age_months'],
                    'phones': row['simplified_phones'],
                    'sentence': row['content'],
                    'child_pseudoid': f"{row['corpus']}_{row['speaker_name']}",
                    'onset': int(row['onset']),
                    'offset': int(row['offset'])
                }
            if 'with_vad_onset' in row.index and pd.notna(row['with_vad_onset']):
                # If rttm annotations are provided, we also extract the intersection of manual & automatic annotations
                output_path = args.out / 'audio_with_vad' / dest_name
                extract_audio_chunk(row['audio_path'], row['with_vad_onset'], row['with_vad_offset'], output_path)
                metadata_row = {
                    **metadata_row,
                    'with_vad_onset': int(row['with_vad_onset']),
                    'with_vad_offset': int(row['with_vad_offset'])
                }
            metadata.append(metadata_row)
    metadata = pd.DataFrame(metadata)

    for col in ['onset', 'offset', 'with_vad_onset', 'with_vad_offset']:
        if col in metadata.columns:
            metadata[col] = metadata[col].astype('Int64')

    metadata.to_csv(args.out / 'metadata.csv', index=False)
    print(f"{100*tot_failed/len(data)} utterances failed to extract (out of audio bounds).")
    print("Done.")

if __name__ == "__main__":
    main()