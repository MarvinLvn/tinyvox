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
git@gin.g-node.org:/LAAC-LSCP/tsay.git 
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
soderstrom tsay warlaumont 
Cougar-2023 lyon providence  thomas     
vandam winnipeg)
for repository in ${repositories[*]}; do
  cd $repository
  datalad get annotations
  datalad get recordings
  cd ..
done; 
```

Extract parts of the recordings that have been transcribed (note Playlogue & Providence have been fully transcribed):

```shell
# Bergelson: missing wav
python extract_annotated.py --annotations /scratch1/data/raw_data/homebank/bergelson/annotations/eaf/an1/converted --recordings /scratch1/data/laac_data/datasets/bergelson/recordings/raw --output /scratch1/data/raw_data/homebank/bergelson/recordings/chunks

# Lucid
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/lucid/annotations/eaf/an1/converted --recordings /scratch1/data/laac_data/datasets/lucid/recordings/raw --output /scratch1/data/raw_data/homebank/lucid/recordings/chunks

# Soderstrom: many problems

# Warlaumont
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/warlaumont/annotations/eaf/an1/converted --recordings /scratch1/data/laac_data/datasets/warlaumont/recordings/raw --output /scratch1/data/raw_data/homebank/warlaumont/recordings/chunks

# Cougar
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/cougar/annotations/cha/an1/converted --recordings /scratch1/data/laac_data/datasets/cougar/recordings/converted/standard --output /scratch1/data/raw_data/homebank/cougar/recordings/chunks

# Lyon
python extract_annotated.py --annotations /scratch1/data/laac_data/datasets/lyon/annotations/textgrid/gl/converted --recordings /scratch1/data/laac_data/datasets/lyon/recordings/converted/standard --output /scratch1/data/raw_data/homebank/lyon/recordings/chunks

# Providence
```