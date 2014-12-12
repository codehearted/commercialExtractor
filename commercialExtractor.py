### Commercial Detector
# Paul Jacobs
# v0.1.1
# Updated 12/12/14

from essentia.standard import *
from pylab import plot, show, figure, imshow

#constants
sr = 44100
inputDir = 'input/'
outputDir = 'output/'
inputFile = 'Safari_20141129_1443_CommercialDetection_irregular_short.aiff'

print inputFile

# setup modules
audio = MonoLoader(filename = inputDir+inputFile)()
w = Windowing(type = 'hann')
spectrum = Spectrum()  # FFT() would return the complex FFT, here we just want the magnitude spectrum
mfcc = MFCC()


# get audio
#audio = loader()

## Essentia Way ##
pool = essentia.Pool()

for frame in FrameGenerator(audio, frameSize = 2048, hopSize = 512):
    mfcc_bands, mfcc_coeffs = mfcc(spectrum(w(frame)))
    pool.add('lowlevel.mfcc',mfcc_coeffs)
    pool.add('lowlevel.mfcc_bands',mfcc_bands)


# and plot
imshow(pool['lowlevel.mfcc'].T[1:,:], aspect = 'auto')
show() # unnecessary if you started "ipython --pylab"
figure()
imshow(pool['lowlevel.mfcc_bands'].T, aspect='auto', interpolation='nearest')

aggPool = PoolAggregator(defaultStats = ['mean','var'])(pool)
YamlOutput(filename = outputDir + inputFile + '.features.yaml')(aggPool)

