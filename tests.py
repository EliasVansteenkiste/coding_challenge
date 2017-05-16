
#project imports
import app
import contour
import utils_plots

def generate_border_plots():
    for idx, icp in enumerate(contour.get_list_available_icontours()):
        if idx == 1000:
            break
        slice, pixel_spacing = app.read_dicom_slice(contour.get_dicom_id(icp), contour.get_slice_id(icp))
        contour_lst = contour.parse_contour_file(icp)
        mask = contour.poly_to_mask(contour_lst,slice.shape[0],slice.shape[1])
        outfile = 'plots/'+contour.get_contour_id(icp)+'_' \
                          +contour.get_dicom_id(icp)+'_' \
                          +str(contour.get_slice_id(icp))+'.jpg'
        print pixel_spacing, outfile
        utils_plots.plot_border_on_slice(slice, mask, outfile)


if __name__ == "__main__":
    generate_border_plots()