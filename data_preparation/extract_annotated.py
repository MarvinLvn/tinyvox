import os
import argparse
from pathlib import Path
import soundfile as sf
import numpy as np


def extract_audio_chunks(recordings_path, annotations_path, output_path):
    """
    Extract audio chunks based on annotation files.

    Args:
        recordings_path (str): Path to the folder containing WAV recordings
        annotations_path (str): Path to the folder containing annotation files
        output_path (str): Path where extracted audio chunks will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Get all annotation files
    annotation_files = [f for f in os.listdir(annotations_path) if f.endswith('.csv')]

    for ann_file in annotation_files:
        # Parse annotation filename
        # Example: 123743-6035_1_18600000_18720000.csv
        base_name = ann_file[:-4]  # Remove .csv extension
        parts = base_name.split('_')
        recording_id = '_'.join(parts[:-2])  # 123743-6035_1
        start_ms = int(parts[-2])  # 18600000
        end_ms = int(parts[-1])  # 18720000

        # Find corresponding WAV file
        wav_file = f"{recording_id}.wav"
        wav_path = os.path.join(recordings_path, wav_file)

        if not os.path.exists(wav_path):
            print(f"Warning: Could not find recording {wav_file} for annotation {ann_file}")
            continue

        try:
            # Open the audio file
            with sf.SoundFile(wav_path) as audio_file:
                # Convert milliseconds to samples
                sample_rate = audio_file.samplerate
                start_sample = int((start_ms / 1000) * sample_rate)
                end_sample = int((end_ms / 1000) * sample_rate)
                n_samples = end_sample - start_sample

                # Seek to the start position and read only the chunk we need
                audio_file.seek(start_sample)
                chunk = audio_file.read(n_samples)

                # Save the chunk
                output_file = os.path.join(output_path, base_name + '.wav')
                sf.write(output_file, chunk, sample_rate)

                print(f"Successfully extracted chunk: {base_name}")

        except Exception as e:
            print(f"Error processing {wav_file}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract audio chunks from WAV files based on annotation files.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--recordings',
        type=str,
        required=True,
        help='Path to the folder containing WAV recordings'
    )

    parser.add_argument(
        '--annotations',
        type=str,
        required=True,
        help='Path to the folder containing annotation files'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path where extracted audio chunks will be saved'
    )

    args = parser.parse_args()

    # Convert to absolute paths
    recordings_path = os.path.abspath(args.recordings)
    annotations_path = os.path.abspath(args.annotations)
    output_path = os.path.abspath(args.output)

    # Check if input directories exist
    if not os.path.exists(recordings_path):
        parser.error(f"Recordings directory does not exist: {recordings_path}")
    if not os.path.exists(annotations_path):
        parser.error(f"Annotations directory does not exist: {annotations_path}")

    extract_audio_chunks(recordings_path, annotations_path, output_path)


if __name__ == "__main__":
    main()