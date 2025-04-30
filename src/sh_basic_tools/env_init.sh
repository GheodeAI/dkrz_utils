#!/bin/bash

module load cdo
module load nano
module load pytorch
module load nvhpc
export XLA_FLAGS=--xla_gpu_cuda_data_dir=/sw/spack-levante/nvhpc-24.7-py26uc/Linux_x86_64/24.7/cuda/12.5
export TF_FORCE_GPU_ALLOW_GROWTH=true
module load texlive/live2021-gcc-11.2.0
source activate
conda activate ENV
cd /work/{PROJ}/{USER}/
