import os
import subprocess
import logging
from pathlib import Path
from tqdm import tqdm
import soundfile as sf

def setup_logging():
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('audio_conversion.log'),
           logging.StreamHandler()
       ]
   )

def check_audio_specs(file_path):
    """Check if audio file meets our specifications using soundfile."""
    try:
        info = sf.info(file_path)
        return info.samplerate == 16000 and info.channels == 1
    except Exception as e:
        logging.error(f"Error checking {file_path}: {str(e)}")
        return False

def convert_audio_files(input_dir):
    setup_logging()
    input_path = Path(input_dir)
    failed_conversions = []

    audio_files = list(input_path.glob("**/*.mp4")) + list(input_path.glob("**/*.mp3")) + list(
        input_path.glob("**/*.wav"))

    for audio_file in tqdm(audio_files, desc="Converting audio files"):
        output_file = audio_file.with_suffix('.wav')

        if audio_file.suffix == '.wav':
            try:
                if check_audio_specs(audio_file):
                    continue
            except Exception as e:
                logging.error(f"Error checking format of {audio_file}: {str(e)}")
                failed_conversions.append((audio_file, str(e)))
                continue

        temp_output = output_file.with_name(f"temp_{output_file.name}")
        convert_cmd = [
            'ffmpeg', '-i', str(audio_file),
            '-vn',
            '-ac', '1',
            '-ar', '16000',
            '-acodec', 'pcm_s16le',
            '-y',
            str(temp_output)
        ]

        try:
            subprocess.run(convert_cmd, check=True, capture_output=True)
            if check_audio_specs(temp_output):
                temp_output.replace(output_file)
                if audio_file.suffix != '.wav':
                    audio_file.unlink()
            else:
                raise subprocess.CalledProcessError(1, convert_cmd)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
            logging.error(f"Error converting {audio_file}: {error_msg}")
            failed_conversions.append((audio_file, error_msg))
            if temp_output.exists():
                temp_output.unlink()

    if failed_conversions:
        with open('failed_conversions.txt', 'w') as f:
            for file, error in failed_conversions:
                f.write(f"{file.absolute()}\n")
        return False
    return True

if __name__ == "__main__":
   input_dir = "/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora"
   success = convert_audio_files(input_dir)
   if not success:
       exit(1)