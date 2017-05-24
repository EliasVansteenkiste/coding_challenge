# General overview of the source files
The most important files are:
* *contour.py* contains functions to read in the ground truth contours and transform the contours to masks
* *scan.py* contains methods to read DICOM scans
* *data_iterator.py* contains the data generator class
* *tests.py* contains methods to plot different views of the contours and images for visual inspection

supporting source files:
* *pathfinder.py* checks if all paths and files to the data exist
* *utils_plots.py* contains plot functions to do the visual checks
* *app.py* contains methods to read in link file and create dictionaries for both ways
* *utils.py* contains some convenience methods, this is copied from another project, some of the methods I don't use for this challenge

In *SETTINGS.json* you can define the paths to data.

# Questions Phase 1
## Part 1
### How did you verify that you are parsing the contours correctly?
I did a visual check on the masks and the contours.
The function plot_polygone_on_mask in *tests.py*, can be used to generate those plots.
After visual inspection, I saw that the binary masks that were generated with **poly_to_mask** function do not completely fit the polygons defined in the original contour files.
After reading the solution on stackoverflow, I saw the following comment:
http://stackoverflow.com/questions/3654289/scipy-create-2d-polygon-mask#comment59125132_3732128
The solution used in the original poly_to_mask function only works with integer coordinate (i.e. grid coordinates)



<img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_127_old.jpg?raw=true" title="Old mask SC-HF-I-2 0127" width="400"><img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_127_new.jpg?raw=true" title="New mask SC-HF-I-2 0127" width="400">

<img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_187_old.jpg?raw=true" title="Old mask SC-HF-I-2 0187" width="400"> <img src="problem_cases/closeup_pm_SC-HF-I-2_SCD0000201_187_new.jpg?raw=true" title="New mask SC-HF-I-2 0187" width="400">


### What changes did you make to the code, if any, in order to integrate it into our production code base? 
I used the **skimage.draw.polygon** function, which behaves much nicer with floating point vertices as can be seen in the few examples that I included in the problem_cases folder.


## Part 2
### Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?
I first read the whole exercise, so I knew I had to write a data iterator, so I did not change the scan and contour functions after part 1.
However, I wrote a function in *scan.py* to read in the whole scan of the image to see if there are different pixel spacings. 

### How do you/did you verify that the pipeline was working correctly?
I tested the data iterator, by letting it run through all the samples and I verified the ids and the shapes.
I also did a visual check on the masks and the contours to see if they fit together.
I included a few examples, but every contour and accompanying slice can be plotted with the **generate_border_plots** method in *test.py*. 

<img src="examples/SC-HF-I-1_SCD0000101_68.jpg?raw=true" title="SC-HF-I-1_SCD0000101_68" width="350"> <img src="examples/SC-HF-I-2_SCD0000201_67.jpg?raw=true" title="SC-HF-I-2_SCD0000201_67" width="350">

<img src="examples/SC-HF-I-2_SCD0000201_80.jpg?raw=true" title="SC-HF-I-2_SCD0000201_80" width="350"> <img src="examples/SC-HF-I-4_SCD0000301_20.jpg?raw=true" title="SC-HF-I-4_SCD0000301_20" width="350">


### Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?
I would have to profile the pipeline for where it consumes most of the runtime, but that only matters if reading the data is a bottleneck. It could as well be the computations on the GPU.

I would interpolate each scan to the same pixel spacing. I made some provisions to be able to add this easily in the **data_prep_fun** method. Now I only have five patient scans and four of them have the same x,y pixel spacings, so the straightforward thing to do is to transform the one special case to most occuring pixel spacing. However, typically there are going to be more diverse pixel spacings and it could be easier to just transform everything to 1mmx1mm. It depends on the distribution in the whole dataset, so maybe in phase 2, I will know what to do.

If I had more time, I would also add more safeguards and assertions.


# Questions Phase 2
## Part 1: Parse the o-contours
### After building the pipeline, please discuss any changes that you made to the pipeline you built in Phase 1, and why you made those changes.

I added a method **get_list_available_ocontours** to *contour.py*. It is very similar to the **get_list_available_icontours**. It just returns the list of available o-contours. This list can be used to check which o-contours are available.

I made a new data iterator and I choose to output both the i-contour and o-contour.
I checked the generated o-contours with by **generate_ocontours_icontours_border_plots** method and I found some problems.

I start with two good examples:

<img src="examples/contour_plot_good_SC-HF-I-4_SCD0000301_180.jpg?raw=true" title="SC-HF-I-4_SCD0000301_180" width="350"> <img src="examples/contour_plot_good_SC-HF-I-2_SCD0000201_80.jpg?raw=true" title="SC-HF-I-2_SCD0000201_80" width="350">

 
One patient, **SC-HF-I-6_SCD0000501**, was dramatic. 
All the o-contours of this patient were off.

Here are a few examples:

<img src="examples/contour_plot_bad_SC-HF-I-6_SCD0000501_199.jpg?raw=true" title="SC-HF-I-6_SCD0000501_199" width="350"> <img src="examples/contour_plot_bad_SC-HF-I-6_SCD0000501_59.jpg?raw=true" title="SC-HF-I-6_SCD0000501_59" width="350">


