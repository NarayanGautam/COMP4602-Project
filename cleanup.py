import os
import glob

# Path to the directory where the script is located
dir_path = os.path.dirname(os.path.realpath(__file__))

# Find all .png files in the directory
png_files = glob.glob(os.path.join(dir_path, '*.png'))

if not png_files:
    print("No .png files found to delete.")
else:
    for file in png_files:
        try:
            os.remove(file)
            print(f"Deleted: {os.path.basename(file)}")
        except OSError as e:
            print(f"Error: {file} : {e.strerror}")

print("Cleanup complete.")