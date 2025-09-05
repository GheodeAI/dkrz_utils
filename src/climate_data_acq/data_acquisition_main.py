#################################################################################
# Title: Main class routine for searching and logging available FREVA datasets
# module load order: python3, clint, xces, then run script
# Author: Odysseas Vlachopoulos, Cosmin M. Marina, Eugenio Lorente-Ramos
# Project: testing
##################################################################################

import logging
import sys

import data_acq_freva_search_ECROPS
import os
import argparse


def copy_data(projects, models, variables_cmip, variables_era5_daily_monthly, variables_era5_hourly, frequency, exp_cmip, exp_reanalysis, homevardir):
    # First initialize a logger instance
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True,
        handlers=[
            logging.FileHandler("LOG_Data_Acquisition_FREVA_output.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info("Started Freva files main programme \n")
    freq_longname_map = {"mon": "monthly", "day": "daily", "hour": "hourly"}

    for project in projects:
        project = project.lower()
        match project:
            case "cmip6":
                for model in models:
                    model = model.lower()
                    for exp in exp_cmip6:
                        exp = exp.lower()
                        for var in variables_cmip:
                            var = var.lower()
                            logging.info(f"\n \nMODEL: {model}, EXPERIMENT: {exp}, VARIABLE: {var}, FREQUENCY: {freq}\n")

                            if exp == "historical":
                                data_acq_freva_search_ECROPS.freva_search_historical(project, model, var, frequency, homevardir)
                                logging.info("\n\n **** Finished with Historical files **** \n\n")
                            else:
                                data_acq_freva_search_ECROPS.freva_search_ssp(project, model, var, frequency, exp, homevardir)
                                logging.info("\n\n **** Finished with SSP files  **** \n \n")

            case "reanalysis":
                for freq in frequency:
                    for exp_reanalysis_i in exp_reanalysis:
                        freq = freq.lower()
                        freq_longname = freq_longname_map[freq]

                        var_set = None
                        match freq:
                            case "mon" | "day":
                                var_set = variables_era5_daily_monthly
                            case "hour":
                                var_set = variables_era5_hourly
                            case _:
                                raise ValueError("Incorrect frequency, try 'mon', 'day' or 'hour'.")

                        for var in var_set:
                            var = var.lower()
                            logging.info(f"\n \nPROJECT: {project}, EXPERIMENT: {exp_reanalysis_i}, VARIABLE: {var}, FREQUENCY: {freq}\n")
                            data_acq_freva_search_ECROPS.freva_search_reanalysis(project, exp_reanalysis_i, var, freq, homevardir)
                            logging.info(f"\n\n **** Finished with ERA5 {freq_longname} data files  **** \n \n")

            case _:
                ValueError(f"Project {project} not recognized, try 'cmip6' or 'reanalysis'")


def main():
    # projects = ['cmip6', 'reanalysis']
    # models = ['cesm2',
    #           'cnrm-cm6-1-HR',
    #           'gfdl-esm4',
    #           'ec-earth3',
    #           'mpi-esm1-2-hr',
    #           'mpi-esm1-2-lr',
    #           'noresm2-mm',
    #           'hadgem3-gc31-mm']

    # variables_cmip = ["tdps", "ua", "va", "tasmax", "lai"]

    # variables_era5_daily_monthly = ['tasmax', 'tasmin', 'tas', 'pr', 'rsds', 'tdps', 'sfcwind', 'hurs']
    # variables_era5_hourly = ['uas', 'vas', 'rsds', 'tdps']

    # frequency = ['hour', 'day', 'mon']
    # exp_cmip6 = ['ssp370', 'ssp585', 'historical', 'past2k]
    # exp_reanalysis = ["era5"]
    # homevardir = "/work/bb1478/b382610/wildfires/data/find_vars_cmip6/data_acq/"

    parser = argparse.ArgumentParser(prog="Train concrete with prev. classification")
    parser.add_argument("-p", "--projects", default="reanalysis")
    parser.add_argument("-m", "--models", default="")
    parser.add_argument("--cmip6_vars", default="")
    parser.add_argument("--era5_vars_month", default="")
    parser.add_argument("--era5_vars_hour", default="")
    parser.add_argument("--exp_cmip", default="")
    parser.add_argument("--exp_reanalysis", default="era5")
    parser.add_argument("-f", "--frequency", default="")
    # parser.add_argument("-V", "--verify", store_action=True)
    parser.add_argument("-d", "--dir", type=str, required=True)

    args = parser.parse_args()

    copy_data(
        args.projects.split(","),
        args.models.split(","),
        args.cmip6_vars.split(","),
        args.era5_vars_month.split(","),
        args.era5_vars_hour.split(","),
        args.frequency.split(","),
        args.exp_cmip.split(","),
        args.exp_reanalysis.split(","),
        args.dir,
    )


if __name__ == "__main__":
    main()
