# General overview of the source files
The most important files are:
* *contour.py* contains functions to read in the ground truth contours and transform the contours to masks
* *scan.py* contains methods to read DICOM scans
* *data_iterator.py* contains the data generator class

supporting source files:
* *pathfinder.py* checks if all paths and files to the data exist
* *utils_plots.py* contains plot functions to do the visual checks
* *app.py* contains methods to read in link file and create dictionaries for both ways
* *utils.py* contains some convenience methods, this is copied from another project, some of the methods I don't use for this challenge


# Questions Part 1
### How did you verify that you are parsing the contours correctly?
I did a visual check on the masks and the contours.
The function plot_polygone_on_mask in tests.py, can be used to generate those plots.
After visual inspection, I saw that the binary masks that were generated with poly_to_mask function do not completely fit the polygons defined in the original contour files.
After reading the solution on stackoverflow, I saw the following comment:
http://stackoverflow.com/questions/3654289/scipy-create-2d-polygon-mask#comment59125132_3732128
The solution used in the original poly_to_mask function only works with integer coordinate (i.e. grid coordinates)



<img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_127_old.jpg?raw=true" title="Old mask SC-HF-I-2 0127" width="400"><img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_127_new.jpg?raw=true" title="New mask SC-HF-I-2 0127" width="400">

<img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_187_old.jpg?raw=true" title="Old mask SC-HF-I-2 0187" width="400"> <img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_187_new.jpg?raw=true" title="New mask SC-HF-I-2 0187" width="400">


### What changes did you make to the code, if any, in order to integrate it into our production code base? 
I used the skimage.draw.polygon function, which behaves much nicer with floating point vertices as can be seen in the few examples that I included in the problem_cases folder.



# Questions part 2
### Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?
I first read the whole exercise, so I knew I had to write a data iterator, so I did not change the scan and contour functions after part 1.
However, I wrote a function in scan.py to read in the whole scan of the image to see if there are different pixel spacings. 

### How do you/did you verify that the pipeline was working correctly?
I tested the data iterator, by letting it run through all the samples and I verified the ids and the shapes.
I also did a visual check on the masks and the contours if they fit together.

### Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?
I would have to profile the pipeline for where it consumes most of the runtime, but that only matters if reading the data is a bottleneck. It could as well be the computations on the GPU.

I would interpolate each scan to the same pixel spacing. I made some provisions to be able to add this easily in the data_prep_fun. Now I only have five patient scans and four of them have the same x,y pixel spacings, so the straightforward thing to do is to transform the one special case to most occuring pixel spacing. However, typically there are going to be more diverse pixel spacings and it could be easier to just transform everything to 1mmx1mm. It depends on the distribution in the whole dataset, so maybe in phase 2, I will know what to do.

If I had more time, I would also add more safeguards and assertions.
