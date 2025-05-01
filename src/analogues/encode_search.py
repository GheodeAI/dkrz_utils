import va_am
import keras
import json
import numpy as np
import tensorflow as tf
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from va_am.utils import AutoEncoders
from va_am import calculate_interest_region, analogSearch
import datetime
from pathlib import Path
import argparse
import sys
from tqdm import tqdm
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
import glob


def reinitialize(model):
    for l in model.layers:
        if isinstance(l, tf.keras.Model):
            reinitialize(l)
            continue
        if hasattr(l, "kernel_initializer"):
            l.kernel.assign(l.kernel_initializer(tf.shape(l.kernel)))
        if hasattr(l, "bias_initializer"):
            l.bias.assign(l.bias_initializer(tf.shape(l.bias)))
        if hasattr(l, "recurrent_initializer"):
            l.recurrent_kernel.assign(
                l.recurrent_initializer(tf.shape(l.recurrent_kernel))
            )


def train_base_model(
    model_enc,
    model_dec,
    year_start_str,
    year_end_str,
    X_train,
    idx=0,
    hw="params.json",
    model_type="",
):
    hw_name = hw.split(".")[0].split("/")[-1]
    x_input = keras.Input(shape=X_train.shape[1:])
    print(f"\nx_input: {x_input}\n")
    print(f"\nx_input shape: {X_train.shape[1:]}\n")
    print(f"\nx_input shape: {X_train.shape}\n")
    x = model_dec(model_enc(x_input))
    autoencoder = keras.Model(x_input, x)
    autoencoder.compile(optimizer=keras.optimizers.Adam(1e-4), loss="mse")

    autoencoder.fit(X_train, X_train, epochs=500, validation_split=0.15)
    Path(f"./models/{hw_name}").mkdir(parents=True, exist_ok=True)
    model_enc.save(
        f"./models/{hw_name}/MvAE_{hw_name}_{model_type}_{year_start_str}-{year_end_str}.h5"
    )
    model_dec.save(
        f"./models/{hw_name}/MvAE_{hw_name}_{model_type}_{year_start_str}-{year_end_str}_dec_.h5"
    )

    return autoencoder


def load_data_past2k(
    year_start,
    year_end,
    year_part,
    year_part_end,
    idx=0,
    hw="params.json",
    out_preprocess=["x_train_pre_pred", "x_test_pre_pred"],
):
    with open(hw) as f:
        params = json.load(f)
    params["name"] = params["name"].replace("#", str(idx))
    params["pre_init"] = params["pre_init"].replace("7000", str(year_part))
    params["pre_end"] = params["pre_end"].replace("7099", str(year_part_end))
    params["target_dataset"] = (
        params["target_dataset"]
        .replace("7000", str(year_start))
        .replace("7099", str(year_end))
    )
    params["pred_dataset"] = (
        params["pred_dataset"]
        .replace("7000", str(year_start))
        .replace("7099", str(year_end))
    )
    params["ident_dataset"] = (
        params["ident_dataset"]
        .replace("7000", str(year_start))
        .replace("7099", str(year_end))
    )

    params["out_preprocess"] = out_preprocess
    params["data_of_interest_init"] = pd.Timestamp(params["data_of_interest_init"])
    params["data_of_interest_end"] = pd.Timestamp(params["data_of_interest_end"])

    return va_am.perform_preprocess(params)


def load_data_ecmwf(
    year_start,
    year_end,
    hw="params.json",
    out_preprocess=["time_indust_pred", "indust_target", "img_size"],
    params=None,
):
    if params is None:
        with open(hw) as f:
            params = json.load(f)
    params_org = params.copy()
    params["name"] = params["name"].replace("#", "0")

    params["out_preprocess"] = out_preprocess[1:]
    params["period"] = "post"

    indust_target, img_size = va_am.perform_preprocess(params)

    params["post_init"] = pd.Timestamp(
        str(year_start) + params["post_init"][4:] + " 00:00:00"
    )
    params["post_end"] = pd.Timestamp(
        str(year_end) + params["post_end"][4:] + " 06:00:00"
    )
    if type(params["data_of_interest_init"]) != pd.Timestamp:
        params["data_of_interest_init"] = pd.Timestamp(
            params["data_of_interest_init"] + " 00:00:00"
        )
    if type(params["data_of_interest_end"]) != pd.Timestamp:
        params["data_of_interest_end"] = pd.Timestamp(
            params["data_of_interest_end"] + " 06:00:00"
        )

    time_indust_pred = va_am.perform_preprocess(params)
    return time_indust_pred, indust_target, img_size


