import csv
import shutil
import os
import glob
import sys

def copy_files_from_csv(csv_file_path, destination_folder):
    """
    Copies files listed in a CSV file to a specified destination folder.

    :param csv_file_path: Path to the CSV file containing file paths.
    :param destination_folder: Path to the destination folder where files will be copied.
    """
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Open the CSV file and read the file paths
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        for row in csv_reader:
            # Assuming each row has only one column (the file path)
            original_file_path = row[0].strip()  # Remove any leading/trailing whitespace
            
            # Get the file name from the original path
            file_name = os.path.basename(original_file_path)
            
            # Define the destination file path
            destination_file_path = os.path.join(destination_folder, file_name)
            
            try:
                # Copy the file to the destination folder
                shutil.copy2(original_file_path, destination_file_path)
                print(f"Copied: {original_file_path} -> {destination_file_path}")
                sys.stdout.flush()
            except FileNotFoundError:
                print(f"File not found: {original_file_path}")
                sys.stdout.flush()
            except Exception as e:
                print(f"Error copying {original_file_path}: {e}")
                sys.stdout.flush()

def main():
    # Define the paths
    data_acq_folder = "./data_acq/" 
    destination_folder = './data_raw/'
    # Use glob to find all CSV files in the 'data_acq' folder
    csv_files = sorted(glob.glob(os.path.join(data_acq_folder, "*.csv")))
    print(csv_files)
    sys.stdout.flush()

    # Check if any CSV files were found
    if not csv_files:
        print(f"No CSV files found in the folder: {data_acq_folder}")
        sys.stdout.flush()
        return

    # Iterate over each CSV file and call the copy function
    for csv_file_path in csv_files:
        print(f"Processing CSV file: {csv_file_path}")
        sys.stdout.flush()
        copy_files_from_csv(csv_file_path, destination_folder + csv_file_path.split('__cmip6_')[1].split('_[')[0]  + '/')

if __name__ == "__main__":
    main()
