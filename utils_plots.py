"""Source code for plot functions used for visual checks"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
print plt.get_backend() 
import warnings
import numpy as np
import skimage.morphology 

warnings.simplefilter('ignore')

def plot_border_on_slice(slice, mask, outfile):
    """
    Plot the border of the mask on a plot of the slice and mask
    the plot is not shown but saved to a file


    :param slice: slice array (2D)
    :param mask: mask array (2D), should have the same shape as slice
    :param outfile: filepath to which the plot will be saved to
    """

    assert(slice.shape == mask.shape)

    f = plt.figure(figsize=(5, 5))
    f.add_subplot(1, 1, 1)
    plt.imshow(slice, cmap=plt.cm.bone)

    selem1 = skimage.morphology.disk(2)
    inner = skimage.morphology.binary_erosion(mask, selem1)
    border = np.logical_xor(inner, mask)
    plt.imshow(border, cmap=plt.cm.viridis, alpha=.3)

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


    

