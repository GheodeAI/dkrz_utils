import argparse
import pandas as pd
import xarray as xr
import os
from tqdm import tqdm
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(description='Build Xarray from CSV index and ensemble NetCDF files.')
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the CSV file')
    parser.add_argument('--variable', type=str, required=True, help='Variable name (e.g., gz500, msl)')
    parser.add_argument('--input_dir', type=str, required=True, help='Input directory for ensemble data (e.g., ./data/ecmwf/)')
    parser.add_argument('--output_path', type=str, required=True, help='Output path for the resulting NetCDF file')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Leer el CSV y ordenar por 'emo-day' y 'rank'
    df = pd.read_csv(args.csv_path, parse_dates=['time', 'emo-day'])
    df = df.sort_values(['emo-day', 'rank']).reset_index(drop=True)
    
    # Obtener dimensiones y coordenadas base del primer archivo (asumiendo que todas las variables tienen la misma estructura)
    example_ens = 'ens_01'  # Ejemplo para obtener coordenadas
    example_path = os.path.join(args.input_dir, example_ens, args.variable, f'ecmwf_{example_ens.split("_")[1]}_{args.variable}_1993-2016_.nc')
    with xr.open_dataset(example_path) as ds:
        lats = ds.lat.values
        lons = ds.lon.values
        time_coords = df['emo-day'].unique()
        
    # Inicializar Dataset vacío con Dask para manejo de memoria
    data_shape = (len(time_coords), 25, len(lats), len(lons))  # (time, analog, lat, lon)
    data = xr.DataArray(
        np.full(data_shape, np.nan, dtype=np.float32),
        dims=['time', 'analog', 'lat', 'lon'],
        coords={
            'time': pd.to_datetime(time_coords),
            'analog': np.arange(25),
            'lat': lats,
            'lon': lons
        },
        name=args.variable
    )
    ds_out = xr.Dataset({args.variable: data})
    
    # Procesar cada fila del CSV
    for idx, row in tqdm(df.iterrows(), total=len(df), desc='Processing'):
        # Construir ruta al archivo NetCDF
        ens = row['ens']
        nc_path = os.path.join(args.input_dir, ens, args.variable, f'ecmwf_{ens.split("_")[1]}_{args.variable}_1993-2016_.nc')
        
        # Calcular el tiempo objetivo (time + leadtime hours)
        target_time = row['time'] + pd.to_timedelta(row['leadtime'], unit='h')
        
        try:
            # Cargar el dato específico
            with xr.open_dataset(nc_path) as ds:
                # Seleccionar el tiempo más cercano (suponiendo que el leadtime está en horas)
                ds_target = ds.sel(time=target_time, method='nearest')
                value = ds_target[args.variable].load()
                
                # Asignar al Dataset de salida
                time_idx = np.where(ds_out.time == row['emo-day'])[0][0]
                analog_idx = int(row['rank'].replace("Analog", ""))
                ds_out[args.variable][time_idx, analog_idx, :, :] = value
        except FileNotFoundError:
            print(f"Archivo no encontrado: {nc_path}", flush=True)
            continue
        except KeyError:
            print(f"Variable {args.variable} no encontrada en {nc_path}", flush=True)
            continue
    
    # Guardar el Dataset resultante
    out_path = os.path.join(args.output_path, args.variable, f'ecmwf_{args.variable}_1993-2016_.nc')
    ds_out.to_netcdf(out_path)
    print(f"Dataset guardado en {out_path}")

if __name__ == '__main__':
    main()