#!/bin/bash
#SBATCH --job-name=data_acq_1
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --mail-user=${MAIL}
#SBATCH --mail-type=END
#SBATCH --account=${PATHPROJ1}
#SBATCH --output=out_sh.log

# Begin of section with executable commands
# By default, the output log of Levante is stored in the same path as this script.


# Loading modules to use in this script

# module purge
module load python3/2022.01-gcc-11.2.0
module load clint
module load xces

python 0_data_acq_main_ECROPS.py