def load_data_era5(
    year_start,
    year_end,
    hw="params.json",
    out_preprocess=[
        "indust_pred",
        "data_of_interest_pred",
        "time_indust_pred",
        "indust_target",
        "img_size",
    ],
    params=None,
):
    if params is None:
        with open(hw) as f:
            params = json.load(f)
    params["name"] = params["name"].replace("#", "0")
    params["post_init"] = str(year_start) + params["post_init"][4:]
    params["post_end"] = str(year_end) + params["post_end"][4:]

    params["out_preprocess"] = out_preprocess
    params["period"] = "post"
    if type(params["data_of_interest_init"]) != pd.Timestamp:
        params["data_of_interest_init"] = pd.Timestamp(
            params["data_of_interest_init"] + " 00:00:00"
        )
    if type(params["data_of_interest_end"]) != pd.Timestamp:
        params["data_of_interest_end"] = pd.Timestamp(
            params["data_of_interest_end"] + " 06:00:00"
        )

    return va_am.perform_preprocess(params)


def train_all_past2k(
    model_enc, model_dec, year_range=(0, 1850), hw="params.json", model_type=""
):
    for i, year_start in enumerate(np.arange(7000, 8850, 100)):
        idx = i + 1
        year_end = year_start + 99
        if year_start == 8800:
            year_end = 8850
        print(f"idx: {idx}", flush=True)
        print(f"year_start: {year_start}", flush=True)
        print(f"year_end: {year_end}", flush=True)
        for j, year_part in enumerate(np.arange(year_start, year_end, 25)):
            year_part_end = year_part + 24
            if year_part == 8825:
                year_part_end = 8850
            print(f"j: {j}", flush=True)
            print(f"year_part: {year_part}", flush=True)
            print(f"year_part_end: {year_part_end}", flush=True)
            X_train, _ = load_data_past2k(
                year_start, year_end, year_part, year_part_end, idx, hw
            )
            X_train = np.nan_to_num(X_train)
            train_base_model(
                model_enc,
                model_dec,
                year_part - 7000,
                year_part_end - 7000,
                X_train,
                idx,
                hw,
                model_type,
            )
            print(f"trained on past2k up to year {year_end}.", flush=True)
    return model_enc, model_dec


def train_era5(
    model_enc, model_dec, year_range=(1940, 2022), hw="params.json", model_type=""
):
    X_train = load_data_era5(
        year_range[0], year_range[1], hw, out_preprocess=["indust_pred"]
    )[0]
    print(f"\nX_train shape: {np.shape(X_train)}\n")
    X_train = np.nan_to_num(X_train)
    train_base_model(
        model_enc, model_dec, year_range[0], year_range[1], X_train, 0, hw, model_type
    )
    print(f"trained on era5 up to year {year_range[1]}.", flush=True)
    return model_enc, model_dec


def encode_past2k(hw, model_type="", year_range=(0, 1850)):
    hw_name = hw.split(".")[0].split("/")[-1]
    for i, year_start in enumerate(np.arange(year_range[0], year_range[1], 100)):
        idx = i + 1
        year_end = year_start + 99
        if year_start == 1800:
            year_end = 1850
        print(f"idx: {idx}", flush=True)
        print(f"year_start: {year_start}", flush=True)
        print(f"year_end: {year_end}", flush=True)
        for j, year_part in enumerate(np.arange(year_start, year_end, 25)):
            year_part_end = year_part + 24
            if year_part == 1825:
                year_part_end = 1850
            print(f"j: {j}", flush=True)
            print(f"year_part: {year_part}", flush=True)
            print(f"year_part_end: {year_part_end}", flush=True)
            AE_ind = keras.models.load_model(
                f"./models/{hw_name}/MvAE_{hw_name}_{model_type}_{str(year_part)}-{str(year_part_end)}.h5",
                custom_objects={"keras": keras, "AutoEncoders": AutoEncoders},
            )
            encode_era5(
                AE_ind,
                year_part_range=(year_part, year_part_end),
                hw=hw,
                model_type="past2k",
                idx=4 * i + j,
            )
    return


