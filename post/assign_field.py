# -*- coding: utf-8 -*-

"""
***

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys
import numpy as np
import pandas as pd

try:
    from osgeo import gdal, ogr, osr
except ImportError:
    import gdal, ogr, osr

# Enable GDAL/OGR exceptions
gdal.UseExceptions()
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")


def create_field(shp_layer, field_name, field_type):

    # print info
    layer_definition = shp_layer.GetLayerDefn()
    # for i in range(layer_definition.GetFieldCount()):
    #     name = layer_definition.GetFieldDefn(i).GetName()
    #     type_code = layer_definition.GetFieldDefn(i).GetType()
    #     type = layer_definition.GetFieldDefn(i).GetFieldTypeName(type_code)
    #     width = layer_definition.GetFieldDefn(i).GetWidth()
    #     precision = layer_definition.GetFieldDefn(i).GetPrecision()

    # if exits, delete it first.
    shp_layer.DeleteField(layer_definition.GetFieldIndex(field_name))
    # ds.ExecuteSQL("ALTER TABLE my_shp DROP COLUMN my_field")

    # Add a new field
    new_field = ogr.FieldDefn(field_name, field_type=field_type)
    shp_layer.CreateField(new_field)

    return shp_layer


def assign_field(shp_path, csv_path, new_field, join_field='fid'):

    # 1. load shpfile
    shp_dataset = ogr.Open(shp_path, gdal.OF_VECTOR | gdal.OF_UPDATE)
    if shp_dataset is None:
        print(f"### ERROR: could not open {shp_path}")
        sys.exit(1)
    shp_layer = shp_dataset.GetLayer(0)

    # 2. create field
    shp_layer = create_field(shp_layer, new_field, field_type=ogr.OFTInteger)

    # 3. read attributes into dict
    csv_df = pd.read_csv(csv_path, sep=',', header=0)
    value_dict = csv_df.set_index([join_field])[new_field].to_dict()

    # 4. write attributes
    for feat in shp_layer:
        join_value = int(feat.GetField(join_field))
        feat_value = value_dict.get(join_value, None)
        if feat_value:
            feat.SetField(new_field, int(feat_value))
            shp_layer.SetFeature(feat)

    # 5. close
    shp_layer = None
    shp_dataset = None
    return shp_path


def main():
    print("##########################################################")
    print("###  #####################################################")
    print("##########################################################")

    shp_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\zhaosu_result\lstm_ts\zhaosu_parcel_lstm_ts.shp'
    csv_path = r'E:\develop_project\python\timseries_classification\datasets\CROP\zhaosu_result\lstm_ts\zhaosu_result_src_confusion.csv'
    new_field = 'PRED_CODE'
    join_field = 'ID_PARCEL'

    assign_field(shp_path, csv_path, new_field, join_field)

    print("### Complete! #############################################")


if __name__ == "__main__":
    main()
