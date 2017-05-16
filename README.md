# Questions Part 1
### How did you verify that you are parsing the contours correctly?
I did a visual check on the masks and the contours.
The function plot_polygone_on_mask in tests.py, can be used to generate those plots.
After visual inspection, I saw that the binary masks that were generated with poly_to_mask function do not completely fit the polygons defined in the original contour files.
After reading the solution on stackoverflow, I saw the following comment:
http://stackoverflow.com/questions/3654289/scipy-create-2d-polygon-mask#comment59125132_3732128
The solution used in the original poly_to_mask function only works with integer coordinate (i.e. grid coordinates)

### What changes did you make to the code, if any, in order to integrate it into our production code base? 
I used the skimage.draw.polygon function, which behaves much nicer with floating point vertices as can be seen in the few examples that I included in the problem_cases folder.



# Questions part 2
Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?
I first read the whole exercise, so I knew I had to write a data iterator, so I did not change the scan and contour functions after part 1

How do you/did you verify that the pipeline was working correctly?
I tested the data iterator, by letting it run through all the samples and I verified the ids and the shapes.

Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?
I would have to profile the pipeline for where it takes to much time, but that only matters if reading the data is a bottleneck. It could as well be the computations on the GPU

If I had more time, I would add more safeguards and assertions.