def encode_ecmwf(AE_ind, year_range=(1993, 2016), hw="params.json"):
    hw_name = hw.split(".")[0].split("/")[-1]
    with open(hw) as f:
        params = json.load(f)
    for i in range(1, 26):
        dataset_name = params["target_dataset"].replace("_01", f"_{i:02d}")
        params_i = params.copy()
        params_i["target_dataset"] = dataset_name
        params_i["pred_dataset"] = dataset_name
        indust_pred = load_data_era5(
            year_range[0], year_range[1], hw, ["indust_pred"], params=params_i
        )
        indust_pred_encoded = AE_ind.predict(indust_pred)
        print(f"encoded on ecmwf for ens {i:02d}.", flush=True)
        del indust_pred
        np.save(
            f"./data/encoded/indust_pred_encoded_ens{i:02d}_{year_range[0]}-{year_range[1]}_{hw_name}.npy",
            indust_pred_encoded,
        )
    return


def encode_era5(
    AE_ind,
    year_range=(1940, 2022),
    year_part_range=(1940, 2022),
    hw="params.json",
    model_type="",
    idx=0,
):
    hw_name = hw.split(".")[0].split("/")[-1]
    if model_type == "past2k":
        indust_pred = load_data_past2k(
            year_range[0],
            year_range[1],
            year_part_range[0],
            year_part_range[1],
            idx=idx,
            hw=hw,
            out_preprocess=["indust_pred"],
        )
    else:
        indust_pred = load_data_era5(year_range[0], year_range[1], hw, ["indust_pred"])
    indust_pred_encoded = AE_ind.predict(indust_pred)
    print(f"encoded on era5 up to year {year_range[1]}.", flush=True)
    del indust_pred
    np.save(
        f"./data/encoded/indust_pred_encoded_{year_part_range[0]}-{year_part_range[1]}_{hw_name}.npy",
        indust_pred_encoded,
    )
    del indust_pred_encoded
    if model_type == "past2k":
        data_of_interest_pred = load_data_past2k(
            year_range[0],
            year_range[1],
            year_part_range[0],
            year_part_range[1],
            idx=idx,
            hw=hw,
            out_preprocess=["data_of_interest_pred"],
        )
    else:
        data_of_interest_pred = load_data_era5(
            year_range[0], year_range[1], hw, ["data_of_interest_pred"]
        )
    data_of_interest_pred_encoded_ind = AE_ind.predict(data_of_interest_pred)
    print(f"encoded on event {hw_name}.", flush=True)
    del data_of_interest_pred
    np.save(
        f"./data/encoded/data_of_interest_pred_encoded_ind_{year_part_range[0]}-{year_part_range[1]}_{hw_name}.npy",
        data_of_interest_pred_encoded_ind,
    )
    del data_of_interest_pred_encoded_ind
    return


