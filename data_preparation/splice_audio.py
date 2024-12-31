from pathlib import Path
import pandas as pd
from tqdm import tqdm
from chat_toolkit.parser import parse_chat_file
import soundfile as sf
from chat_toolkit.cha import CHATFile, Utterance, MissingTimestampsUtterance

def load_cha(cha_paths):
    print("Loading .cha files")
    cha_files = []
    for cha_file in tqdm(cha_paths):
        cha_files.append(parse_chat_file(cha_file))
    return cha_files

def splice_audio(cha_files, audio_paths, output_folder, root_folder):
    print("Splicing audio and adjusting timestamps in .cha files")
    for cha_file, audio_path in tqdm(zip(cha_files, audio_paths)):

        # Load audio and initialize output paths
        audio, sr = sf.read(audio_path)
        audio_output_path = output_folder / Path(audio_path).relative_to(root_folder)
        audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        cha_output_path = output_folder / Path(cha_file.filename).relative_to(root_folder)
        cha_output_path.parent.mkdir(parents=True, exist_ok=True)

        if audio_output_path.exists() and cha_output_path.exists(): continue

        if len(cha_file.utterances) >= 2 and isinstance(cha_file.utterances[0], Utterance) and isinstance(cha_file.utterances[-1], Utterance):
            # Extract onset of first utt and offset of last utt
            start_ms = cha_file.utterances[0].onset
            end_ms = cha_file.utterances[-1].offset
            start_idx = int(start_ms/1000*sr)
            end_idx = int(end_ms/1000*sr)

            # Splice audio and save it
            if start_idx == end_idx:
                cha_file.print_content()
            audio_segment = audio[start_idx:end_idx]
            sf.write(audio_output_path, audio_segment, sr)

            # Adjust timestamps
            for utterance in cha_file.utterances:
                if isinstance(utterance, Utterance):
                    utterance.onset = utterance.onset - start_ms
                    utterance.offset = utterance.offset - start_ms

            cha_output_path = output_folder / Path(cha_file.filename).relative_to(root_folder)
            cha_output_path.parent.mkdir(parents=True, exist_ok=True)
            cha_file.write(cha_output_path)
        else:
            #Symlink wav and cha
            audio_output_path.symlink_to(audio_path)
            cha_output_path.symlink_to(cha_file.filename)



if __name__ == '__main__':
    PAIRS_PATH = Path('/scratch2/mlavechin/ASR_longforms/pairs/matched.txt')
    ROOT_FOLDER = Path('/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora')
    OUTPUT_FOLDER = ROOT_FOLDER / 'prepared'
    matched = pd.read_csv(PAIRS_PATH, sep='\t')

    #matched = matched[:50]

    # 1) Load cha files
    cha_files = load_cha(matched['transcript'])

    # 2) Splice audio
    splice_audio(cha_files, matched['audio'], OUTPUT_FOLDER, ROOT_FOLDER)
