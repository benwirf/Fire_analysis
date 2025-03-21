import zipfile
import os

folder_path = 'Fire_Scars_Archive'
save_path = 'Fire_Scars_Archive\\shapefiles'

for file in os.scandir(folder_path):
    if file.name.split('.')[-1] == 'zip':
        zip_path = os.path.join(folder_path, file.name)
        with zipfile.ZipFile(zip_path,"r") as zip_ref:
            zip_ref.extractall(save_path)
