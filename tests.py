"""Source code for some tests"""

#project imports
import app
import contour
import utils_plots
import scan


"""
I generated plots with the borders on the slice of the scan.
In this way we can easily do a visual check if the mask correctly fits on the slice of the scan
"""
def generate_border_plots():
    for idx, icp in enumerate(contour.get_list_available_icontours()):
        # if idx == 1000:
        #     break
        did = contour.get_dicom_id(icp)
        sid = contour.get_slice_id(icp)
        slice, pixel_spacing = scan.read_dicom_slice(did, sid)
        c_lst = contour.parse_contour_file(icp)
        mask = contour.poly_to_mask(c_lst,slice.shape[0],slice.shape[1])
        outfile = 'plots/'+contour.get_contour_id(icp)+'_' \
                          +did+'_' \
                          +str(sid)+'.jpg'
        print pixel_spacing, 'plotting mask to file', outfile
        utils_plots.plot_border_on_slice(slice, mask, outfile)


if __name__ == "__main__":
    generate_border_plots()