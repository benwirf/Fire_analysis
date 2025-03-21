import os

property_lyr = iface.activeLayer()

all_fires_lyr = QgsVectorLayer('Polygon?crs=epsg:4283', 'all_fires', 'memory')
new_flds = [QgsField('ID', QVariant.Int), QgsField('YEAR', QVariant.Int), QgsField('MONTH', QVariant.Int)]
all_fires_lyr.dataProvider().addAttributes(new_flds)
all_fires_lyr.updateFields()
QgsProject.instance().addMapLayer(all_fires_lyr)

xform = QgsCoordinateTransform(property_lyr.crs(), QgsCoordinateReferenceSystem('epsg:4283'), QgsProject.instance())

search_rect = xform.transform(property_lyr.extent()) # Rectangle transformed to epsg:4283 (GDA94)

firescar_folder = 'Fire_Scars_Archive\\geopackages'

all_fires= []

fid = 1

for file in os.scandir(firescar_folder):
    if file.name.split('.')[-1] == 'gpkg':
        file_name = file.path.split('\\')[-1].split('.')[0]
#        print(file_name)
        # file_name strings are like: fs19_mths_gda (full years) and fs2022shp (current year to date)
        firescar_lyr = QgsVectorLayer(file.path, file_name, 'ogr')
        if firescar_lyr.isValid():
            # Deal with (exclude from spatial index) sliver polygon (artifact from raster?) around edge of fire layer extent
            firescar_valid_features = [f for f in firescar_lyr.getFeatures() if f.geometry().boundingBox().area() < 500]
            idx = QgsSpatialIndex()
            idx.addFeatures(firescar_valid_features)
            for id in idx.intersects(search_rect):
#                all_fires.append(id)
                ft1 = [f for f in firescar_valid_features if f.id() == id][0]
                ft2 = QgsFeature()
                ft2.setGeometry(ft1.geometry())
                if '_' in file_name: # Full years e.g. fs19_mths_gda
                    last_digits = file_name.split('_')[0].strip('fs')
                else: # Current year to date e.g. fs2022shp
                    last_digits = file_name[4:6] # returns characters 5 & 6
                yr = int(f'20{last_digits}') # e.g. 2019 etc
                ft2.setAttributes([fid, yr, ft1['Month']])
                all_fires_lyr.dataProvider().addFeatures([ft2])
                fid+=1
        firescar_lyr = None

#print(all_fires)
QgsProject.instance().addMapLayer(all_fires_lyr)
