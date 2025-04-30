#!/bin/bash
#SBATCH --job-name=data_copy
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --mail-user=cosmin.marina@uah.es
#SBATCH --mail-type=END
#SBATCH --account=bb1478
#SBATCH --output=out_sh.log

# Begin of section with executable commands
# By default, the output log of Levante is stored in the same path as this script.


# Loading modules to use in this script

module purge
module load python3/2022.01-gcc-11.2.0
module load clint
module load xces

python copy_files.py &> out.log