#################################################################################
# Title: Main class routine for searching and logging available FREVA datasets
# module load order: python3, clint, xces, then run script
# Author: Odysseas Vlachopoulos
# Project: testing
##################################################################################

import logging
import sys
# from FREVA import freva_search
import data_acq_freva_search_ECROPS
import os

# projects = ['cmip6', 'reanalysis']
projects = ['cmip6']
# models = ['cesm2',
#           'cnrm-cm6-1-HR',
#           'gfdl-esm4',
#           'ec-earth3',
#           'mpi-esm1-2-hr',
#           'noresm2-mm',
#           'hadgem3-gc31-mm']
models = ['mpi-esm1-2-lr']
          
# models = [] # DO NOT DO ANYTHING FOR CMIP6
variables_cmip = ['tdps', 'ua', 'va', 'tasmax', 'lai']

# variables_era5_daily_monthly = ['tasmax', 'tasmin', 'tas', 'pr', 'rsds', 'tdps', 'sfcwind', 'hurs']
variables_era5_daily_monthly = ['tdps', 'ua', 'va', 'tasmax', 'lai']
# variables_era5_hourly = ['uas', 'vas']
variables_era5_hourly: list[str] = []

# variables_era5_hourly = ['uas', 'vas', 'rsds', 'tdps']
# 10m wind speed vas and uas are calculated with ECROPS function in wofost_util/util.py wind10to2(wind10) function


geopotential_height = 50000  # 500hPa
vorticity_height = 20000  # 200hPa

# frequency = ['hour', 'day', 'mon']
frequency = ['day']
# frequency = ['mon']
# exp_cmip6 = ['ssp370', 'ssp585', 'historical']
exp_cmip6 = ['historical', 'past2k']
exp_reanalysis = 'era5'


def main():   
    # First initialize a logger instance
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True,
        handlers=[
            logging.FileHandler("LOG_Data_Acquisition_FREVA_output.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info('Started Freva files main programme \n')

    for project in projects:
        if project == 'cmip6':
            for i in range(len(models)):
                for exp in exp_cmip6:
                    for var in variables_cmip:
                        logging.info("\n \n" + "MODEL: " + str(models[i]) +
                                     ", EXPERIMENT: " + str(exp) +
                                     ", VARIABLE: " + str(var) +
                                     ", FREQUENCY: " + str(frequency) + "\n")
                        if not exp == 'historical':
                            data_acq_freva_search_ECROPS.freva_search_ssp(project, models[i], var, frequency, exp)
                            logging.info('\n\n **** Finished with SSP files  **** \n \n')
                        if exp == 'historical':
                            data_acq_freva_search_ECROPS.freva_search_historical(project, models[i], var, frequency)
                            logging.info('\n\n **** Finished with Historical files **** \n\n')

        if project == 'reanalysis':
            for var in variables_era5_daily_monthly:
                logging.info("\n \n" + "PROJECT: " + str(project) +
                             ", EXPERIMENT: " + str(exp_reanalysis) +
                             ", VARIABLE: " + str(var) +
                             ", FREQUENCY: " + str(frequency[2]) + "\n")
                data_acq_freva_search_ECROPS.freva_search_reanalysis(project, exp_reanalysis, var, frequency[2])
        
            for var in variables_era5_daily_monthly:
                logging.info("\n \n" + "PROJECT: " + str(project) +
                             ", EXPERIMENT: " + str(exp_reanalysis) +
                             ", VARIABLE: " + str(var) +
                             ", FREQUENCY: " + str(frequency[1]) + "\n")
                data_acq_freva_search_ECROPS.freva_search_reanalysis(project, exp_reanalysis, var, frequency[1])
            
            for var in variables_era5_hourly:
                logging.info("\n \n" + "PROJECT: " + str(project) +
                             ", EXPERIMENT: " + str(exp_reanalysis) +
                             ", VARIABLE: " + str(var) +
                             ", FREQUENCY: " + str(frequency[0]) + "\n")
                data_acq_freva_search_ECROPS.freva_search_reanalysis(project, exp_reanalysis, var, frequency[0])

                
if __name__ == '__main__':
    main()
