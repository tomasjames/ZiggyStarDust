################################################################################
############################ 4th Year Project Code #############################
############################## Initial Simulation ##############################
################################################################################

############################# Import statements ################################
# Import RADMC-3D
import radmc3dPy

# Import OS manipulation tools
import os

# Import time tools
import time

# Import units
from radmc3dPy.natconst import *

# Import numpy
import numpy as np

# Import csv
import csv

# Import matplotlib
from matplotlib.pyplot import *

# Import astropy
from astropy.io import fits, convolution

###################### Check for correct default.inp files #####################

print '########################################################################'
print '########################## Default File Check ##########################'
print '########################################################################'

# Check to see whether radmc3d.inp exists. If so, leave it alone and if not write it to the working directory
if os.path.isfile('radmc3d.inp') == True:
    print '\nradmc3d.inp already exists; no need to write/overwrite\n'
else:
    # This line writes the radmc3d.inp file and then immediately closes it
    open('radmc3d.inp', 'w').close()
    print '\n--->radmc3d.inp did not alreadt exists; a blank file called radmc3d.inp has been written to the working directory\n'

############################## Set up initial model ############################
# Call the data file generation generation script to write the necessary files to the working directory
execfile('/Users/tomasjames/Documents/University/Project/ZiggyStarDust/Code/datafiles/vanilla/datafilegen.py')

############################## Set up initial model ############################
# Writes the default parameter file for the 2d sphere model
radmc3dPy.analyze.writeDefaultParfile('3d_cloud')

# Setup the dust module with the ascii input files
radmc3dPy.setup.problemSetupDust('3d_cloud', binary=False, nx=128, ny=128, nz=128, xbound=[-15000*au,15000*au], ybound=[-15000*au,15000*au], zbound=[-15000*au,15000*au], nphot=1500000.)

############################ Run Monte-Carlo simulation ########################

# Interface with operating system to run the Monte-Carlo sim (and allowing the
# code to use wavelength_micron.inp)
os.system('radmc3d image loadlambda')

########################## Initailise the resulting data #######################

# Define wavelength ranges of spire to plot (PSW, PMW and PLW)
psw_ext = [199.4540,298.5657]

# Plot image for first SPIRE wavelength band (PSW)
#radmc3dPy.image.makeImage(npix=100000, sizeau=15000, incl=90., lambdarange=psw_ext, nlam=60)

############################### Manipulate the PSF #############################

# Determine which of the PSFs exists in the folder
files = glob.glob('./*spire*')

if files == ['./theoretical_spire_beam_model_psw_V0_2.fits']:
    # Read in the PSF
    hdulist = fits.open('./theoretical_spire_beam_model_psw_V0_2.fits')
else:
    print 'There is no PSF data file. Please download from http://dirty.as.arizona.edu/~kgordon/mips/conv_psfs/conv_psfs.html and rerun the code.\n'

# Extract the image data
img_data = hdulist[0].data

########################### Account for transmission ###########################

# Initialise the data from the ray trace
# This is stored in the class radmc3dImage
imag = radmc3dPy.image.readImage('image.out')

# Read in the specially created file holding the interpolated transmissions
trans_data = np.loadtxt('transmission.txt')

# Write a new image.out file called image_trans.out that will contain all of the new intensity information
with open('image_trans.out', 'w') as f:
    #image_trans = open('image_trans.out', 'w')
    image_trans = csv.writer(f, delimiter=' ')

    # Begin writing of the file by writing the format number
    #image_trans.writerows(str(1)+str('\n'))
    image_trans.writerow([1])

    # Write the number of pixels in x and y dimensions
    #image_trans.write("%.f" % imag.nx)
    #image_trans.write(" %.f \n" % imag.ny)
    image_trans.writerow([imag.nx, imag.ny])

    # Write the number of wavelength points
    #image_trans.write(str('          ')+str(imag.nwav)+str('\n'))
    #image_trans.writerow([imag.nwav])
    image_trans.writerow([1])

    # Write the pixel sizes
    #image_trans.write("%.f" % imag.sizepix_x)
    #image_trans.write(" %.f \n" % imag.sizepix_y)
    image_trans.writerow([imag.sizepix_x, imag.sizepix_y])

    # Because the image is a composite of all wavelengths, only write the average of the wavelength points
    avwav = np.mean(imag.wav)
    image_trans.writerow(["%.15f" % avwav])
    # Writes a blank line to seperate the wavelength points from the intensity points
    image_trans.writerow([])

    # Begin computing transmission weighted sum
    # This is to be achieved by looping through each pixel in the image and multiplying by each transmission coefficient at that wavelength. This is then summed along all wavelengths to give a 'composite' image

    # Declare a list to store the variables
    store = []
    summation = []

    for i in range(0, imag.nx):
        for j in range(0, imag.ny):
            for k in range(0, imag.nwav):
                #if i == 0. and j == 0. and k == 0.:
                    #image_trans.write('  \n')
                store.append(np.float64(imag.image[i][j][k]*trans_data[k][1]))
            summation.append(np.float64(np.sum(store)))
            #image_trans.write(str(np.sum(store))+str('\n'))
            store = []

    image_trans.writerows(zip(np.float64(summation)))

# Close the file for memory purposes
#image_trans.close()

########################## Plot the resulting data #######################

# Initialise the image
imag_trans = radmc3dPy.image.readImage('image_trans.out', binary=False)

# Plot the image in a matplotlib figure
radmc3dPy.image.plotImage(imag_trans, arcsec=False, au=True, dpc=150., log=False, bunit='inu')

print '\n######################################################################'
print 'Please run the command \"viewimage\" in the Terminal at this point to'
print 'start the GUI image viewer'
print '########################################################################'
