# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os, sys, time
import argparse
import yaml


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
        reference_list = cfg['reference_list']
        target_raster = cfg['target_raster']
        result_raster = cfg['result_raster']
        model_folder = cfg['model_folder']

    print(f'### REF {len(reference_list)} ==>> {target_raster}')
    return config_name, reference_list, target_raster, result_raster, model_folder


def main():
    print("##################################################################")
    print("### Raster repair using reference images #########################")
    print("##################################################################")


if __name__ == '__main__':
    main()