def search_ecmwf(
    year_range=(1993, 2016), year_part_range=(1993, 2016), hw="params.json"
):
    hw_name = hw.split(".")[0].split("/")[-1]
    with open(hw) as f:
        params = json.load(f)

    params_multiple = params.copy()

    current = datetime.datetime.now()
    int_reg = params["interest_region"]
    if params["interest_region_type"] == "coord":
        int_reg = calculate_interest_region(
            params["interest_region"],
            [
                params["latitude_min"],
                params["latitude_max"],
                params["longitude_min"],
                params["longitude_max"],
            ],
            params["resolution"],
            False,
            "file",
        )

    heatwave_period = np.arange(
        datetime.datetime.strptime(
            params_multiple["data_of_interest_init"], "%Y-%m-%d"
        ),
        datetime.datetime.strptime(params_multiple["data_of_interest_end"], "%Y-%m-%d")
        + datetime.timedelta(days=1),
        datetime.timedelta(days=1),
    )
    heatwave_period = np.array(list(map(pd.Timestamp, heatwave_period)))
    params_multiple["data_of_interest_init"] = heatwave_period
    params_multiple["data_of_interest_end"] = heatwave_period
    print(
        f"Heatwave period: {heatwave_period}\n {np.shape(heatwave_period)}\n",
        flush=True,
    )

    # indust_pred, data_of_interest_pred, time_indust_pred, indust_target, img_size = load_data_era5(year_range[0], year_range[1], hw, params=params)
    _, _, time_indust_pred_gen, indust_target_gen, img_size = load_data_era5(
        year_range[0], year_range[1], hw, params=params
    )
    for idx, init in enumerate(tqdm(params_multiple["data_of_interest_init"])):
        print(f"\nProcessing date: {init}", flush=True)
        params["data_of_interest_init"] = init
        params["data_of_interest_end"] = params_multiple["data_of_interest_end"][idx]
        min_idx_time = np.max([0, idx - 45])
        max_idx_time = np.min([idx + 45, len(heatwave_period) - 1])
        min_days_time = idx - min_idx_time
        max_days_time = max_idx_time - idx

        # Filtrar los datos en función de min_tim y max_time, calculando los indices dentro del .npy haciendo uso de un slice en time_indust_pred
        min_time = params["data_of_interest_init"] - datetime.timedelta(
            days=int(min_days_time)
        )
        max_time = params["data_of_interest_init"].replace(hour=6) + datetime.timedelta(
            days=int(max_days_time)
        )

        # Create boolean mask for the time range
        time_mask = (time_indust_pred_gen.time >= min_time) & (
            time_indust_pred_gen.time <= max_time
        )
        indices = np.where(time_mask.values)[0]
        start_time_idx = indices[0]  # Index of first occurrence >= min_time
        end_time_idx = indices[-1]  # Index of last occurrence <= max_time
        time_indust_pred = time_indust_pred_gen.sel(time=slice(min_time, max_time))
        indust_target = indust_target_gen.sel(time=slice(min_time, max_time))

        for i in tqdm(range(1, 26), desc="Processing ens"):
            # AE Post
            file_time_name = (
                f'./comparison-csv/analogues-ae-am-post-{params["season"]}{params["name"]}_ens{i:02d}_x{params["iter"]}-{params["data_of_interest_init"]}-epoch{params["n_epochs"]}-latent{params["latent_dim"]}-k{params["k"]}-arch{params["arch"]}-{"VAE" if params["use_VAE"] else "noVAE"}_{year_part_range[0]}-{year_part_range[1]}_{current.year}-{current.month}-{current.day}-{current.hour}-{current.minute}-{current.second}.npy'.replace(
                    " ", ""
                )
                .replace("'", "")
                .replace(",", "")
            )
            ## Load data
            indust_pred_encoded = np.load(
                f"./data/encoded/indust_pred_encoded_ens{i:02d}_{year_part_range[0]}-{year_part_range[1]}_{hw_name}.npy"
            )
            indust_pred_encoded = indust_pred_encoded[start_time_idx:end_time_idx]
            print(f"shape indust_pred_encoded: {np.shape(indust_pred_encoded)}")
            data_of_interest_pred_encoded_ind = np.load(
                f"./data/encoded/indust_pred_encoded_{year_part_range[0]}-{year_part_range[1]}_{hw_name[:-5]}era5.npy"
            )
            data_of_interest_pred_encoded_ind = data_of_interest_pred_encoded_ind[idx]
            print(
                f"shape data_of_interest_pred_encoded_ind: {np.shape(data_of_interest_pred_encoded_ind)}"
            )
            latent_analog_ind = analogSearch(
                params["p"],
                params["k"],
                indust_pred_encoded,
                data_of_interest_pred_encoded_ind,
                time_indust_pred,
                indust_target,
                False,
                threshold=0,
                img_size=img_size,
                iter=params["iter"],
                replace_choice=params["replace_choice"],
                target_var_name=params["target_var_name"],
                file_time_name=file_time_name,
            )
            del indust_pred_encoded  # , time_indust_pred indust_target
            # del data_of_interest_pred_encoded_ind

            dict_stats = {}
            # print(f'type latent_analog_ind 0 : {type(latent_analog_ind[0])}', flush=True)
            # print(f'type latent_analog_ind 1 : {type(latent_analog_ind[1])}', flush=True)
            # print(f'type latent_analog_ind 2 : {type(latent_analog_ind[2])}', flush=True)
            # print(f'sh latent_analog_ind 0 : {np.shape(latent_analog_ind[0])}', flush=True)
            # print(f'sh latent_analog_ind 1 : {np.shape(latent_analog_ind[1])}', flush=True)
            # print(f'latent_analog_ind 2 : {latent_analog_ind[2]}', flush=True)
            for j in range(params["iter"]):
                # dict_stats[f'Analog{j}'] = [f"{(np.sqrt(np.nansum((data_of_interest_pred_encoded_ind - latent_analog_ind[0][j])**2))/img_size):.10f}", str(latent_analog_ind[2][j].data)[:10], str(latent_analog_ind[2][j].data)[11:13]]
                dict_stats[f"Analog{j}"] = [
                    f"{latent_analog_ind[3][j]:.10f}",
                    str(latent_analog_ind[2][j].data)[:10],
                    str(latent_analog_ind[2][j].data)[11:13],
                ]
            del data_of_interest_pred_encoded_ind
            df_stats = pd.DataFrame.from_dict(
                dict_stats, orient="index", columns=["pred-diff", "time", "leadtime"]
            )
            Path("./comparison-csv").mkdir(parents=True, exist_ok=True)
            df_stats.to_csv(
                f'./comparison-csv/{params["season"]}{params["name"]}_ens{i:02d}_x{params["iter"]}-{params["data_of_interest_init"]}-epoch{params["n_epochs"]}-latent{params["latent_dim"]}-k{params["k"]}-arch{params["arch"]}-{"VAE" if params["use_VAE"] else "noVAE"}-analog-comparision-stats_{year_part_range[0]}-{year_part_range[1]}_{current.year}-{current.month}-{current.day}-{current.hour}-{current.minute}-{current.second}.csv'.replace(
                    " ", ""
                )
                .replace("'", "")
                .replace(",", "")
            )
    return


