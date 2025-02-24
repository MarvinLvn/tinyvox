#!/bin/bash

# Create directory for storing the failed task lists
mkdir -p failed_jobs

# Find tasks that failed due to missing languages.csv
grep -l "Cannot find.*languages.csv" logs/align_*_*.err | sed -E 's/.*align_[0-9]+_([0-9]+).err/\1/' | sort -n > failed_jobs/missing_file_tasks.txt

# Find tasks that failed due to OOM errors
grep -l "oom-kill event" logs/align_*_*.err | sed -E 's/.*align_[0-9]+_([0-9]+).err/\1/' | sort -n > failed_jobs/oom_tasks.txt

# Combine all failed tasks
cat failed_jobs/missing_file_tasks.txt failed_jobs/oom_tasks.txt | sort -n | uniq > failed_jobs/all_failed_tasks.txt

echo "Found $(wc -l < failed_jobs/missing_file_tasks.txt) tasks with missing file errors"
echo "Found $(wc -l < failed_jobs/oom_tasks.txt) tasks with out-of-memory errors"
echo "Total unique failed tasks: $(wc -l < failed_jobs/all_failed_tasks.txt)"