# Data preparation

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

2. Remove .mp3 for which there's already a .wav and convert everything to single-channel 16 kHz:

```shell
./clean_duplicates.sh
python convert_audio.py
```

3. List pairs of (audio, transcript)

```shell

```
# Download data

First, install repositories:

```sh
conda activate childproject
repositories=(git@gin.g-node.org:/MarvinLvn/playlogue.git 
git@gin.g-node.org:/LAAC-LSCP/vandam.git
git@gin.g-node.org:/LAAC-LSCP/Cougar-2023.git 
git@gin.g-node.org:/LAAC-LSCP/lyon.git 
git@gin.g-node.org:/LAAC-LSCP/tsay.git
git@gin.g-node.org:/LAAC-LSCP/providence.git 
git@gin.g-node.org:/LAAC-LSCP/thomas.git
git@gin.g-node.org:/LAAC-LSCP/bergelson.git 
git@gin.g-node.org:/LAAC-LSCP/warlaumont.git 
git@gin.g-node.org:/LAAC-LSCP/soderstrom.git
git@gin.g-node.org:/LAAC-LSCP/lucid.git 
git@gin.g-node.org:/LAAC-LSCP/winnipeg.git)

for repository in ${repositories[*]}; do
    datalad install $repository;
done;

```

Then, get annotations + recordings. If you don't work on oberon, it's gonna take a LONG time. 
On oberon (LAAC cluster), I just had to do it for vandam, thomas, winnipeg, providence, tsay, bergelson (those were not installed in laac_data or were missing files).
```sh
repositories=(bergelson lucid playlogue
warlaumont cougar lyon 
providence  thomas     
vandam winnipeg)
for repository in ${repositories[*]}; do
  cd $repository
  datalad get annotations
  datalad get recordings
  cd ..
done; 
```

Extract parts of the recordings that have been transcribed (note Playlogue, Providence, Thomas, and Forrester have been fully transcribed):

```shell
# Bergelson (one recording has 0 duration and cannot be extracted)
python extract_annotated.py --annotations /scratch1/data/raw_data/CLEAR_ASR/bergelson/annotations/eaf/an1/converted --recordings /scratch1/data/raw_data/CLEAR_ASR/bergelson/recordings/raw --output /scratch1/data/raw_data/CLEAR_ASR/bergelson/recordings/chunks

# Lucid
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/lucid/annotations/eaf/an1/converted --recordings /scratch1/data/laac_data/datasets/lucid/recordings/raw --output /scratch1/data/raw_data/CLEAR_ASR/lucid/recordings/chunks

# Warlaumont
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/warlaumont/annotations/eaf/an1/converted --recordings /scratch1/data/laac_data/datasets/warlaumont/recordings/raw --output /scratch1/data/raw_data/CLEAR_ASR/warlaumont/recordings/chunks

# Cougar
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/cougar/annotations/cha/an1/converted --recordings /scratch1/data/laac_data/datasets/cougar/recordings/converted/standard --output /scratch1/data/raw_data/CLEAR_ASR/cougar/recordings/chunks

# Lyon
python extract_annotated.py --annotations /scratch1/data/raw_data/CLEAR_ASR/lyon/annotations/textgrid/gl/converted --recordings /scratch1/data/laac_data/datasets/lyon/recordings/converted/standard --output /scratch1/data/raw_data/CLEAR_ASR/lyon/recordings/chunks
# Winnipeg
python extract_annotated.py --annotations /scratch1/data/raw_data/CLEAR_ASR/winnipeg/annotations/eaf/an1/converted --recordings /scratch1/data/raw_data/CLEAR_ASR/winnipeg/recordings/raw --output /scratch1/data/raw_data/CLEAR_ASR/winnipeg/recordings/chunks

# Vandam (chunks aligned with their transcription are already stored in the repo, but we'll do some renaming)
python extract_annotated_vandam.py --annotations /scratch1/data/raw_data/CLEAR_ASR/vandam/annotations/cha/an1/converted --recordings /scratch1/data/raw_data/CLEAR_ASR/vandam/recordings --output /scratch1/data/raw_data/CLEAR_ASR/vandam/recordings/chunks --mapping /scratch1/data/raw_data/CLEAR_ASR/vandam/metadata/annotations.csv

# Thomas: we'll only create symlinks to have a 'chunks' folder containing annotation portions of the audio
ln -s $PWD/thomas/recordings/raw $PWD/thomas/recordings/chunks

# Playlogue
ln -s $PWD/playlogue/recordings/raw $PWD/playlogue/recordings/chunks

# Providence
ln -s $PWD/providence/recordings/converted/standard $PWD/providence/recordings/chunks

# Forrester
ln -s $PWD/forrester/recordings/raw $PWD/forrester/recordings/chunks
```

At this point, you should have `recordings/chunks` (containing audio files) and `annotations/set_name` (containing .csv annotation files) for each corpus.