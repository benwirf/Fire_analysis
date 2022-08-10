import os

folder_path = 'C:\\Users\\qw2\\Desktop\\Fire_Scars_Archive\\shapefiles'
save_path = 'C:\\Users\\qw2\\Desktop\\Fire_Scars_Archive\\geopackages'

for file in os.scandir(folder_path):
    if file.name.split('.')[-1] == 'shp':
        in_path = os.path.join(folder_path, file.name)
        lyr_name = file.name.split('.')[0]
        out_path = os.path.join(save_path, f'{lyr_name}.gpkg')
#        print(in_path)
#        print(out_path)
#        print(f'Fixing {file.name}')
        params = {'INPUT':in_path,
                'OUTPUT':out_path}
        processing.run('native:fixgeometries', params)

print('Done')