Others seemed fine, but there were some minor issues.
To investigate this I made a method, **generate_masked_scan_plots**, to plot a closeup of the masked scan. The masks are made from the o-contours.

<img src="examples/suspicious_masked_scan_SC-HF-I-5_SCD0000401_40.jpg?raw=true" title="SC-HF-I-5_SCD0000401_40" width="200"> <img src="examples/suscpicious_masked_scan_SC-HF-I-1_SCD0000101_59.jpg?raw=true" title="SC-HF-I-1_SCD0000101_59" width="200"> <img src="examples/suspicious_masked_scan_SC-HF-I-5_SCD0000401_200.jpg?raw=true" title="SC-HF-I-5_SCD0000401_200" width="200">

In the left and center plot you can see the contours suddenly cut off a piece of the ventricle, this leads to a part of the border not be in the mask.
In the center and right plot you can also see that ocontour is not precisely fit to the outside border of the ventricle.


## Part 2: Heuristic LV Segmentation approaches
### Let’s assume that you want to create a system to outline the boundary of the blood pool (i-contours), and you already know the outer border of the heart muscle (o-contours). Compare the differences in pixel intensities inside the blood pool (inside the i-contour) to those inside the heart muscle (between the i-contours and o-contours); could you use a simple thresholding scheme to automatically create the i-contours, given the o-contours? Why or why not? Show figures that help justify your answer.

Simple tresholding is not really a solution here.
If we take a look at the histograms of the pixels inside the o-contours, then we see that they change significantly. Some masked slices have pixel values ranging from 0-500 (eg. SC-HF-I-1_SCD0000101_99) and other slices (e.g. SC-HF-I-4_SCD0000301_20) have pixel values between 0-200. I looked at the metadata of the DICOM files and there was no 'rescale slope' and 'intercept' tags, so that was not the issue. I also looked at the other metadata tags, but I could not find anything suspicious.

Despite of the conclusion based on the histograms, I tried a threshold value of 150 for all the scans based on the histograms, but then you can observe in the following plots that it works for some scans but not for all.
For each slice I plot the masked scan on the left, the histogram in the center and the resulting mask on the right.

Good samples (with some minor issues)
<img src="examples/hist_masked_sc_SC-HF-I-5_SCD0000401_200.jpg?raw=true" title="SC-HF-I-5_SCD0000401_200" width="350"> <img src="examples/hist_masked_sc_SC-HF-I-5_SCD0000401_140.jpg?raw=true" title="SC-HF-I-5_SCD0000401_140" width="350">

<img src="examples/hist_masked_sc_SC-HF-I-4_SCD0000301_120.jpg?raw=true" title="SC-HF-I-4_SCD0000301_120" width="350"> <img src="examples/hist_masked_sc_SC-HF-I-4_SCD0000301_100.jpg?raw=true" title="SC-HF-I-4_SCD0000301_100" width="350">


Bad samples with different issues:

1. The ocontour does not fit well for these two examples, as mentioned in the previous section.

<img src="examples/hist_masked_sc_SC-HF-I-1_SCD0000101_79.jpg?raw=true" title="SC-HF-I-1_SCD0000101_79" width="350"> <img src="examples/hist_masked_sc_SC-HF-I-1_SCD0000101_59.jpg?raw=true" title="SC-HF-I-1_SCD0000101_59" width="350">

2. The tendinous chords in the ventricle show up in our mask.

<img src="examples/hist_masked_sc_SC-HF-I-4_SCD0000301_80.jpg?raw=true" title="SC-HF-I-4_SCD0000301_80" width="350"> <img src="examples/hist_masked_sc_SC-HF-I-2_SCD0000201_100.jpg?raw=true" title="SC-HF-I-2_SCD0000201_100" width="350">

3. Treshold is completely off

<img src="examples/hist_masked_sc_SC-HF-I-5_SCD0000401_100.jpg?raw=true" title="SC-HF-I-5_SCD0000401_100" width="350"> <img src="examples/hist_masked_sc_SC-HF-I-1_SCD0000101_159.jpg?raw=true" title="SC-HF-I-1_SCD0000101_159" width="350">

We could try to change the treshold for each slice seperately. The treshold could be based on the histogram of the pixel values inside the ocontour. There are typically  two distinct groups of pixel values, as can be seen in the histograms. The first group is the pixels representing the contents of the ventricle and the other is the pixels representing the border of the ventricle.

Dynamic tresholding will not solve the third issue which is the occurence of the tendinous chords in the mask. 

### Do you think that any other heuristic (non-machine learning)-based approaches, besides simple thresholding, would work in this case? Explain.

We could use the morphological operations erosion and dilation to improve an tresholding approach. It could connect areas during dilation and to make sure the tendinous chords are emerged in the mask. Once emerged we could delete the tendons by labeling the regions inside the mask.
However in my opinion this heuristic approach takes a lot of time and tuning.

Another idea is to start from the o-contour based mask and erode the border away from the mask. We could repeatedly do small disk erosions and check if the included border pixels have different pixel values. The treshold is again a parameter that is hard to tune.
Another limitation of this method is that it assumes that the thickness of the border of the ventricle is equal in all the areas.


