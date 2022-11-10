# -*- coding: utf-8 -*-

"""
Functions for time-series dataset

Author: Zhou Ya'nan
Date: 2021-09-16
"""
import os
import numpy as np
import warnings
from tqdm import tqdm
from osgeo import gdal

from raster_util import read_label_data, write_patch_sample
from raster_util import write_numpy_array, load_numpy_array

warnings.filterwarnings('ignore')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
os.environ['PROJ_LIB'] = r'D:\develop-envi\anaconda3\envs\py38\Lib\site-packages\pyproj\proj_dir\share\proj'
gdal.UseExceptions()


class RasterGridLayerStack(object):
    """
    栅格切片堆叠。
    在栅格数据集合切片程序中，由于内存限制而不能一次性对所有栅格集合切片，考虑将其分为多个子集合分别切片，进而合并多个切片。
    """
    def __init__(self, raster_folder_list, result_folder, patch_size=32):

        self.raster_folder_list = raster_folder_list
        self.result_folder = result_folder
        self.patch_size = patch_size

        self.grid_code_list = []

    def list_folder_grid_codes(self, filter_ext='.npy'):
        """
        根据第一个栅格切片集合，生成切片编码。
        :param filter_ext:
        :return:
        """
        folder = self.raster_folder_list[0]

        # fast version
        item_list = os.listdir(folder)
        for path in item_list:
            self.grid_code_list.append(path[:-4])
        self.grid_code_list.sort()

        # item_list = os.listdir(folder)
        # for path in item_list:
        #     abs_path = os.path.join(folder, path)
        #     name, ext = os.path.splitext(path)
        #     if os.path.isfile(abs_path) and (ext == filter_ext):
        #         self.grid_code_list.append(name)
        # self.grid_code_list.sort()

        return self.grid_code_list

    @staticmethod
    def _warp_raster_grid_data(grid_array, target_size):
        """
        对要堆叠的数据进行包装处理，比如数据类型、空间插值等。
        :param grid_array:
        :param target_size:
        :return:
        """
        grid_row, grid_col = grid_array.shape[1], grid_array.shape[2]
        assert(grid_row == grid_col)
        assert(target_size % grid_row == 0)

        if grid_row != target_size:
            factor = int(target_size / grid_row)
            grid_array = grid_array.repeat(factor, axis=-1).repeat(factor, axis=-2)

        return grid_array.astype(np.float32)

    def layerstack_raster_data(self):
        """
        切片堆叠。
        :return:
        """
        print('### Layer-stacking grid samples...')

        first_folder = os.path.basename(self.raster_folder_list[0])
        combine_folder = os.path.join(self.result_folder, first_folder)
        if not os.path.exists(combine_folder):
            os.makedirs(combine_folder)

        # combine grid data
        num_grid = len(self.grid_code_list)
        for gg, code in tqdm(enumerate(self.grid_code_list)):
            print(f'Grid {code}')

            # target folder
            if num_grid > 10000:
                sub = gg // 10000
                write_folder = os.path.join(combine_folder, '{:0>2d}'.format(sub))
                if gg % 10000 == 0 and not os.path.exists(write_folder):
                    os.makedirs(write_folder)
            else:
                write_folder = combine_folder

            # load raster grid data
            raster_grid_data_list = []
            for folder in self.raster_folder_list:
                raster_grid_path = os.path.join(folder, code + '.npy')
                raster_grid_data = load_numpy_array(raster_grid_path)
                raster_grid_data = self._warp_raster_grid_data(raster_grid_data, self.patch_size)
                raster_grid_data_list.append(raster_grid_data)
            all_raster_grid_data = np.concatenate(raster_grid_data_list, axis=0)

            # save to disk
            write_path = os.path.join(write_folder, code)
            write_numpy_array(all_raster_grid_data, write_path)
        # for

        print('### Combining grid samples complete!')
        return combine_folder


def main():
    print("##################################################################")
    print("###                                      #########################")
    print("##################################################################")

    #######################################################
    # cmd line
    patch_size = 32
    result_folder = r'K:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\01_48'
    raster_folder_list = [
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\01_06\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\07_12\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\13_18\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\19_24\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\25_30\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\31_36\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\37_42\08',
        r'k:\FF\application_dataset\2020-france-agri-grid\s2_l2a_tif_masked\grid_20m_10m_32\43_48\08'
    ]

    #######################################################
    # do
    rgls = RasterGridLayerStack(raster_folder_list, result_folder, patch_size)
    rgls.list_folder_grid_codes()
    rgls.layerstack_raster_data()

    #######################################################
    # close

    print('### Task complete !')


if __name__ == '__main__':
    main()
