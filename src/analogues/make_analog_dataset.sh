#!/bin/bash
#SBATCH --job-name=make_analog_dataset
#SBATCH --partition=gpu
#SBATCH --nodes=4
#SBATCH --mem=0
#SBATCH --time=12:00:00
#SBATCH --mail-user={MAIL}
#SBATCH --mail-type=END
#SBATCH --account={PROJ}
#SBATCH --output=out_anal_dataset.log

module load python3
source activate
conda activate ENV
python make_analog_dataset.py --csv_path "anal_dict/post_processed_analogues_1993-2016.csv" --variable gz300 --input_dir "./data/ecmwf/" --output_path "./data/analogues/"
