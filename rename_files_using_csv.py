import pandas as pd
import shutil

df = pd.read_csv(r"C:\Users\shubh\Downloads\V_blocks.csv")

for index, row in

    file_name = row["ID"]

    # Source path
    source = f"E:/Saptarshi_work/KERALA_DETECTED_FARM_BOUNDARY_CORRECTIONS/Kerala_Farm_Boundary_Block_Extent_updated/pranay_files/{file_name}.tif"

    # Destination path
    destination = f"E:/Saptarshi_work/KERALA_DETECTED_FARM_BOUNDARY_CORRECTIONS/Kerala_Farm_Boundary_Block_Extent_updated/pranay_files/Vayanad_{file_name}.tif"

    # Copy the content of
    # source to destination

    try:
        shutil.copy(source, destination)
        print("File copied successfully.")

    # If source and destination are same
    except shutil.SameFileError:
        print("Source and destination represents the same file.")

    # If there is any permission issue
    except PermissionError:
        print("Permission denied.")

    # For other errors
    except:
        print("Error occurred while copying file.")
