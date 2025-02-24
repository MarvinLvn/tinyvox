#!/bin/bash
#SBATCH --job-name=align
#SBATCH --output=logs/align_%A_%a.out
#SBATCH --error=logs/align_%A_%a.err
#SBATCH --array=0-637%4  # 31882/50 rounded up
#SBATCH --time=30:00:00
#SBATCH --mem=64G
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=6

START=$((SLURM_ARRAY_TASK_ID * 50))
END=$((START + 49))

# Ensure last batch doesn't exceed max files
if [ $END -gt 31881 ]; then
   END=31881
fi

bash run_align.sh $START $END
