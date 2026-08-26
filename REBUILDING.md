# Rebuilding TinyVox from scratch

This is only needed if you want to reproduce or modify the data pipeline. If you just want to use TinyVox, see the [Quickstart](README.md#quickstart) in the main README instead.

## 1) Installation

To install the repo and its dependencies, you can run:

```sh
conda env create -f env.yml
conda activate tinyvox
pip install -e .
```

## 2) Data preparation

If you want to rebuild TinyVox from scratch, follow these steps.

**Step 1 — Download all audio files and transcript files from [PhonBank](https://phon.talkbank.org/)**, following the same structure.

You can use our helper script (which should hopefully work if nothing has changed on the PhonBank side):

```sh
python data_preparation/talkbank_audio_scrapper.py mail password database
```

where `mail` and `password` should be your email address and password associated with your TalkBank account, and `database` should be one of `homebank`, `childes`, or `phon` (`phon` in our case).

Note that this script will download everything, keeping the same structure as the original structure used in PhonBank.

*Script last tested: January 20th, 2026*

**Step 2 — Unzip and keep the `.zip` files**, as we'll need them for step 3.

To unzip you can use this bash command:

```shell
find /path/to/data -name "*.zip" -type f -execdir unzip -o {} \;
```

```shell
├── childes
│   ├── Biling
│   │   ├── Amsterdam
│   │   │   ├── Annick
│   │   │   │   ├── fra
│   │   │   │   └── nld
│   │   │   ├── Anouk
│   │   │   │   ├── fra
│   │   │   │   └── nld
...
└── phon
    ├── Biling
    │   ├── Almeida
    │   │   ├── fra
    │   │   └── por
    │   ├── ChildL2
    │   │   └── 0wav
```

**Step 3 — Remove `.mp3` files for which there's already a `.wav`**, and convert everything to single-channel 16 kHz. Don't forget to change the data path in the two scripts above.

```shell
python data_preparation/convert_audio.py /path/to/downloaded_corpora
```

where the provided path corresponds to where the data was downloaded in step 1.

**Step 4 — List pairs of (audio, transcript)**, checking that the audio can be loaded and filtering out (1) automatic transcripts and (2) transcripts with >2% of utterances missing timestamps.

This creates a `.csv` file at `data_logs/original_pairs.csv` with the created pairs.

```shell
python data_preparation/create_pairs.py --data_path /path/to/downloaded_corpora --required_tiers pho xpho
```

**Step 5 — Extract phonetically-transcribed utterances of the target child.**

Run `analysis/data_quantity.ipynb` to produce `phonetically_transcribed_pairs/utterances.csv`.

**Step 6 — Map the input phonetic inventory to the target inventory** (`ipa/mapping.py`) and remove empty utterances:

```shell
python data_preparation/simplify_phones.py --data phonetically_transcribed_pairs/utterances.csv
```

This creates `phonetically_transcribed_pairs/utterances2.csv`.

**Step 7 — Extract KCHI segments into individual files:**

```shell
python data_preparation/extract_segments.py --data phonetically_transcribed_pairs/utterances2.csv --out /path/to/TinyVox
```

**Step 8 — Create the phonetic vocabulary:**

```shell
python data_preparation/create_inventory.py --path /path/to/TinyVox
```

**Step 9 — Copy original audio files to TinyVox:**

```shell
python data_preparation/copy_original_files.py --data TinyVox
```