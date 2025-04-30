#!/bin/bash
#SBATCH --job-name=remap_era5
#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --mail-user={MAIL}
#SBATCH --mail-type=END
#SBATCH --account={PROJ}
#SBATCH --output=out_sh_remap.log

module load cdo
cdo remapbil,grid_1x1_integer.grid ../../datasets/ERA5/ERA5_level\=500_var\=geopotential_daymean_invertlat.nc data/era5/ERA5_z500_daymean_invertlat_g1_aux.nc
cdo sellonlatbox,-180,180,-90,90 data/era5/ERA5_z500_daymean_invertlat_g1_aux.nc data/era5/ERA5_z500_daymean_invertlat_g1.nc
rm data/era5/ERA5_z500_daymean_invertlat_g1_aux.nc
