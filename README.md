TinyVox is a large-scale, cross-linguistic corpus of over half a million IPA-transcribed child vocalizations, curated from [PhonBank](https://talkbank.org/phon/). It covers five languages (English, French, Portuguese, German, and Spanish) and includes recordings from 560 children aged 6 months to 8 years across 31 source corpora. TinyVox standardizes heterogeneous phonetic annotations into a unified 57-phoneme inventory and provides ready-to-use train/validation/test splits designed for training and evaluating automatic phoneme recognition systems on child speech. It was introduced alongside [BabAR](https://github.com/MarvinLvn/BabAR), a phoneme recognition system for young children's speech.

## 0) Downloading TinyVox

TinyVox can be downloaded here: [https://talkbank.org/phon/access/Derived/TinyVox.html](https://talkbank.org/phon/access/Derived/TinyVox.html).

```
├── audio/
├── metadata.csv
├── train.csv
├── val.csv
└── test.csv
```

The `audio` folder contains children's speech utterances (.wav files) extracted from manually-annotated boundaries.

`metadata.csv` contains various information about these utterances, including:
- `audio_filename` the name of the .wav file containing the utterance in the `audio` folder 
- `original_audio_path` the path of the original audio file (from which `audio_filename` has been extracted); if you want to redownload the original audio file
- `original_transcript_path` the path of the original transcript file (.cha); if you want to redownload the original annnotation file 
- `language` the language spoken by the child
- `gender` the gender of the child
- `file_activity` the type of activity that is being recorded (e.g., toyplay or picture naming)
- `age_months` the age of the child in months
- `phones` the manual transcription (after normalization)
- `sentence` the orthographic transcript (not always available, not used in the paper)
- `child_pseudoid` which child has been recorded (inferred pseudo-id from metadata) 
- `onset` the onset of the utterance (in ms) in the original file (if you want to re-extract the utterance)
- `offset` the offset of the utterance (in ms) in the original file (if you want to re-extract the utterance)

`{train,val,test}.csv` contains essentially the same information with the split we used to train BabAR. 

If you want to re-create TinyVox from scratch, you can follow these instructions:

## 1) Installation

To install the repo and its dependencies, you can run:

```sh
conda env create -f env.yml
conda activate tinyvox
pip install -e .
```

## 2) Data preparation 

If you want to rebuild TinyVox from scratch, you can followed these steps.

1. Download all audio files and transcript files from [PhonBank](https://phon.talkbank.org/), following the same structure. 

You can use our helper script (which should hopefully work if nothing has changed on the PhonBank side):

```sh
python data_preparation/talkbank_audio_scrapper.py mail password database
```

where mail and password should be your email address and password associated to your TalkBank account and database should belong to [homebank, childes, or phon] (phon in our case).

Note that this script will download everything, keeping the same structure as the original structured used in PhonBank. 

Script last tested: January 20th, 2026

2. Unzip and keep .zip files as we'll need them for step 3.

To unzip you can use this bash command:
```shell
find /path/to/data -name "*.zip" -type f -execdir unzip -o {} \;
```

```shell
├── childes
│   ├── Biling
│   │   ├── Amsterdam
│   │   │   ├── Annick
│   │   │   │   ├── fra
│   │   │   │   └── nld
│   │   │   ├── Anouk
│   │   │   │   ├── fra
│   │   │   │   └── nld
...
└── phon
    ├── Biling
    │   ├── Almeida
    │   │   ├── fra
    │   │   └── por
    │   ├── ChildL2
    │   │   └── 0wav
```

3. Remove .mp3 for which there's already a .wav and convert everything to single-channel 16 kHz. Don't forget to change the data path in the two scripts above. 

```shell
python data_preparation/convert_audio.py /path/to/downloaded_corpora
```

where the provided path corresponds to where the data have been downloaded in step 1.

4. List pairs of (audio, transcript) while checking that the audio can be loaded and trying to filter out 1) automatic transcripts, 2) transcripts with >2% utterances with missing timestamps. 
This will create a .csv file in `data_logs/original_pairs.csv` with the created pairs.

```shell
python data_preparation/create_pairs.py --data_path /path/to/downloaded_corpora --required_tiers pho xpho
```

5. You can run `analysis/data_quantity.ipynb` to extract phonetically-transcribed utterances of the target child into the `phonetically_transcribed_pairs/utterances.csv` file.

6. To map the input phonetic inventory to the target inventory (`ipa/mapping.py`) and remove empty utterances, you can use: 

```shell
python data_preparation/simplify_phones.py --data phonetically_transcribed_pairs/utterances.csv
```

This will create a file `phonetically_transcribed_pairs/utterances2.csv`

7. Extract KCHI segments into individual files using:

```shell
python data_preparation/extract_segments.py --data phonetically_transcribed_pairs/utterances2.csv --out /path/to/TinyVox
```

8. Create phonetic vocabulary:

```shell
python data_preparation/create_inventory.py --path /path/to/TinyVox
```

9. Copy original audio files to tinyvox:

```shell
python data_preparation/copy_original_files.py --data TinyVox
```

## References

```bibtex
@misc{babar,
      title={BabAR: from phoneme recognition to developmental measures of young children's speech production}, 
      author={Marvin Lavechin and Elika Bergelson and Roger Levy},
      year={2026},
      eprint={2603.05213},
      archivePrefix={arXiv},
      primaryClass={eess.AS},
      url={https://arxiv.org/abs/2603.05213}, 
}
```