def search_past2k(year_range=(1940, 2022), year_part_range=(0, 1885), hw="params.json"):
    hw_name = hw.split(".")[0].split("/")[-1]
    for i, year_start in enumerate(
        np.arange(year_part_range[0], year_part_range[1], 100)
    ):
        idx = i + 1
        year_end = year_start + 99
        if year_start == 1800:
            year_end = 1850
        print(f"idx: {idx}", flush=True)
        print(f"year_start: {year_start}", flush=True)
        print(f"year_end: {year_end}", flush=True)
        for j, year_part in enumerate(np.arange(year_start, year_end, 25)):
            year_part_end = year_part + 24
            if year_part == 1825:
                year_part_end = 1850
            print(f"j: {j}", flush=True)
            print(f"year_part: {year_part}", flush=True)
            print(f"year_part_end: {year_part_end}", flush=True)
            search_era5(
                year_range=year_range, year_part_range=(year_part, year_part_end), hw=hw
            )
    return


def search_era5(
    year_range=(1940, 2022), year_part_range=(1940, 2022), hw="params.json"
):
    hw_name = hw.split(".")[0].split("/")[-1]
    with open(hw) as f:
        params = json.load(f)

    params_multiple = params.copy()

    current = datetime.datetime.now()
    int_reg = params["interest_region"]
    if params["interest_region_type"] == "coord":
        int_reg = calculate_interest_region(
            params["interest_region"],
            [
                params["latitude_min"],
                params["latitude_max"],
                params["longitude_min"],
                params["longitude_max"],
            ],
            params["resolution"],
            False,
            "file",
        )

    heatwave_period = np.arange(
        datetime.datetime.strptime(
            params_multiple["data_of_interest_init"], "%Y-%m-%d"
        ),
        datetime.datetime.strptime(params_multiple["data_of_interest_end"], "%Y-%m-%d")
        + datetime.timedelta(days=1),
        datetime.timedelta(days=1),
    )
    heatwave_period = np.array(list(map(pd.Timestamp, heatwave_period)))
    params_multiple["data_of_interest_init"] = heatwave_period
    params_multiple["data_of_interest_end"] = heatwave_period

    for idx, init in enumerate(params_multiple["data_of_interest_init"]):
        params["data_of_interest_init"] = init
        params["data_of_interest_end"] = params_multiple["data_of_interest_end"][idx]

        # Analog Post
        file_time_name = (
            f'./comparison-csv/analogues-am-post-{params["season"]}{params["name"]}x{params["iter"]}-{params["data_of_interest_init"]}-epoch{params["n_epochs"]}-latent{params["latent_dim"]}-k{params["k"]}-arch{params["arch"]}-{"VAE" if params["use_VAE"] else "noVAE"}_{year_part_range[0]}-{year_part_range[1]}_{current.year}-{current.month}-{current.day}-{current.hour}-{current.minute}-{current.second}.npy'.replace(
                " ", ""
            )
            .replace("'", "")
            .replace(",", "")
        )
        ## Load data
        (
            indust_pred,
            data_of_interest_pred,
            time_indust_pred,
            indust_target,
            img_size,
        ) = load_data_era5(year_range[0], year_range[1], hw, params=params)
        print(
            f"\nShape in encode_seach: {np.shape(data_of_interest_pred)}\n", flush=True
        )
        ## Search
        analog_ind = analogSearch(
            params["p"],
            params["k"],
            indust_pred,
            data_of_interest_pred,
            time_indust_pred,
            indust_target,
            False,
            threshold=0,
            img_size=img_size,
            iter=params["iter"],
            replace_choice=params["replace_choice"],
            target_var_name=params["target_var_name"],
            file_time_name=file_time_name,
        )
        ## Del data
        del indust_pred, data_of_interest_pred

        # AE Post
        file_time_name = (
            f'./comparison-csv/analogues-ae-am-post-{params["season"]}{params["name"]}x{params["iter"]}-{params["data_of_interest_init"]}-epoch{params["n_epochs"]}-latent{params["latent_dim"]}-k{params["k"]}-arch{params["arch"]}-{"VAE" if params["use_VAE"] else "noVAE"}_{year_part_range[0]}-{year_part_range[1]}_{current.year}-{current.month}-{current.day}-{current.hour}-{current.minute}-{current.second}.npy'.replace(
                " ", ""
            )
            .replace("'", "")
            .replace(",", "")
        )
        ## Load data
        indust_pred_encoded = np.load(
            f"./data/encoded/indust_pred_encoded_{year_part_range[0]}-{year_part_range[1]}_{hw_name}.npy"
        )
        data_of_interest_pred_encoded_ind = np.load(
            f"./data/encoded/data_of_interest_pred_encoded_ind_{year_part_range[0]}-{year_part_range[1]}_{hw_name}.npy"
        )
        data_of_interest_pred_encoded_ind = data_of_interest_pred_encoded_ind[idx]
        latent_analog_ind = analogSearch(
            params["p"],
            params["k"],
            indust_pred_encoded,
            data_of_interest_pred_encoded_ind,
            time_indust_pred,
            indust_target,
            False,
            threshold=0,
            img_size=img_size,
            iter=params["iter"],
            replace_choice=params["replace_choice"],
            target_var_name=params["target_var_name"],
            file_time_name=file_time_name,
        )
        del indust_pred_encoded, time_indust_pred, indust_target
        # del data_of_interest_pred_encoded_ind

        dict_stats = {}
        data_of_interest_pred, data_of_interest_target = load_data_era5(
            year_range[0],
            year_range[1],
            hw,
            ["data_of_interest_pred", "data_of_interest_target"],
            params=params,
        )
        for i in range(params["iter"]):
            dict_stats[f"WithoutAE-Pre{i}"] = [np.nan, np.nan, np.nan]

            dict_stats[f"WithoutAE-Post{i}"] = [
                np.nansum(np.abs(data_of_interest_pred - analog_ind[0][i])) / img_size,
                np.nanmean(
                    np.abs(
                        data_of_interest_target[params["interest_var_name"]].data
                        - analog_ind[1][i]
                    )[:, int_reg[0] : int_reg[1], int_reg[2] : int_reg[3]]
                ),
                np.nanmean(
                    analog_ind[1][i][int_reg[0] : int_reg[1], int_reg[2] : int_reg[3]]
                ),
                str(analog_ind[2][i].data)[:10],
            ]

            dict_stats[f"WithAE-Pre-Pre{i}"] = [np.nan, np.nan, np.nan]

            dict_stats[f"WithAE-Post-Post{i}"] = [
                np.nansum(
                    np.abs(data_of_interest_pred_encoded_ind - latent_analog_ind[0][i])
                )
                / img_size,
                np.nanmean(
                    np.abs(
                        data_of_interest_target[params["interest_var_name"]].data
                        - latent_analog_ind[1][i]
                    )[:, int_reg[0] : int_reg[1], int_reg[2] : int_reg[3]]
                ),
                np.nanmean(
                    latent_analog_ind[1][i][
                        int_reg[0] : int_reg[1], int_reg[2] : int_reg[3]
                    ]
                ),
                str(latent_analog_ind[2][i].data)[:10],
            ]

            dict_stats[f"Original{i}"] = [
                0,
                0,
                np.nanmean(
                    (
                        (data_of_interest_target[params["interest_var_name"]].data)[
                            :, int_reg[0] : int_reg[1], int_reg[2] : int_reg[3]
                        ]
                    )
                ),
            ]

        del (
            data_of_interest_pred,
            data_of_interest_target,
            data_of_interest_pred_encoded_ind,
        )
        df_stats = pd.DataFrame.from_dict(
            dict_stats,
            orient="index",
            columns=["pred-diff", "target-diff", "target", "time"],
        )
        Path("./comparison-csv").mkdir(parents=True, exist_ok=True)
        df_stats.to_csv(
            f'./comparison-csv/{params["season"]}{params["name"]}x{params["iter"]}-{params["data_of_interest_init"]}-epoch{params["n_epochs"]}-latent{params["latent_dim"]}-k{params["k"]}-arch{params["arch"]}-{"VAE" if params["use_VAE"] else "noVAE"}-analog-comparision-stats_{year_part_range[0]}-{year_part_range[1]}_{current.year}-{current.month}-{current.day}-{current.hour}-{current.minute}-{current.second}.csv'.replace(
                " ", ""
            )
            .replace("'", "")
            .replace(",", "")
        )
    return


