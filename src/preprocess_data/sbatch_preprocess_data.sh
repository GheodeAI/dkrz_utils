#!/bin/bash
#SBATCH --job-name=10V_preprocess
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --mail-user=cosmin.marina@uah.es
#SBATCH --mail-type=END
#SBATCH --account=bb1478
#SBATCH --output=out_sh.log

module load cdo
sh preprocess_data_unique.sh /pool/data/ERA5/E5/sf/an/1D/166/ ./raw/ -r '.*\.grb' > out.log
