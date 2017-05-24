"""Source code for some tests"""
import numpy as np
import scipy.ndimage


#project imports
import app
import contour
import utils_plots
import scan
import pathfinder


"""
I generated plots with the borders on the slice of the scan.
In this way we can easily do a visual check if the mask correctly fits on the slice of the scan
"""
def generate_border_plots(lst_contours, pixel_spacing_normalization=False):
    for idx, icp in enumerate(lst_contours):
        did = contour.get_dicom_id(icp)
        sid = contour.get_slice_id(icp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        c_lst = contour.parse_contour_file(icp)
        
        outfile = 'plots/'+contour.get_contour_id(icp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting mask to file', outfile
        if pixel_spacing_normalization:
            assert pixel_spacing[0]==pixel_spacing[1]
            slice = scipy.ndimage.zoom(slice, pixel_spacing[0], order=0)

        mask = contour.poly_to_mask(c_lst,slice.shape[0],slice.shape[1])
        utils_plots.plot_border_on_slice(slice, mask, outfile, figsize=(20, 20))#, x_bs=[75,175], y_bs=[75,175])


def generate_ocontours_icontours_border_plots(lst_ocontours, pixel_spacing_normalization=False):
    for idx, ocp in enumerate(lst_ocontours):
        icp = contour.get_icontour_path(ocp)
        did = contour.get_dicom_id(ocp)
        sid = contour.get_slice_id(ocp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        oc_lst = contour.parse_contour_file(ocp)
        ic_lst = contour.parse_contour_file(icp)
        
        outfile = 'plots/'+contour.get_contour_id(ocp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting mask to file', outfile
        if pixel_spacing_normalization:
            assert pixel_spacing[0]==pixel_spacing[1]
            slice = scipy.ndimage.zoom(slice, pixel_spacing[0], order=0)

        masko = contour.poly_to_mask(oc_lst,slice.shape[0],slice.shape[1])
        maski = contour.poly_to_mask(ic_lst,slice.shape[0],slice.shape[1])
        utils_plots.plot_borders_on_slice(slice, masko, maski, outfile, figsize=(20, 20))#, x_bs=[75,175], y_bs=[75,175])

def generate_masked_scan_plots(lst_ocontours):
    for idx, ocp in enumerate(lst_ocontours):
        did = contour.get_dicom_id(ocp)
        sid = contour.get_slice_id(ocp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        oc_lst = contour.parse_contour_file(ocp)
        
        outfile = 'plots/masked_scan_'+contour.get_contour_id(ocp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting masked slice to file', outfile

        mask = contour.poly_to_mask(oc_lst,slice.shape[0],slice.shape[1])
        masked_slice = mask*slice
        utils_plots.plot_slice(masked_slice, outfile, figsize=(20, 20), x_bs=[75,175], y_bs=[75,175])

def generate_histograms_masked_scan(lst_ocontours):
    for idx, ocp in enumerate(lst_ocontours):
        did = contour.get_dicom_id(ocp)
        sid = contour.get_slice_id(ocp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        oc_lst = contour.parse_contour_file(ocp)
        
        outfile = 'plots/hist_masked_sc_'+contour.get_contour_id(ocp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting masked slice to file', outfile

        mask = contour.poly_to_mask(oc_lst,slice.shape[0],slice.shape[1])
        masked_slice = mask*slice 
        print np.amin(masked_slice), np.amax(masked_slice)
        bins = np.arange(0,550,10) 
        hist,bins = np.histogram(masked_slice, bins=bins) 
        print hist
        th_mslice = masked_slice > 150
        utils_plots.plot_slice_hist(masked_slice, th_mslice, bins[1:], outfile, figsize=(10, 5), x_bs=[75,175], y_bs=[75,175])



def generate_scan_plots_from_contour_lst(lst_contours):
    for idx, cp in enumerate(lst_contours):
        did = contour.get_dicom_id(cp)
        sid = contour.get_slice_id(cp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        oc_lst = contour.parse_contour_file(cp)
        
        outfile = 'plots/scan_'+contour.get_contour_id(cp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting slice to file', outfile

        utils_plots.plot_slice(slice, outfile, figsize=(20, 20), x_bs=[75,175], y_bs=[75,175])


def generate_polygon_mask_plots():
    for idx, icp in enumerate(contour.get_list_available_icontours()):
        did = contour.get_dicom_id(icp)
        sid = contour.get_slice_id(icp)
        c_lst = contour.parse_contour_file(icp)
        mask = contour.poly_to_mask(c_lst,256,256)
        outfile = 'plots/bp_oc_ic_'+contour.get_contour_id(icp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print 'plotting polygones and masks to file', outfile
        utils_plots.plot_polygone_on_mask(c_lst, mask, outfile)


def generate_polygon_mask_plot(icp):
    did = contour.get_dicom_id(icp)
    sid = contour.get_slice_id(icp)
    c_lst = contour.parse_contour_file(icp)
    mask = contour.poly_to_mask(c_lst,256,256)
    outfile = 'plots/pm_'+contour.get_contour_id(icp)+'_' \
                      +did+'_' \
                      +str(sid)+'.jpg'
    print 'plotting polygones and masks to file', outfile
    utils_plots.plot_polygone_on_mask(c_lst, mask, outfile, resolution=100)

if __name__ == "__main__":
    #generating plot at high resolution for a problem case
    #generate_polygon_mask_plot(pathfinder.CONTOURS_PATH+'/'+'SC-HF-I-2/i-contours/IM-0001-0127-icontour-manual.txt')
    #generate_polygon_mask_plot(pathfinder.CONTOURS_PATH+'/'+'SC-HF-I-2/i-contours/IM-0001-0187-icontour-manual.txt')
    #generate_polygon_mask_plot(pathfinder.CONTOURS_PATH+'/'+'SC-HF-I-4/o-contours/IM-0001-0080-ocontour-manual.txt')
    #generate_border_plots(contour.get_list_available_icontours())

    # all_ocontours = contour.get_list_available_icontours()
    # selection = [path for path in all_ocontours if 'SC-HF-I-3' in path]
    # generate_border_plots(selection)

    all_ocontours = contour.get_list_available_ocontours()
    #selection = [path for path in all_ocontours if 'SC-HF-I-3' in path]
    #generate_ocontours_icontours_border_plots(all_ocontours)
    generate_histograms_masked_scan(all_ocontours)
