from __future__ import annotations
import xarray as xr
import numpy as np
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", message=r"Passing", category=FutureWarning)
import glob
import argparse
from typing import Union
import pandas as pd


def merge_var(
    list_var: list[str],
    short_name: list[str],
    local_path: str,
    out_path: str,
    area: Union[bool, str],
):
    """
    merge_var

    Merge multiple NetCDF files for each variable in `list_var` into a single NetCDF file.

    This function processes a list of variables (`list_var`), finds all corresponding NetCDF files
    in the specified directory (`local_path`), and merges them along the time dimension. The merged
    data is saved as a new NetCDF file with a name derived from `short_name`.

    Parameters
    ----------
    list_var : list of str
        List of variable identifiers used to locate NetCDF files. Each variable identifier is used
        to match files in the `local_path` directory.
    short_name : list of str
        List of short names corresponding to each variable in `list_var`. These names are used to
        generate the output filenames.
    local_path : str
        Path to the directory containing the input NetCDF files. The function will search for files
        matching the pattern `{local_path}*{var}*.nc` for each variable in `list_var`.
    out_path : str
        Path to the directory where the output NetCDF files will be saved.
    area : bool or str
        Default False. If specified an area, that whould be the region selected on the Xarray. Sould
        follow the order: North, West, South, East.

    Returns
    -------
    None
        The function does not return any value. It saves the merged data as NetCDF files in the
        `out_path` directory.

    Notes
    -----
    - The function assumes that all input NetCDF files have consistent dimensions and variables.
    - The function uses `xarray` for handling NetCDF files and `tqdm` for progress tracking.

    Examples
    --------
    >>> merge_var(['167', '168'], ['t2m', 'dp'], './raw/', './features/')
    # This will merge all files matching './raw/*167*.nc' and './raw/*168*.nc' into two separate
    # output files: './features/data_glob_1D_t2m.nc' and './features/data_glob_1D_dp.nc'.
    """
    for idx, var in enumerate(tqdm(list_var, desc="Processing variables")):
        files = np.array(sorted(glob.glob(f"{local_path}*{var}*.nc")))
        print(f"\nfiles:\n {files}")
        data = xr.open_dataset(files[0], engine="netcdf4")
        # data = data.drop_vars('depth_bnds')
        data = data.sortby(data.lat)
        data = data.sortby(data.lon)
        new_times = [
            t.replace(hour=int(files[0][-5:-3]), minute=0, second=0)
            for t in pd.to_datetime(data.time.values)
        ]
        data = data.assign_coords(time=new_times)
        if isinstance(area, str):
            # North, West, South, East.
            area_list = np.array(area.split(",")).astype(int)
            data = data.sel(
                lat=slice(area_list[2], area_list[0]),
                lon=slice(area_list[1], area_list[3]),
            )
        for file in tqdm(files[1:], desc=f"Merging files for {var}", leave=False):
            # print(f'Loading: {file}')
            try:
                d_i = xr.open_dataset(file, engine="netcdf4")
            except Exception as ex:
                print(f"Exception loading file {file} with:\n{ex}")
            # d_i = d_i.drop_vars('depth_bnds')
            else:
                d_i = d_i.sortby(d_i.lat)
                d_i = d_i.sortby(d_i.lon)
                new_times = [
                    t.replace(hour=int(file[-5:-3]), minute=0, second=0)
                    for t in pd.to_datetime(d_i.time.values)
                ]
                d_i = d_i.assign_coords(time=new_times)
                if isinstance(area, str):
                    area_list = np.array(area.split(',')).astype(int)
                    d_i = d_i.sel(lat=slice(area_list[2],area_list[0]), lon=slice(area_list[1],area_list[3]))
                data = xr.concat([data, d_i], dim='time')
                d_i.close()
        # data.to_netcdf(f'{out_path}data_{area if area else "glob"}_1D_{short_name[idx]}.nc'.replace(",", "").replace(" ", ""))
        data = data.sortby(data.time)
        data.to_netcdf(
            f"{out_path}{short_name[idx]}_1993-2016_.nc".replace(",", "").replace(
                " ", ""
            )
        )
    return


# data = xr.open_dataset(files_pred[0])#.drop_dims('plev')
# data = data.squeeze(dim="plev")
# for idx, f in tqdm(enumerate(files_pred[1:]), total=len(files_pred[1:]), desc="Processing vars"):
# #for f in tqdm(files_pred[1:-1], total=len(files_pred[1:-1]), desc="Processing vars"):
#     d_i = xr.open_dataset(f)
#     print(idx)
#     if idx==len(files_pred[1:])-1:
#         d_i = d_i.squeeze(dim="depth")
#     data[list(d_i.data_vars)[0]] = (('time', 'lat', 'lon'), d_i[list(d_i.data_vars)[0]].data)
#     d_i.close()


def main():
    # Parser initialization
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--var",
        dest="var",
        help="Specify which variable to merge. Could be a single value or a comma-separated list.",
    )
    parser.add_argument(
        "-sn",
        "--short_name",
        dest="short_name",
        help="Specify which is the short name to save the variable. Could be a single value or a comma-separated list.",
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="local_path",
        help="Local path to the directory where the variable is located.",
    )
    parser.add_argument(
        "-o",
        "--outpath",
        dest="out_path",
        help="Path to the output directory where to save the result.",
    )
    parser.add_argument(
        "-a",
        "--area",
        dest="area",
        help="Sub-region of interest. A str list in order: North, West, South, East.",
    )
    args = parser.parse_args()

    # Default values
    var = "168"
    short_name = ["dp"]
    local_path = "./raw/"
    out_path = "./features/"
    area = False

    # Override defaults if arguments are provided
    if args.var is not None:
        var = (
            args.var.split(",") if "," in args.var else [args.var]
        )  # Handle single value or list
    if args.short_name is not None:
        short_name = (
            args.short_name.split(",") if "," in args.short_name else [args.short_name]
        )  # Handle single value or list
    if args.local_path is not None:
        local_path = args.local_path
    if args.out_path is not None:
        out_path = args.out_path
    if args.area is not None:
        area = args.area
    for i in range(1, 26):
        print(f"\nRunning for ens {i:02d}\n")
        short_name_i = [str(short_name[0]).replace("_01", f"_{i:02d}")]
        local_path_i = local_path.replace("_01", f"_{i:02d}")
        out_path_i = out_path.replace("_01", f"_{i:02d}")
        print(f"\nShort name {short_name}")
        print(f"\nLocal path {local_path}")
        print(f"\nOut path {out_path}\n")
        print(f"\nShort name i {short_name_i}")
        print(f"\nLocal path i {local_path_i}")
        print(f"\nOut path i {out_path_i}\n")
        merge_var(var, short_name_i, local_path_i, out_path_i, area)
    # If no need for repet ir for several experiments, then you could
    # remode the for-loop and use instead:
    # merge_var(var, short_name, local_path, out_path, area)


if __name__ == "__main__":
    main()
