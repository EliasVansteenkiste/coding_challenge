"""Source code for data iterators"""
import numpy as np

#project imports
import pathfinder
import utils
import app
import contour

class DataGenerator(object):
    def __init__(self, batch_size, gt_paths, p_transform, data_prep_fun, mask_prep_fun, rng,
                 random, infinite, full_batch, **kwargs):


        self.gt_paths = gt_paths
        self.nsamples = len(gt_paths)
        self.batch_size = batch_size
        self.p_transform = p_transform
        self.data_prep_fun = data_prep_fun
        self.mask_prep_fun = mask_prep_fun
        self.rng = rng
        self.random = random
        self.infinite = infinite
        self.full_batch = full_batch

    def generate(self):
        while True:
            rand_idxs = np.arange(len(self.gt_paths))
            if self.random:
                self.rng.shuffle(rand_idxs)
            for pos in xrange(0, len(rand_idxs), self.batch_size):
                idxs_batch = rand_idxs[pos:pos + self.batch_size]
                nb = len(idxs_batch)

                
                # allocate batches
                x_batch = np.zeros((nb,) + self.p_transform['patch_size'], dtype='float32')
                y_batch = np.zeros((nb,) + self.p_transform['patch_size'], dtype='float32')

                batch_ids = []

                for i, idx in enumerate(idxs_batch):
                    gt_path = self.gt_paths[idx]

                    cid = contour.get_contour_id(gt_path)
                    did = contour.get_dicom_id(gt_path)
                    sid = str(contour.get_slice_id(gt_path))

                    sample_id = cid + '_' + did + '_' + sid
                    batch_ids.append(sample_id)

                    try:
                        x, pixel_spacing = app.read_dicom_slice(did, sid)
                    except Exception:
                        print 'cannot open dicom, dicom id: ', did, ', slice id:', sid

                    try:
                        contour_lst = contour.parse_contour_file(gt_path)
                    except Exception:
                        print 'cannot open gt ', gt_path

                    y = contour.poly_to_mask(contour_lst,x.shape[0],x.shape[1])

                    x_batch[i] = self.data_prep_fun(x)
                    y_batch[i] = self.mask_prep_fun(y)


                if self.full_batch:
                    if nb == self.batch_size:
                        yield x_batch, y_batch, batch_ids
                else:
                    yield x_batch, y_batch, batch_ids

            if not self.infinite:
                break

def _test_data_generator():
    #testing the data iterator 

    # p_transform can be used to pass various info to the data iterator
    p_transform = {'patch_size': (256, 256)} 
    rng = np.random.RandomState(42)

    def data_prep_fun(x):
        #here you can do normalization, a crop, ...
        return x

    def mask_prep_fun(y):
        #here you can change the ground truth mask, maybe some morphological operations or whatever helps training
        return y

    all_gts = contour.get_list_available_icontours()

    dg = DataGenerator( batch_size=8,
                        gt_paths = all_gts,
                        p_transform=p_transform,
                        data_prep_fun = data_prep_fun,
                        mask_prep_fun = mask_prep_fun,
                        rng=rng,
                        full_batch=False, random=True, infinite=False)

    for (x_chunk, y_chunk, id_train) in dg.generate():
        print x_chunk.shape, y_chunk.shape, id_train





if __name__ == "__main__":
    _test_data_generator()


