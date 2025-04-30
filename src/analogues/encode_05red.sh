#!/bin/bash
#SBATCH --job-name=encode_05red
#SBATCH --partition=gpu
#SBATCH --nodes=2
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --time=12:00:00
#SBATCH --mail-user={USER}
#SBATCH --mail-type=END
#SBATCH --account={PROJ}
#SBATCH --output=out_sh_enc_05red.log

module load pytorch
module load nvhpc
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/sw/spack-levante/nvhpc-24.7-py26uc/Linux_x86_64/24.7/cuda/12.5
export TF_FORCE_GPU_ALLOW_GROWTH=true
module load texlive/live2021-gcc-11.2.0
source activate
conda activate ENV
#python encode_search.py -m "encode" -f "config/identify_hw_france2003-mv-05-red.json" > out_enc_05red.log
#python encode_search.py -m "encode" -f "config/train/train_france2003_era5.json" > out_enc_05red.log
#python encode_search.py -m "search-ecmwf" -f "config/search/train_france2003_ecmwf.json" > out_enc_05red.log
python encode_search.py -m "post-process-anal" -f "config/search/train_france2003_ecmwf.json" > out_enc_05red.log
#python encode_search.py -m "search-past2k" -f "config/analogos/train_france2003_past2k.json" > out_enc_05red.log
#python encode_search.py -m "search-past2k" -f "config/entrenamiento/train_france2003_past2k.json" > out_enc_05red.log
