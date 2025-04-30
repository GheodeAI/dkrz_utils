#!/bin/bash
#SBATCH --job-name=z300_merge_data
#SBATCH --partition=gpu
#SBATCH --nodes=4
#SBATCH --mem=0
#SBATCH --time=12:00:00
#SBATCH --mail-user=cosmin.marina@uah.es
#SBATCH --mail-type=END
#SBATCH --account=bb1478
#SBATCH --output=out_sh.log

module load python3
source activate
conda activate minu_80
python merge_data.py -v "gz300/" -sn "ecmwf_01_gz300" -p "../../datasets/ecmwf/ens_01/" -o "data/ecmwf/ens_01/gz300/"
