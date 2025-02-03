# Installation

To install the repo and its dependencies, you can run:

```sh
conda env create -f env.yml
conda activate asr
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install ctc_segmentation==1.7.1
pip install nemo_toolkit['all']
pip install -e .
```

If you get the following error when installing nemo_toolkit:

```sh
/tmp/pip-install-szsh7rze/mamba-ssm_397a97adb34747749384b66bc3648329/setup.py:119: UserWarning: mamba_ssm was requested, but nvcc was not found.  Are you sure your environment has nvcc available?  If you're installing within a container from https://hub.docker.com/r/pytorch/pytorch, only images whose names contain 'devel' will provide nvcc.
        warnings.warn(
      Traceback (most recent call last):
        File "<string>", line 2, in <module>
        File "<pip-setuptools-caller>", line 34, in <module>
        File "/tmp/pip-install-szsh7rze/mamba-ssm_397a97adb34747749384b66bc3648329/setup.py", line 189, in <module>
          if bare_metal_version >= Version("11.8"):
      NameError: name 'bare_metal_version' is not defined
```

You can run:

```sh
wget https://github.com/state-spaces/mamba/releases/download/v2.2.2/mamba_ssm-2.2.2+cu118torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
pip install mamba_ssm-2.2.2+cu118torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
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

## B) Preprocess audio and clean .cha files

4. Splice audio between the onset of the first utterance and the offset of the last utterance (to avoid partially annotated files). Files with missing timestamps are kept as-is.

```shell
python splice_audio.py
```

5. Clean .CHA files:

```shell
python clean_cha.py
```

Note a: This will create *_cleaned.cha files in the `downloaded_corpora/prepared` folder.

Note b: /!\ To anyone who'd like to work on TalkBank with another task (e.g., child phone recognition), you should probably start from here. 
The next step is destructive as we'll force-align only 4 languages: English, German, French, Spanish

## C) Force align at the utterance level 

6. Prepare data to be processed by NeMo:

```sh
python force_align/prepare_data.py --paired force_align/fake_matched.txt \
  --cleaned $DATA/ForcedAlignmentTest \
  --data $DATA/ForcedAlignmentTest \
  --start <START> --end <END> \
  --output FA_prepared
```

where:
* --cleaned is the path to the cleaned data (*.wav with *_cleaned.cha)
* --data is the path to where the original data are stored (*.wav with original *.cha)
* (start, end) are indices of the files you want to process in the --paired file.
* --output is the output folder where .wav (symlink) and .txt (normalized) files will be stored.

This will recreate the corpus structure in `FA_prepared` with the audio file (symbolic link) and the cleaned transcript (new file).

7. Then we can run utterance-level forced alignment:

```sh  
python force_align/ctc_align.py \
  --data=FA_prepared/from_<START>_to_<END> \
  --model=stt_multilingual_fastconformer_hybrid_large_pc --window_len=8000
```


# Download data (OUTDATED)

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