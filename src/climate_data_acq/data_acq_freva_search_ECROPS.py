#################################################################################
# Title: FREVA search routines and logging of available datasets
# Author: Odysseas Vlachopoulos
# Project: testing
# FREVA var names: ['institute', 'experiment', 'dataset', 'variable', 'cmor_table',
# 'ensemble', 'product', 'project', 'realm', 'model', 'time_frequency']
##################################################################################

import freva
import numpy as np
import logging
import os


def freva_search_ssp(project, model, var, freq, experiment, homevardir):
    """
    Get all the ssp files from FREVA for the inputs and write them to a csv,
    e.g. "mpi-esm1-2-hr__cmip6_ssp585_rsds_day.csv".
    Get the existing ssp unique ensemble ids to find the corresponding ensemble runs for the historical period, and
    write those to a csv,
    e.g. "mpi-esm1-2-hr__cmip6_ssp585_rsds_day_historical.csv"
    :param project: see configuration at data_acq_main.py
    :param model: see configuration at data_acq_main.py
    :param var: see configuration at data_acq_main.py
    :param freq: see configuration at data_acq_main.py
    :param experiment: see configuration at data_acq_main.py
    :return: nothing, writes csv files
    """
    ## 1. Get all the ssp files
    ssp_files = freva.databrowser(
        project=project,
        model=model,
        variable=var,
        time_frequency=freq,
        experiment=experiment,
    )

    ## iteratable freva generator object ssp_files can either be tranformed to a list or parsed,
    ## not both, it lives through one iteration it seems
    ssp_files_list = list(
        ssp_files
    )  # make the freva generator object ssp_files a list for list functions e.g. len()
    ssp_files_array = np.sort(ssp_files_list)

    ## 2. Get all the unique ensemble ids to be used in matching with all other ssp files
    all_ensembles = []
    for ssp_file in ssp_files_array:
        res = freva.facet_search(file=ssp_file, facet="ensemble")
        all_ensembles.append(
            res.get("ensemble")[0]
        )  # get the first (only) value of the dictionary <ensemble:value>

    unique_ensembles = np.unique(
        all_ensembles
    )  # then filter out only the unique ensemble values

    logging.info(f"{experiment} for {var} unique ensemble ids = {unique_ensembles}")

    # Get the number of ssp files per unique ensemble id: Function is called only for logging the number of files
    get_files_from_unique_ensembles(
        project, model, var, freq, experiment, unique_ensembles
    )

    ## 3. Get all the historical datasets we need by the ensemble id in unique_ensembles
    historical_files_array = get_files_from_unique_ensembles(
        project, model, var, freq, "historical", unique_ensembles
    )

    np_historical_files_array = np.sort(historical_files_array)
    ### logging.info(str(var) + " total HISTORICAL num of files = " + str(np_historical_files_array.size))

    ## Write everything to csv files
    ssp_csv_filename = f"{model}__{project}_{experiment}_{var}_{freq}.csv"
    ssp_files_array.tofile(os.path.join(homevardir, ssp_csv_filename), sep="\n")
    historical_csv_filename = (
        f"{model}__{project}_{experiment}_{var}_{freq}_historical.csv"
    )

    np_historical_files_array.tofile(
        os.path.join(homevardir, historical_csv_filename), sep="\n"
    )


