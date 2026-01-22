# Installation

To install the repo and its dependencies, you can run:

```sh
conda env create -f env.yml
conda activate tinyvox
pip install -e .
```

# Data preparation 

## A) Download audio along with their transcript

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