def post_process_anal(hw="params.json"):
    with open(hw) as f:
        params = json.load(f)
    heatwave_period = np.arange(
        datetime.datetime.strptime(params["data_of_interest_init"], "%Y-%m-%d"),
        datetime.datetime.strptime(params["data_of_interest_end"], "%Y-%m-%d")
        + datetime.timedelta(days=1),
        datetime.timedelta(days=1),
    )
    print(f"heatwave_period: {heatwave_period}\n", flush=True)
    df_all_days = {}
    for idx, day_timestamp in enumerate(tqdm(heatwave_period)):
        day = str(day_timestamp)[:10]
        files_interest = glob.glob(f"comparison-csv/*{day}*.csv")
        files_interest = sorted(files_interest)
        list_interest = [pd.read_csv(df) for df in files_interest]
        print(f"list_interest: {list_interest}\n", flush=True)
        anal_name = list_interest[0]["Unnamed: 0"]
        daily_df = list_interest[0]
        daily_df["ens"] = f"ens_{1:02d}"
        for idx_df, df_i in enumerate(tqdm(list_interest[1:])):
            df_i["ens"] = f"ens_{idx_df + 2 :02d}"
            daily_df = pd.concat([daily_df, df_i], ignore_index=True)
        daily_df = daily_df.sort_values(by=["pred-diff"], ignore_index=True)
        daily_df = daily_df[:25].drop(columns=["Unnamed: 0"])
        daily_df["leadtime"] = daily_df["leadtime"].map("{:02d}".format)
        daily_df.insert(loc=0, column="rank", value=anal_name)
        daily_df["emo-day"] = day
        if idx == 0:
            df_all_days = daily_df
        else:
            df_all_days = pd.concat([df_all_days, daily_df], ignore_index=True)
    df_all_days.to_csv(
        f"./anal_dict/post_processed_analogues_{str(heatwave_period[0])[:4]}-{str(heatwave_period[-1])[:4]}.csv"
    )