def freva_search_historical(project, model, var, freq, homevardir):
    """
    Retreives all the historical files from FREVA and writes them to csv,
    e.g. "mpi-esm1-2-hr__cmip6_rsds_day_allhistorical.csv"
    :param project: see configuration at data_acq_main.py
    :param model: see configuration at data_acq_main.py
    :param var: see configuration at data_acq_main.py
    :param freq: see configuration at data_acq_main.py
    :return: nothing, writes csv files
    """
    ## 1. Get all the historical files
    historical_files = freva.databrowser(
        project=project,
        model=model,
        variable=var,
        time_frequency=freq,
        experiment="historical",
    )

    ## iteratable freva generator object ssp_files can either be tranformed to a list or parsed,
    ## not both, it lives through one iteration it seems
    historical_files_list = list(historical_files)
    historical_files_array = np.sort(historical_files_list)

    ### logging.info(str(experiment) + " for " + str(var) + " total num of files = " + str(ssp_files_array.size))

    ## 2. Get all the unique ensemble ids
    all_ensembles = []
    for historical_file in historical_files_array:
        res = freva.facet_search(file=historical_file, facet="ensemble")
        all_ensembles.append(
            res.get("ensemble")[0]
        )  # get the first and only value of the dictionary <ensemble:value>

    unique_ensembles = np.unique(
        all_ensembles
    )  # then filter out only the unique ensemble values
    logging.info(f"Historical for {var} unique ensemble ids = {unique_ensembles}")

    # Get the number of historical files per unique ensemble id: Function is calles only for logging the number of files
    get_files_from_unique_ensembles(
        project, model, var, freq, "historical", unique_ensembles
    )

    ## Write everything to csv files
    all_historical_csv = f"{model}__{project}_{var}_{freq}_allhistorical.csv"

    historical_files_array.tofile(
        os.path.join(homevardir, all_historical_csv), sep="\n"
    )


def freva_search_reanalysis(
    project, experiment, var, freq, homevardir
):  # , geopoten_value):
    """
    Retreive from FREVA all reanalysis files such as ERA5 and write the list to csv,
    e.g. "era5__reanalysis_day_tas.csv"
    :param project: see configuration at data_acq_main.py
    :param experiment: see configuration at data_acq_main.py
    :param var: see configuration at data_acq_main.py
    :param freq: see configuration at data_acq_main.py
    :param geopoten_value: see configuration at data_acq_main.py
    :return:
    """
    ## 1. Get all the reanalysis files with a variable
    reanalysis_files = freva.databrowser(
        project=project, time_frequency=freq, variable=var, experiment=experiment
    )

    reanalysis_files_list = list(reanalysis_files)
    reanalysis_files_array = np.sort(reanalysis_files_list)

    ## 3. Get all the unique ensemble ids for each var
    all_ensembles = []
    for reanalysis_file in reanalysis_files_array:
        res = freva.facet_search(file=reanalysis_file, facet="ensemble")
        all_ensembles.append(
            res.get("ensemble")[0]
        )  # get the first(and only) value of the dictionary <ensemble:value>

    unique_ensembles = np.unique(
        all_ensembles
    )  # then filter out only the unique ensemble values
    logging.info(
        f"{experiment} reanalysis for {var} unique ensemble ids = {unique_ensembles}"
    )

    ## Write everything to csv files
    all_reanalysis_csv_filename = f"{experiment}__{project}_{freq}_{var}.csv"

    reanalysis_files_array.tofile(
        os.path.join(homevardir, all_reanalysis_csv_filename), sep="\n"
    )


def get_files_from_unique_ensembles(
    project, model, var, freq, experiment, unique_ensemble_list
):
    """
    The inputs to this function are internal, although dictated by the data_acq_main.py . This function is called
    internally in order to retrieve from FREVA items using their ensemble id, used for corresponding ssp and historical
    runs and existing files in the system.
    :param project: see configuration at data_acq_main.py
    :param model: see configuration at data_acq_main.py
    :param var: see configuration at data_acq_main.py
    :param freq: see configuration at data_acq_main.py
    :param experiment: see configuration at data_acq_main.py
    :param unique_ensemble_list:
    :return: a list of filepaths
    """
    files_array = []
    for unique_ens in unique_ensemble_list:
        files = freva.databrowser(
            project=project,
            model=model,
            ensemble=unique_ens,
            variable=var,
            time_frequency=freq,
            experiment=experiment,
        )
        for file in files:
            files_array.append(file)

        logging.info(
            f"{experiment} {var} files for ensemble {unique_ens} = {len(files)}"
        )

    return files_array
