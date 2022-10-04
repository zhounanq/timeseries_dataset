# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys, time
import argparse
import yaml

from tsraster_dataset_split_disk import TSRasterDatasetSplitDisk


def parse_args():
    parser = argparse.ArgumentParser(description='Parcel-based time-series dataset for deep learning...')
    parser.add_argument('--config_path', required=False, type=str,
                        default="./config/conf.yaml",
                        help='configure file for main process in YAML format')
    opts = parser.parse_args()
    return opts


def configure_info(yaml_path):

    with open(yaml_path, 'r') as f:
        cfg = yaml.safe_load(f)
        print(cfg)
        config_name = cfg['config_name']
        label_path = cfg['label_path']
        raster_list = cfg['raster_list']
        result_folder = cfg['result_folder']

        patch_size = int(cfg['patch_size'])
        min_pixel_percent = float(cfg['min_pixel_percent'])

    return config_name, label_path, raster_list, result_folder, patch_size, min_pixel_percent


def main():
    print("##################################################################")
    print("### Raster repair using reference images #########################")
    print("##################################################################")

    #######################################################
    # cmd line
    opts = parse_args()
    yaml_path = opts.config_path
    yaml_path = r'E:\develop_project\github-self\timeseries_dataset\config\dijon.yaml'

    config_name, label_path, raster_list, result_folder, patch_size, min_pixel_percent = configure_info(yaml_path)

    #######################################################
    # do
    tdsd = TSRasterDatasetSplitDisk(label_path, raster_list, result_folder, patch_size, min_pixel_percent)
    tdsd.prepare_data()
    tdsd.generate()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
