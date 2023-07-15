###This script re-arranges firescars from calendar year to financial year
###It also clips the firescars to a study area, checks for and tries to repair
###any invalid geometries, collects the firescar geometries by month and_
###reprojects them from 4283 to 9473

import os

financial_years = ['2000-2001',
                    '2001-2002',
                    '2002-2003',
                    '2003-2004',
                    '2004-2005',
                    '2005-2006',
                    '2006-2007',
                    '2007-2008',
                    '2008-2009',
                    '2009-2010',
                    '2010-2011',
                    '2011-2012',
                    '2012-2013',
                    '2013-2014',
                    '2014-2015',
                    '2015-2016',
                    '2016-2017',
                    '2017-2018',
                    '2018-2019',
                    '2019-2020',
                    '2020-2021',
                    '2021-2022',
                    '2022-2023',]
                
'EPSG:9473'

def transform_geom(g):
    new_geom = QgsGeometry().fromWkt(g.asWkt())
    src_crs = QgsCoordinateReferenceSystem('EPSG:4283')
    tgt_crs = QgsCoordinateReferenceSystem('EPSG:9473')
    xform = QgsCoordinateTransform(src_crs, tgt_crs, QgsProject.instance())
    new_geom.transform(xform)
    return new_geom

def createFsLayerByFy(fy):
    fy_layers = []
    src_folder = r'/home/ben/DITT/Central_Australia_Fire_Mapping/Fire_Scars_Archive/geopackages'
        
    for file in os.scandir(src_folder):
        if file.name.split('.')[1] == 'gpkg':
            # print(file.name)
            if file.name[4:6] == '_m':
                # This is a full year fs layer
                yy = file.name[2:4]
                if yy == fy.split('-')[0][2:4]:
                    # We want this to be the first item in the list
                    fy_layers.insert(0, file.name)
                elif yy == fy.split('-')[1][2:4]:
                    # We want this to be the last item in list
                    fy_layers.append(file.name)
            else:
                # This is the most recent, to-date part year fs layer
                yy = file.name[4:6]
                if yy == fy.split('-')[0][2:4] or yy == fy.split('-')[1][2:4]:
                    # This should always be the last item in list
                    fy_layers.append(file.name)
    # print(fy_layers)
    feat_list = []
    id = 1
    
    study_extent_layer_path = r'/home/ben/DITT/Central_Australia_Fire_Mapping/extent_wgs84.gpkg|layername=extent_gda_94'
    study_extent_layer = QgsVectorLayer(study_extent_layer_path, 'study_extent', 'ogr')
    study_extent_geom = [ft for ft in study_extent_layer.getFeatures()][0].geometry()# There is only one feature in this layer    
    
    calendar_year_1 = fy_layers[0]
    calendar_year_1_fs_layer = QgsVectorLayer(os.path.join(src_folder, calendar_year_1), 'fs_layer', 'ogr')
    cy1_sp_idx = QgsSpatialIndex(calendar_year_1_fs_layer.getFeatures())
    cy1_candidate_feat_ids = cy1_sp_idx.intersects(study_extent_geom.boundingBox())
    months1 = [7, 8, 9, 10, 11, 12]
    for m in months1:
        month_fires1 = [ft for ft in calendar_year_1_fs_layer.getFeatures(QgsFeatureRequest(cy1_candidate_feat_ids)) if ft['month'] == m]
        if not month_fires1:
            continue
        month_fires1_geoms = []
        for ft in month_fires1:
            g1 = ft.geometry()
            # print(g1.isGeosValid())
            if not g1.isGeosValid():
                g1 = g1.makeValid()
            g1_in_study_area = g1.intersection(study_extent_geom)
            month_fires1_geoms.append(g1_in_study_area)
        month_fires1_geom = transform_geom(QgsGeometry.collectGeometry(month_fires1_geoms))
        feat = QgsFeature()
        feat.setGeometry(month_fires1_geom)
        feat.setAttributes([id, fy.split('-')[0], m])
        feat_list.append(feat)
        id+=1
        
    calendar_year_2 = fy_layers[1]
    calendar_year_2_fs_layer = QgsVectorLayer(os.path.join(src_folder, calendar_year_2), 'fs_layer', 'ogr')
    cy2_sp_idx = QgsSpatialIndex(calendar_year_2_fs_layer.getFeatures())
    cy2_candidate_feat_ids = cy2_sp_idx.intersects(study_extent_geom.boundingBox())
    months2 = [1, 2, 3, 4, 5, 6]
    for m in months2:
        month_fires2 = [ft for ft in calendar_year_2_fs_layer.getFeatures(QgsFeatureRequest(cy2_candidate_feat_ids)) if ft['month'] == m]
        if not month_fires2:
            continue
        month_fires2_geoms = []
        for ft in month_fires2:
            g2 = ft.geometry()
            if not g2.isGeosValid():
                g2 = g2.makeValid()
            g2_in_study_area = g2.intersection(study_extent_geom)
            month_fires2_geoms.append(g2_in_study_area)
        month_fires2_geom = transform_geom(QgsGeometry.collectGeometry(month_fires2_geoms))
        feat = QgsFeature()
        feat.setGeometry(month_fires2_geom)
        feat.setAttributes([id, fy.split('-')[1], m])
        feat_list.append(feat)
        id+=1
        
    output_folder = r'/home/ben/DITT/Central_Australia_Fire_Mapping/Sth_NT_Fire_Scars_by_FY'
    output_layer_name = f'Firescars_{fy}.gpkg'
    output_path = os.path.join(output_folder, output_layer_name)
    
    writer_options = QgsVectorFileWriter.SaveVectorOptions()
    writer_options.driverName = 'GPKG'
    writer_options.fileEncoding = 'utf-8'
    
    field_list = [QgsField('ID', QVariant.Int),
            QgsField('FIN_YR', QVariant.String),
            QgsField('MONTH', QVariant.Int)]
    
    fields = QgsFields()
    for fld in field_list:
        fields.append(fld)
    
    writer = QgsVectorFileWriter.create(output_path,
                                        fields,
                                        QgsWkbTypes.MultiPolygon,
                                        QgsCoordinateReferenceSystem('EPSG:9473'),
                                        QgsProject.instance().transformContext(),
                                        writer_options)
    
    ok = writer.addFeatures(feat_list)
    
    if not ok:
        print(f'Writer Error {writer.lastError()}!!!')
    
    del writer
            
            
# for fy in financial_years:
#     createFsLayerByFy(fy)

createFsLayerByFy('2000-2001')

print('Done')
            