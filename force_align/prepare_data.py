import argparse
import os
import re
from pathlib import Path

import pandas as pd
from nemo.collections.asr.models import ASRModel
from nemo.collections.asr.models.hybrid_rnnt_ctc_models import EncDecHybridRNNTCTCModel
from nemo.utils import model_utils
from tqdm import tqdm

from chat_toolkit.parser import parse_chat_file

MAX_UNIT_PERC = .5
MIN_NB_UTT = 1
# English, German, French, Spanish
AUTHORIZED_LANGUAGES = ['eng', 'deu', 'fra', 'spa']
LANG_MAP = {'eng': 'en',
            'deu': 'de',
            'fra': 'fr',
            'spa': 'es'}

def check_is_cha_valid(cha_data):
    nb_utt = len(cha_data)
    if nb_utt < MIN_NB_UTT:
        return False, 'too_few_utt'

    nb_unint = sum('xxx' in utt.content for utt in cha_data.utterances)
    if nb_unint > (nb_utt // 2):
        return False, 'too_many_xxx'

    languages = cha_data.languages
    if len(languages) > 1 or languages[0] not in AUTHORIZED_LANGUAGES:
        return False, 'unsupported_language'

    return True, LANG_MAP[languages[0]]

def clean_content(content, unknown_token):
    content = re.sub(r'\s+([?.!,])', r'\1', content) # Remove extra spaces before punct
    content = re.sub(r'[\\"/+*%@#=&_~‡^:\\]', '', content) # Remove special characters
    content = re.sub(r'\b(xx|xxx|yy|yyy|ww|www|0)\b', unknown_token, content) # xxx, yyy, www, 0 and replaced  by [UNK]
    content = re.sub(r'[^\x20-\x7E]', '', content) # Remove unicode special characters
    content = re.sub(r'\.{2,}', '.', content) # Replace .. by .
    content = re.sub(r'([?.!¿¡])[.]+', r'\1', content) # Replace [punct]. by [punct]
    return content

def clean_data(matched, cleaned_path, data_path, unknown_token):
    not_valid = []
    data = []
    for idx, row in tqdm(matched.iterrows()):
        transcript, audio, corpus = Path(row['transcript']), Path(row['audio']), row['corpus']
        transcript = Path(str(transcript.parent).replace(str(data_path), str(cleaned_path))) / (transcript.stem + '_cleaned.cha')
        audio = Path(str(audio.parent).replace(str(data_path), str(cleaned_path))) / audio.name
        cha_data = parse_chat_file(transcript)
        is_valid, reason = check_is_cha_valid(cha_data)
        if is_valid:
            content = '|'.join(utt.content for utt in cha_data.utterances)
            data.append(
                {
                    "audio_filepath": str(audio),
                    "text": clean_content(content, unknown_token),
                    "language": reason,
                    "corpus": corpus
                }
            )
        else:
            not_valid.append({"audio": str(audio), "reason": reason})

    return data, not_valid

def normalize_sentences(sentences, language):
    # replace numbers with num2words
    try:
        p = re.compile("\d+")
        new_text = ""
        match_end = 0
        for i, m in enumerate(p.finditer(sentences)):
            match = m.group()
            match_start = m.start()
            if i == 0:
                new_text = sentences[:match_start]
            else:
                new_text += sentences[match_end:match_start]
            match_end = m.end()
            new_text += sentences[match_start:match_end].replace(match, num2words(match, lang=language))
        new_text += sentences[match_end:]
        sentences = new_text
    except NotImplementedError:
        print(
            f"{language} might be missing in 'num2words' package. Add required language to the choices for the"
            f"--language argument."
        )
        raise

    sentences = re.sub(r' +', ' ', sentences)
    return sentences

def write_utterance(output_file, text, language, vocabulary_symbols):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    sentences = text.replace('|', '\n')
    # 1) Write file with punctuation
    with open(output_file.parent / (output_file.stem + '_with_punct.txt'), 'w') as fout:
        fout.write(sentences)

    # 2) Normalize sentences
    sentences = normalize_sentences(sentences, language)

    # 3) Write normalized sentences
    with open(output_file.parent / (output_file.stem + '_with_punct_normalized.txt'), 'w') as fout:
        fout.write(sentences)

    symbols_to_remove = ''.join(set(sentences).difference(set(vocabulary_symbols + ["\n", " "])))
    sentences = sentences.translate(''.maketrans(symbols_to_remove, len(symbols_to_remove) * " "))

    # remove extra space
    sentences = re.sub(r' +', ' ', sentences)

    with open(output_file, "w") as f:
        f.write(sentences)

def write_cleaned_data(data, output, vocabulary_symbols):
    output.mkdir(parents=True, exist_ok=True)

    for item in data:
        audio_path = Path(item['audio_filepath'])
        corpus = item['corpus']
        text = item['text']
        language = item['language']

        if corpus not in audio_path.parts:
            raise ValueError(f"{corpus.name} not found in {audio_path}.\nAborting.")

        start_idx = audio_path.parts.index(corpus)
        # Create audio symlink
        # (recreating the corpus structure to avoid skipping files that have the same name but different subpaths)
        output_audio = output / Path(*audio_path.parts[start_idx:])

        if not output_audio.exists():
            output_audio.parent.mkdir(parents=True, exist_ok=True)
            output_audio.symlink_to(audio_path)

        # Write utterances
        write_utterance(output_audio.with_suffix('.txt'), text, language, vocabulary_symbols)

def write_not_valid(not_valid, output):
    pd.DataFrame(not_valid).to_csv(output / f'not_valid.csv', index=False)

def write_languages(data, output):
    pd.DataFrame(data)[['audio_filepath', 'language']].to_csv(output / f'languages.csv', index=False)

def main():
    parser = argparse.ArgumentParser(description="Create manifest_{start}_{end}.json containing "
                                                 "the audio filepaths along with their transcript")
    parser.add_argument("--paired", type=str, required=True,
                        help="Path to the .csv file containing pairs of (audio,transcript)")
    parser.add_argument("--cleaned", type=str, required=True,
                        help="Path the folder containing *_cleaned.cha files")
    parser.add_argument('--data', type=str, required=True,
                        help="Path to the data folder containing (audio, transcript) pairs")
    parser.add_argument("--start", type=int, required=True,
                        help="Row index of where to start (from 0)")
    parser.add_argument("--end", type=int, required=True,
                        help="Row index of where to end (from 0)")
    parser.add_argument("--output", type=str, required=True,
                        help="Path where to store the prepared files")
    parser.add_argument("--unknown_token", type=str, default='<unk>',
                        required=False, help="Special token for unknown words")
    parser.add_argument("--model", type=str, default='stt_multilingual_fastconformer_hybrid_large_pc',
                        required=False, help="Model used later to (this is used to get the vocab)")
    args = parser.parse_args()

    args.paired = Path(args.paired)
    args.cleaned = Path(args.cleaned)
    args.data = Path(args.data)
    start, end = args.start, args.end
    args.output = Path(args.output) / f"from_{start}_to_{end}"

    # Get vocabulary symbols (this is specific to the model used)

    if os.path.exists(args.model):
        model_cfg = ASRModel.restore_from(restore_path=args.model, return_config=True)
        classpath = model_cfg.target  # original class path
        imported_class = model_utils.import_class_by_path(classpath)  # type: ASRModel
        print(f"Restoring model : {imported_class.__name__}")
        asr_model = imported_class.restore_from(restore_path=args.model)  # type: ASRModel
    else:
        # restore model by name
        asr_model = ASRModel.from_pretrained(model_name=args.model)  # type: ASRModel

    if not isinstance(asr_model, EncDecHybridRNNTCTCModel):
        raise NotImplementedError(
            f"Model is not an instance of NeMo ENCDecHybridRNNTCTCModel."
            " Currently only instances of this model are supported"
        )


    if hasattr(asr_model, 'tokenizer'):  # i.e. tokenization is BPE-based
        vocabulary = asr_model.tokenizer.vocab
    elif hasattr(asr_model.decoder, "vocabulary"):  # i.e. tokenization is character-based
        vocabulary = asr_model.cfg.decoder.vocabulary
    else:
        raise ValueError("Unexpected model type. Vocabulary list not found.")

    vocabulary_symbols = []

    for x in vocabulary:
        # if x != "<unk>":
        #     # for BPE models
        #     vocabulary_symbols.extend([x for x in x.replace("##", "").replace("▁", "")])
        vocabulary_symbols.extend([x for x in x.replace("##", "").replace("▁", "")])
    vocabulary_symbols = list(set(vocabulary_symbols))
    vocabulary_symbols += [x.upper() for x in vocabulary_symbols]

    matched = pd.read_csv(args.paired, sep='\t')

    if matched.isna().any().any():
        print(matched.head())
        raise ValueError(f"Can't parsed {args.paired}. Please check all fields are tab separated.")

    if (start < 0 or start > matched.shape[0] or
            end < 0 or end > matched.shape[0] or
            start > end):
        raise ValueError("Start should be smaller than end and both should be between 0 and matched.shape[0].")
    matched = matched[start:end]
    data, not_valid = clean_data(matched, args.cleaned, args.data, args.unknown_token)
    print(f"Data len = {len(data)}")
    print(f"Not valid len = {len(not_valid)}")
    write_not_valid(not_valid, args.output)
    if len(data) != 0:
        write_cleaned_data(data, args.output, vocabulary_symbols)
        write_languages(data, args.output)

if __name__ == "__main__":
    main()
