import csv
import shutil
import os
import glob
import sys

def copy_files_from_csv(csv_file_path, destination_folder, variable, experiment):
    """
    Copies files listed in a CSV file to a structured destination folder.

    :param csv_file_path: Path to the CSV file containing file paths.
    :param destination_folder: Base path to the destination folder.
    :param variable: Variable name (e.g., 'lai', 'tasmax').
    :param experiment: Experiment name (e.g., 'historical', 'past2k').
    """
    # Open the CSV file and read the file paths
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        for row in csv_reader:
            original_file_path = row[0].strip()
            
            # Extract ensemble name from the file path
            path_components = original_file_path.split('/')
            try:
                # Find the position of the experiment in the path
                exp_index = path_components.index(experiment)
                ensemble = path_components[exp_index + 1]  # Ensemble is next component
            except (ValueError, IndexError):
                print(f"Could not extract ensemble from: {original_file_path}")
                continue
            
            # Build destination path: destination_folder/variable/experiment/ensemble/
            dest_dir = os.path.join(destination_folder, variable, experiment, ensemble)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file to destination
            file_name = os.path.basename(original_file_path)
            dest_file_path = os.path.join(dest_dir, file_name)
            
            try:
                shutil.copy2(original_file_path, dest_file_path)
                print(f"Copied: {original_file_path} -> {dest_file_path}")
                sys.stdout.flush()
            except FileNotFoundError:
                print(f"File not found: {original_file_path}")
                sys.stdout.flush()
            except Exception as e:
                print(f"Error copying {original_file_path}: {e}")
                sys.stdout.flush()

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='Copy CMIP6 files to structured directories based on CSV lists.'
    )
    parser.add_argument('-s', '--source', 
                        default='./data_acq/',
                        help='Folder containing CSV files (default: ./data_acq/)')
    parser.add_argument('-d', '--dest', 
                        default='./data_raw/',
                        help='Destination base folder (default: ./data_raw/)')
    
    args = parser.parse_args()
    
    # Use the paths from arguments (or defaults if not provided)
    data_acq_folder = args.source
    destination_folder = args.dest
    
    # Find all CSV files
    csv_files = sorted(glob.glob(os.path.join(data_acq_folder, "*.csv")))
    print(f"Found CSV files: {csv_files}")
    sys.stdout.flush()

    if not csv_files:
        print(f"No CSV files found in: {data_acq_folder}")
        sys.stdout.flush()
        return

    # Process each CSV file
    for csv_file_path in csv_files:
        print(f"Processing CSV: {csv_file_path}")
        sys.stdout.flush()
        
        # Extract variable and experiment from filename
        filename = os.path.basename(csv_file_path)
        parts = filename.split('__cmip6_')[-1].split('_[')[0].split('_')
        
        # Determine experiment and variable
        if parts[0] == 'past2k':
            experiment = 'past2k'
            variable = parts[1]
        else:
            experiment = 'historical'
            variable = parts[0]
        
        # Copy files with structured paths
        copy_files_from_csv(csv_file_path, destination_folder, variable, experiment)

if __name__ == "__main__":
    main()