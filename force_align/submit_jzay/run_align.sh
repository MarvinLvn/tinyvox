#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Error: Please provide start and end indices of files to be processed"
    echo "Usage: $0 <START> <END>"
    exit 1
fi

START=$1
END=$2

WORK_DIR=/linkhome/rech/genscp01/uow84uh/ASR_longforms
SCRIPT_DIR=${WORK_DIR}/force_align/submit_jzay
MATCHED_PATH=${WORK_DIR}/pairs/jzay/matched.txt # path to the file containing (audio,transcript) pairs
DATA=/lustre/fsn1/projects/rech/xdz/uow84uh/DATA/CLEAR_ASR/IN_PREP/downloaded_corpora
CLEANED_PATH=${DATA}/prepared # where the cleaned data are stored on jzay
ORIGINAL_PATH=/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora # Oberon path that will be replaced
OUTPUT_PATH=${DATA}/prepared_nemo_aligned

source activate /linkhome/rech/genscp01/uow84uh/.conda/envs/asr
module unload gcc
module load gcc/14.2.0
export TMPDIR=$WORK # For NeMo to load model where there's space
#export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

cd ${WORK_DIR}
# 1) Prepare data
echo python force_align/prepare_data.py --paired $MATCHED_PATH \
  --cleaned $CLEANED_PATH \
  --data $ORIGINAL_PATH \
  --start $START --end $END \
  --output $OUTPUT_PATH


# 2) Run force alignment
echo python force_align/ctc_align.py --data ${OUTPUT_PATH}/from_${START}_to_${END} \
  --model=stt_multilingual_fastconformer_hybrid_large_pc \
  --window_len=8000 --gpu
