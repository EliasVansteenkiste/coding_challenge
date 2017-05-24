"""Source code for plot functions used for visual checks"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
print plt.get_backend() 
import warnings
import numpy as np
import skimage.morphology 

warnings.simplefilter('ignore')

def plot_border_on_slice(slice, mask, outfile, figsize=(5, 5), x_bs=None, y_bs=None):
    """
    Plot the border of the mask on a plot of the slice
    the plot is not shown but saved to a file


    :param slice: slice array (2D)
    :param mask: mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """

    assert(slice.shape == mask.shape)

    f = plt.figure(figsize=figsize)
    f.add_subplot(1, 1, 1)

    if x_bs:
        slice = slice[x_bs[0]:x_bs[1]]
    if y_bs:
        slice = slice[:,y_bs[0]:y_bs[1]]

    print slice.shape
    plt.imshow(slice, cmap=plt.cm.bone)

    selem1 = skimage.morphology.disk(2)
    inner = skimage.morphology.binary_erosion(mask, selem1)
    border = np.logical_xor(inner, mask)

    if x_bs:
        border = border[x_bs[0]:x_bs[1]]
    if y_bs:
        border = border[:,y_bs[0]:y_bs[1]]

    print border.shape
    plt.imshow(border, cmap=plt.cm.viridis, alpha=.3)

    f.savefig(outfile, bbox_inches='tight')
    print outfile
    plt.close('all')

def plot_borders_on_slice(slice, mask1, mask2, outfile, figsize=(5, 5), x_bs=None, y_bs=None):
    """
    Plot the border of the masks on a plot of the slice
    the plot is not shown but saved to a file


    :param slice: slice array (2D)
    :param mask1: first mask array (2D), should have the same shape as slice
    :param mask1: second mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """

    assert slice.shape == mask1.shape
    assert slice.shape == mask2.shape

    f = plt.figure(figsize=figsize)
    f.add_subplot(1, 1, 1)

    if x_bs:
        slice = slice[x_bs[0]:x_bs[1]]
    if y_bs:
        slice = slice[:,y_bs[0]:y_bs[1]]

    print slice.shape
    plt.imshow(slice, cmap=plt.cm.bone)

    selem1 = skimage.morphology.disk(2)
    inner1 = skimage.morphology.binary_erosion(mask1, selem1)
    border1 = np.logical_xor(inner1, mask1)

    inner2 = skimage.morphology.binary_erosion(mask2, selem1)
    border2 = np.logical_xor(inner2, mask2)

    if x_bs:
        border1 = border1[x_bs[0]:x_bs[1]]
        border1 = border1[x_bs[0]:x_bs[1]]
    if y_bs:
        border2 = border2[:,y_bs[0]:y_bs[1]]
        border2 = border2[:,y_bs[0]:y_bs[1]]

    print border1.shape
    plt.imshow(border1, cmap=plt.cm.viridis, alpha=.3)
    plt.imshow(border2, cmap=plt.cm.magma, alpha=.3)

    f.savefig(outfile, bbox_inches='tight')
    print outfile
    plt.close('all')


def plot_polygone_on_mask(points, mask, outfile, resolution):
    """
    Plot the border of the mask on a plot of the slice and mask
    the plot is not shown but saved to a file


    :param points: a list of (x,y) points indicating the vertices of the polygone
    :param mask: mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """

    f = plt.figure(figsize=(resolution, resolution))
    f.add_subplot(1, 1, 1)
    plt.imshow(mask, cmap=plt.cm.bone)

    plt.scatter(*zip(*points), s=5)

    # selem1 = skimage.morphology.disk(2)
    # inner = skimage.morphology.binary_erosion(mask, selem1)
    # border = np.logical_xor(inner, mask)
    # plt.imshow(border, cmap=plt.cm.viridis, alpha=.3)

    f.savefig(outfile, bbox_inches='tight')
    plt.close('all')

def plot_slice_mask(slice, mask, outfile, border=True):
    """
    Plot the slice and mask next to each other

    the plot is not shown but saved to 


    :param slice: slice array (2D)
    :param mask: mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """
    f = plt.figure(figsize=(10, 5))
    f.add_subplot(1, 2, 1)
    plt.imshow(slice, cmap=plt.cm.bone)

    f.add_subplot(1, 2, 2)
    if border:
        selem1 = skimage.morphology.disk(2)
        inner = skimage.morphology.binary_erosion(mask, selem1)
        border = np.logical_xor(inner, mask)
        plt.imshow(border, cmap=plt.cm.gray)
    else:
        plt.imshow(mask, cmap=plt.cm.gray, interpolation=None)

    f.savefig(outfile, bbox_inches='tight')
    plt.close('all')

def plot_slice(slice, outfile, figsize=(10,10), x_bs=None, y_bs=None):
    """
    Plot the slice

    :param slice: plot of the slice
    :param resolution: the resolution of the plot figure
    :param outfile: filepath to which the plot will be saved to
    """

    if x_bs:
        slice = slice[x_bs[0]:x_bs[1]]
    if y_bs:
        slice = slice[:,y_bs[0]:y_bs[1]]

    f = plt.figure(figsize=figsize)
    f.add_subplot(1, 1, 1)
    plt.imshow(slice, cmap=plt.cm.bone)

    f.savefig(outfile, bbox_inches='tight')
    plt.close('all')

def plot_slice_hist(slice, th_slice, bins, outfile, treshold=150, figsize=(10, 5), x_bs=None, y_bs=None):
    """
    Plot the slice and mask next to each other

    the plot is not shown but saved to 


    :param slice: slice array (2D)

    :param bins: array with bin borders of the histogram 
    :param mask: mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """

    if x_bs:
        slice = slice[x_bs[0]:x_bs[1]]
        th_slice = th_slice[x_bs[0]:x_bs[1]]
    if y_bs:
        slice = slice[:,y_bs[0]:y_bs[1]]
        th_slice = th_slice[:,y_bs[0]:y_bs[1]]

    f = plt.figure(figsize=figsize)
    f.add_subplot(1, 3, 1)
    plt.imshow(slice, cmap=plt.cm.bone)

    f.add_subplot(1, 3, 2)
    hist0, bins0 = np.histogram(slice,bins=bins)
    print "hist0, bins0"
    print hist0, bins0
    max_occ = np.amax(hist0[1:])
    print max_occ
    n, bins1, patches = plt.hist(slice.flatten(), bins, facecolor='green', edgecolor='k', alpha=0.75)
    print "n, bins1, patches"
    print n, bins1, patches
    plt.plot((treshold, treshold), (0, max_occ), 'k-')

    f.add_subplot(1, 3, 3)
    plt.imshow(th_slice)


    f.savefig(outfile, bbox_inches='tight')
    plt.close('all')

