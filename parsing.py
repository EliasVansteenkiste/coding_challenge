"""Parsing code for DICOMS and contour files"""

import dicom
from dicom.errors import InvalidDicomError
import numpy as np
from PIL import Image, ImageDraw
import os

import app
import pathfinder
import utils_plots


def parse_contour_file(filename):
    """Parse the given contour filename

    :param filename: filepath to the contourfile to parse
    :return: list of tuples holding x, y coordinates of the contour
    """

    coords_lst = []

    with open(filename, 'r') as infile:
        for line in infile:
            coords = line.strip().split()

            x_coord = float(coords[0])
            y_coord = float(coords[1])
            coords_lst.append((x_coord, y_coord))

    return coords_lst


def poly_to_mask(polygon, width, height):
    """Convert polygon to mask

    :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
     in units of pixels
    :param width: scalar image width
    :param height: scalar image height
    :return: Boolean mask of shape (height, width)
    """

    # http://stackoverflow.com/a/3732128/1410871
    img = Image.new(mode='L', size=(width, height), color=0)
    ImageDraw.Draw(img).polygon(xy=polygon, outline=0, fill=1)
    mask = np.array(img).astype(bool)
    return mask

def get_list_available_icontours():
    icountours = []
    pid2oid = app.read_pid2oid(pathfinder.LINK_PATH)
    for key,value in pid2oid.iteritems():
        path = pathfinder.CONTOURS_PATH+'/'+value+'/i-contours'
        for filename in os.listdir(path):
            icountours.append(path + '/' + filename)
    return icountours

def get_slice_id(icontour_path):
    filename = icontour_path.split('/')[-1]
    slice_id = int(filename.split('-')[2])
    return slice_id

def get_contour_id(icontour_path):
    contour_id = icontour_path.split('/')[-3]
    return contour_id

def get_dicom_id(icontour_path, oid2pid = app.read_oid2pid(pathfinder.LINK_PATH)):
    contour_id = icontour_path.split('/')[-3]
    dicom_id = oid2pid[contour_id]
    return dicom_id

def generate_border_plots():
    for idx, icp in enumerate(get_list_available_icontours()):
        if idx == 1000:
            break
        slice, pixel_spacing = app.read_dicom_slice(get_dicom_id(icp), get_slice_id(icp))
        contour_lst = parse_contour_file(icp)
        mask = poly_to_mask(contour_lst,slice.shape[0],slice.shape[1])
        outfile = 'plots/'+get_contour_id(icp)+'_'+get_dicom_id(icp)+'_'+str(get_slice_id(icp))+'.jpg'
        print pixel_spacing, outfile
        utils_plots.plot_border_on_slice(slice, mask, outfile)


if __name__ == "__main__":
    generate_border_plots()





