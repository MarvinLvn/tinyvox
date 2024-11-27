# Download data

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