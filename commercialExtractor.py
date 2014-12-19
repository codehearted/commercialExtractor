### Commercial Detector
# Paul Jacobs
# v0.1.1
# Updated 12/12/14

from essentia.standard import *
from pylab import plot, show, figure, imshow, axis, subplot
from numpy import *


#constants
sr = 44100
inputDir = 'input/'
outputDir = 'output/'

#inputFile = 'Safari_20141129_1443_CommercialDetection_irregular_short.aiff'
inputFile = 'Safari_20141212_1103_CommercialDetection_pandora.aiff'

print 'processing: ' + inputFile

# setup modules
audio = MonoLoader(filename = inputDir+inputFile)()
w = Windowing(type = 'hann')
spectrum = Spectrum()  # FFT() would return the complex FFT, here we just want the magnitude spectrum
mfcc = MFCC()
rms = RMS()
levels = LevelExtractor(frameSize = 20480, hopSize = 5120)
loudness = Loudness()

# get audio
#audio = loader()

## Essentia Way ##
pool = essentia.Pool()

pool.add('lowlevel.levels',levels(audio))
pool.add('lowlevel.loudness',loudness(audio))

for frame in FrameGenerator(audio, frameSize = 2048, hopSize = 512):
    mfcc_bands, mfcc_coeffs = mfcc(spectrum(w(frame)))
    pool.add('lowlevel.mfcc',mfcc_coeffs)
    rms512 = rms(w(frame))
    pool.add('lowlevel.rms512',rms512)
	

# and plot
# t = linspace(0, (audio.size/5167.96), pool['lowlevel.rms512'].size)

figure(1)
subplot(2,1,1)
plot(pool['lowlevel.rms512'])
subplot(2,1,2)
plot(audio)
show()

plot(pool['lowlevel.loudness'])
show()
figure()

plot(pool['lowlevel.levels'])
show()
figure()

#imshow(pool['lowlevel.mfcc_bands'].T, aspect='auto', interpolation='nearest')
#show() # unnecessary if you started "ipython --pylab"
#figure()

imshow(pool['lowlevel.mfcc'].T[1:,:], aspect = 'auto')
show() # unnecessary if you started "ipython --pylab"

aggPool = PoolAggregator(defaultStats = ['mean','var'])(pool)
YamlOutput(filename = outputDir + inputFile + '.features.yaml')(aggPool)

