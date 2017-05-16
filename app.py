import csv
import dicom
import SimpleITK as sitk
import numpy as np
import csv
import os
from collections import defaultdict
import cPickle as pickle

import utils
import pathfinder

def read_pid2oid(link_path):
    """
    :param link_path: str, path to link CSV file contining patient ids and original ids
    :return: dict with patient ids as keys and the values are the original ids
    """
    pid2oid = {}

    with open(link_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            pid2oid[row['patient_id']] = row['original_id']

    return pid2oid

def _test_read_pid2oid():
    print read_pid2oid(pathfinder.LINK_PATH)

def parse_dicom_file(filename):
    """Parse the given DICOM filename

    :param filename: filepath to the DICOM file to parse
    :return: dictionary with DICOM image data
    """

    try:
        dcm = dicom.read_file(filename)
        dcm_image = dcm.pixel_array

        try:
            intercept = dcm.RescaleIntercept
        except AttributeError:
            intercept = 0.0
        try:
            slope = dcm.RescaleSlope
        except AttributeError:
            slope = 0.0

        if intercept != 0.0 and slope != 0.0:
            dcm_image = dcm_image*slope + intercept
        dcm_dict = {'pixel_data' : dcm_image}
        return dcm_dict
    except InvalidDicomError:
        return None


def parse_dicom_file(path):
    try:
        d = dicom.read_file(path)
        metadata = {}
        for attr in dir(d):
            if attr[0].isupper() and attr != 'PixelData':
                try:
                    metadata[attr] = getattr(d, attr)
                except AttributeError:
                    pass

        metadata['InstanceNumber'] = int(metadata['InstanceNumber'])
        metadata['PixelSpacing'] = np.float32(metadata['PixelSpacing'])
        metadata['ImageOrientationPatient'] = np.float32(metadata['ImageOrientationPatient'])
        try:
            metadata['SliceLocation'] = np.float32(metadata['SliceLocation'])
        except:
            metadata['SliceLocation'] = None
        metadata['ImagePositionPatient'] = np.float32(metadata['ImagePositionPatient'])
        metadata['Rows'] = int(metadata['Rows'])
        metadata['Columns'] = int(metadata['Columns'])


        dcm_image = d.pixel_array
        try:
            intercept = d.RescaleIntercept
        except AttributeError:
            intercept = 0.0
        try:
            slope = d.RescaleSlope
        except AttributeError:
            slope = 0.0

        if intercept != 0.0 and slope != 0.0:
            dcm_image = dcm_image*slope + intercept

        return dcm_image, metadata

    except InvalidDicomError:
        return None


def extract_pid_dir(patient_data_path):
    return patient_data_path.split('/')[-1]


def extract_pid_filename(file_path, replace_str='.mhd'):
    return os.path.basename(file_path).replace(replace_str, '').replace('.pkl', '')


def get_patient_data(patient_data_path):
    slice_paths = os.listdir(patient_data_path)
    sid2data = {}
    sid2metadata = {}
    for s in slice_paths:
        slice_id = s.split('.')[0]
        data, metadata = parse_dicom_file(patient_data_path + '/' + s)
        sid2data[slice_id] = data
        sid2metadata[slice_id] = metadata
    return sid2data, sid2metadata



def read_dicom_scan(patient_data_path):
    sid2data, sid2metadata = get_patient_data(patient_data_path)
    sid2position = {}
    max_key = max([int(i) for i in list(sid2data.keys())])
    time_series = []
    positions = []
    pixel_spacings = []
    for start_sid in range(1, max_key+1, 20):
        slice_positions = set()
        slice_shapes = set()
        slice_pixel_spacings = set()
        scans_fixed_loc = []
        for i in range(20): #20 timesteps
            sid = start_sid + i
            sid = unicode(str(sid), "utf-8")
            slice_positions.add(get_slice_position(sid2metadata[sid]))
            slice_shapes.add(sid2data[sid].shape)
            slice_pixel_spacings.add(tuple(sid2metadata[sid]['PixelSpacing']))
            scans_fixed_loc.append(sid2data[sid])
        #check if all positions of one time series are the same
        assert len(slice_positions)==1, "slice positions need to be equal: %s" % slice_positions
        assert len(slice_shapes)==1, "slice shapes need to be equal: %s" % slice_shapes
        assert len(slice_pixel_spacings)==1, "Pixel spacing is different within one time series: %s" % slice_pixel_spacings
        positions.append(next(iter(slice_positions)))
        pixel_spacings.append(next(iter(slice_pixel_spacings)))
        time_series.append(np.stack(scans_fixed_loc))
    whole_scan = np.stack(time_series)
    # set time dimension on the 0-axis and z dimension on the 1-axis
    whole_scan = np.swapaxes(whole_scan,0,1) 

    print whole_scan.shape
    positions = np.array(positions)
    z_pixel_spacing = positions[1:]-positions[:-1]
    assert np.all((z_pixel_spacing - z_pixel_spacing[0]) < 0.01), 'z pixel spacings are not equal for the whole scan: %s' %z_pixel_spacing

    s_pixel_spacings = set(pixel_spacings)
    assert len(s_pixel_spacings) == 1, "There are different x,y pixel spacings in the scan: %s" % s_pixel_spacings
    xy_pixelspacing = next(iter(s_pixel_spacings))

    return whole_scan, (z_pixel_spacing[0], xy_pixelspacing[0], xy_pixelspacing[1])


def sort_slices_position(patient_data):
    return sorted(patient_data, key=lambda x: get_slice_position(x['metadata']))


def sort_sids_by_position(sid2metadata):
    return sorted(sid2metadata.keys(), key=lambda x: get_slice_position(sid2metadata[x]))


def get_slice_position(slice_metadata):
    """
    https://www.kaggle.com/rmchamberlain/data-science-bowl-2017/dicom-to-3d-numpy-arrays
    """
    orientation = tuple((o for o in slice_metadata['ImageOrientationPatient']))
    position = tuple((p for p in slice_metadata['ImagePositionPatient']))
    rowvec, colvec = orientation[:3], orientation[3:]
    normal_vector = np.cross(rowvec, colvec)
    slice_pos = np.dot(position, normal_vector)
    return slice_pos


def slice_location_finder(sid2metadata):
    """
    :param slicepath2metadata: dict with arbitrary keys, and metadata values
    :return:
    """

    sid2midpix = {}
    sid2position = {}

    for sid in sid2metadata:
        metadata = sid2metadata[sid]
        image_orientation = metadata["ImageOrientationPatient"]
        image_position = metadata["ImagePositionPatient"]
        pixel_spacing = metadata["PixelSpacing"]
        rows = metadata['Rows']
        columns = metadata['Columns']

        # calculate value of middle pixel
        F = np.array(image_orientation).reshape((2, 3))
        # reversed order, as per http://nipy.org/nibabel/dicom/dicom_orientation.html
        i, j = columns / 2.0, rows / 2.0
        im_pos = np.array([[i * pixel_spacing[0], j * pixel_spacing[1]]], dtype='float32')
        pos = np.array(image_position).reshape((1, 3))
        position = np.dot(im_pos, F) + pos
        sid2midpix[sid] = position[0, :]

    if len(sid2midpix) <= 1:
        for sp, midpix in sid2midpix.iteritems():
            sid2position[sp] = 0.
    else:
        # find the keys of the 2 points furthest away from each other
        max_dist = -1.0
        max_dist_keys = []
        for sp1, midpix1 in sid2midpix.iteritems():
            for sp2, midpix2 in sid2midpix.iteritems():
                if sp1 == sp2:
                    continue
                distance = np.sqrt(np.sum((midpix1 - midpix2) ** 2))
                if distance > max_dist:
                    max_dist_keys = [sp1, sp2]
                    max_dist = distance
        # project the others on the line between these 2 points
        # sort the keys, so the order is more or less the same as they were
        # max_dist_keys.sort(key=lambda x: int(re.search(r'/sax_(\d+)\.pkl$', x).group(1)))
        p_ref1 = sid2midpix[max_dist_keys[0]]
        p_ref2 = sid2midpix[max_dist_keys[1]]
        v1 = p_ref2 - p_ref1
        v1 /= np.linalg.norm(v1)

        for sp, midpix in sid2midpix.iteritems():
            v2 = midpix - p_ref1
            sid2position[sp] = np.inner(v1, v2)

    return sid2position


def get_patient_data_paths(data_dir):
    pids = sorted(os.listdir(data_dir))
    return [data_dir + '/' + p for p in pids]

def read_patient_annotations_luna(pid, directory):
    return pickle.load(open(os.path.join(directory,pid+'.pkl'),"rb"))




def _test_read_dicom_scan():
    pid2oid = read_pid2oid(pathfinder.LINK_PATH)
    for key in pid2oid:
        img, pixel_spacings = read_dicom_scan(pathfinder.DICOMS_PATH+'/'+key)
        print key, img.shape, pixel_spacings






if __name__ == "__main__":
    _test_read_dicom_scan()


