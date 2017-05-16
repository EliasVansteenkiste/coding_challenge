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
    :param link_path: str, path to link CSV file containing patient ids and original ids
    :return: dict with patient ids as keys and the values are the original ids
    """
    pid2oid = {}

    with open(link_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            pid2oid[row['patient_id']] = row['original_id']

    return pid2oid

def read_oid2pid(link_path):
    """
    :param link_path: str, path to link CSV file containing patient ids and original ids
    :return: dict with original ids as keys and the values are the patient ids
    """
    oid2pid = {}

    with open(link_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            oid2pid[row['original_id']] = row['patient_id']

    return oid2pid

def parse_dicom_file(filename):


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
    """Parse the given DICOM filename

    :param path: filepath to the DICOM file to parse
    :return dcm_image: DICOM image data
    :return metadata: dictionary with metadata read from the dicom file
    """
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



def read_dicom_slice(dicom_id, slice_id):
    slice_path = pathfinder.DICOMS_PATH + '/' + dicom_id + '/' + str(slice_id) + '.dcm'
    data, metadata = parse_dicom_file(slice_path)
    pixel_spacing = metadata['PixelSpacing']
    return data, pixel_spacing



def read_dicom_scan(patient_data_path):
    sid2data, sid2metadata = get_patient_data(patient_data_path)
    sid2position = {}
    sid2idx = {}
    time_series = []
    positions = []
    pixel_spacings = []
    max_key = max([int(i) for i in list(sid2data.keys())])
    start_sid_range = np.arange(1, max_key+1, 20)

    for idx, start_sid in enumerate(start_sid_range):
        slice_positions = set()
        slice_shapes = set()
        slice_pixel_spacings = set()
        scans_fixed_loc = []
        for i in range(20): #20 timesteps
            sid = start_sid + i
            sid = unicode(str(sid), "utf-8")
            sid2idx[sid] = (i,idx)
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

    return whole_scan, sid2idx, (z_pixel_spacing[0], xy_pixelspacing[0], xy_pixelspacing[1])


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



def get_patient_data_paths(data_dir):
    pids = sorted(os.listdir(data_dir))
    return [data_dir + '/' + p for p in pids]

def read_patient_annotations_luna(pid, directory):
    return pickle.load(open(os.path.join(directory,pid+'.pkl'),"rb"))




def _test_read_dicom_scan():
    pid2oid = read_pid2oid(pathfinder.LINK_PATH)
    for key in pid2oid:
        img, sid2idx, pixel_spacings = read_dicom_scan(pathfinder.DICOMS_PATH+'/'+key)
        print key, img.shape, pixel_spacings

    #TODO there are different pixel spacings so we will have to interpolate






if __name__ == "__main__":
    _test_read_dicom_scan()


