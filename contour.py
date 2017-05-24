"""Parsing code for contour files"""

import dicom
from dicom.errors import InvalidDicomError
import numpy as np
from PIL import Image, ImageDraw
import skimage
import os
import cv

#project imports
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

def poly_to_mask_alt2(vertexlist, width, height):
    """Convert polygon to mask

    :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
     in units of pixels
    :param width: scalar image width
    :param height: scalar image height
    :return: Boolean mask of shape (height, width)
    """

    img = Image.new('L', (width, height), color=0)   # The Zero is to Specify Background Color
    draw = ImageDraw.Draw(img)

    for vertex in range(len(vertexlist)):
        startpoint = vertexlist[vertex]
        try: endpoint = vertexlist[vertex+1]
        except IndexError: endpoint = vertexlist[0] 
        # The exception means We have reached the end and need to complete the polygon
        draw.line((startpoint[0], startpoint[1], endpoint[0], endpoint[1]), fill=1)

    mask = np.array(img).astype(bool)
    print mask.shape
    return mask


def poly_to_mask(vertexlist, width, height):
    """Convert polygon to mask

    :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
     in units of pixels
    :param width: scalar image width
    :param height: scalar image height
    :return: Boolean mask of shape (height, width)
    """
    vertex_row_coords, vertex_col_coords = zip(*vertexlist)
    shape = (width, height)
    fill_row_coords, fill_col_coords = skimage.draw.polygon(vertex_col_coords, vertex_row_coords, shape)
    mask = np.zeros(shape, dtype=np.bool)
    mask[fill_row_coords, fill_col_coords] = True
    return mask



def poly_to_mask_old(polygon, width, height):
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
    """Check all available i-contours

    :return: a list of paths to all the i-contours
    """
    icountours = []
    pid2oid = app.read_pid2oid(pathfinder.LINK_PATH)
    for key,value in pid2oid.iteritems():
        path = pathfinder.CONTOURS_PATH+'/'+value+'/i-contours'
        for filename in os.listdir(path):
            icountours.append(path + '/' + filename)
    return icountours

def get_list_available_ocontours():
    """Check all available o-contours

    :return: a list of paths to all the o-contours
    """
    ocountours = []
    pid2oid = app.read_pid2oid(pathfinder.LINK_PATH)
    for key,value in pid2oid.iteritems():
        path = pathfinder.CONTOURS_PATH+'/'+value+'/o-contours'
        for filename in os.listdir(path):
            ocountours.append(path + '/' + filename)
    return ocountours


def get_icontour_path(ocountour_path):
    folders = ocountour_path.split('/')
    oc_filename = folders[-1]
    ic_filename = oc_filename.replace('ocontour','icontour')
    main_dir = '/'.join(folders[:-2])
    icontour_path = main_dir + '/i-contours/'+ic_filename
    return icontour_path

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
















