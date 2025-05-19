# Installation

To install the repo and its dependencies, you can run:

```sh
conda env create -f env.yml
conda activate phorec
```

# Data preparation 

## A) Download audio along with their transcript

1. Download all audio files and transcript files from [CHILDES](https://childes.talkbank.org/), [HomeBank](https://homebank.talkbank.org/), [PhonBank](https://phon.talkbank.org/),
following the same structure. Unzip and keep .zip files as we'll need them for step 3.

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

2. Remove .mp3 for which there's already a .wav and convert everything to single-channel 16 kHz. Don't forget to change the data path in the two scripts above. 

```shell
./clean_duplicates.sh
python convert_audio.py
```

3. List pairs of (audio, transcript) while checking that the audio can be loaded and trying to filter out 1) automatic transcripts, 2) transcripts with >2% utterances with missing timestamps. 
This will create a .csv file in `data_logs/original_pairs.csv` with the created pairs.

```shell
python create_pairs.py
```

4. You can run `analysis/data_quantity.ipynb` to extract phonetically-transcribed utterances of the target child into the `phonetically_transcribed_pairs/utterances.csv` file.

5. To map the input phonetic inventory to the target inventory (`ipa/mapping.py`) and remove empty utterances, you can use: 

```shell
python simplify_phones.py --data phonetically_transcribed_pairs/utterances.csv
```

This will create a file `phonetically_transcribed_pairs/utterances2.csv`