def main():
    # Parser initialization
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--method",
        dest="method",
        help="Specify an method to execute between: \n 'encode' (default), 'search' or 'train'",
    )
    parser.add_argument(
        "-f",
        "--configfile",
        dest="conf",
        help="JSON file with configuration of parameters. If not specified and 'method' require the file, it will be searched at 'params.json'",
    )
    args = parser.parse_args()
    method = "encode"
    hw = "params.json"
    if args.method is not None:
        method = args.method
    if args.conf is not None:
        hw = args.conf
    with open(hw) as f:
        params = json.load(f)
    year_range = (
        int(params["post_init"].split("-")[0]),
        int(params["post_end"].split("-")[0]),
    )
    if method in ["train", "train-past2k"]:
        in_shape = (
            (params["latitude_max"] - params["latitude_min"]) // params["resolution"]
            + 1,
            (params["longitude_max"] - params["longitude_min"]) // params["resolution"]
            + 1,
        )
        print(
            f"Input shape for {hw.split('.')[0].split('/')[-1]}: {in_shape}", flush=True
        )
        ae_object = va_am.utils.AutoEncoders.AE_conv(
            in_shape, 400, arch=10, in_channels=1, out_channels=1
        )
        base_model_enc = ae_object.encoder
        base_model_dec = ae_object.decoder

        reinitialize(base_model_enc)
        reinitialize(base_model_dec)

        if method == "train-past2k":
            print("Train on Past2k data", flush=True)
            # base_model_enc, base_model_dec = train_all_past2k(base_model_enc, base_model_dec, year_range=(0, 1885), hw=hw, model_type="past2k")
            train_all_past2k(
                base_model_enc,
                base_model_dec,
                year_range=(0, 1885),
                hw=hw,
                model_type="past2k",
            )
        else:
            train_era5(
                base_model_enc,
                base_model_dec,
                year_range=(1940, 2022),
                hw=hw,
                model_type="era5",
            )

    elif method == "encode-past2k":
        encode_past2k(hw=hw, model_type="past2k")
    elif method == "encode":
        AE_ind = keras.models.load_model(
            params["file_AE_post"],
            custom_objects={"keras": keras, "AutoEncoders": AutoEncoders},
        )
        encode_era5(AE_ind, year_range=year_range, hw=hw)
        # encode_era5(AE_ind, year_range=(1993, 2016), year_part_range=(1993, 2016), hw=hw)
    elif method == "encode-ecmwf":
        AE_ind = keras.models.load_model(
            params["file_AE_post"],
            custom_objects={"keras": keras, "AutoEncoders": AutoEncoders},
        )
        encode_ecmwf(AE_ind, year_range=year_range, hw=hw)
    elif method == "search-past2k":
        search_past2k(year_range=year_range, year_part_range=(1600, 1885), hw=hw)
    elif method == "search":
        search_era5(year_range=year_range, year_part_range=year_range, hw=hw)
    elif method == "search-ecmwf":
        search_ecmwf(year_range=(1993, 2016), year_part_range=(1993, 2016), hw=hw)
    elif method == "post-process-anal":
        post_process_anal(hw=hw)
    else:
        message = ValueError(
            f"Not recognized {method} method. The available methods are 'encode' (default), 'search' or 'train'"
        )
        raise message
    return


if __name__ == "__main__":
    main()
