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

# storage
pool = essentia.Pool()

print 'processing: ' + inputFile

# processing module setup
audio = MonoLoader(filename = inputDir+inputFile)()
w = Windowing(type = 'hann')
spectrum = Spectrum()  # FFT() would return the complex FFT, here we just want the magnitude spectrum
mfcc = MFCC()
rms = RMS()
levels = LevelExtractor(frameSize = 20480, hopSize = 5120)
loudness = Loudness()
silenceThreshold = 1.0e-4

# processing stream

# get levels
pool.add('lowlevel.levels',levels(audio))

# find silent frames
pool.add('silenceDetected',essentia.array(pool['lowlevel.levels'][0] < silenceThreshold))

# find beginning and end frames of silence periods
sil = pool['silenceDetected'];
it = nditer([sil, None], 
       flags=['c_index', 'refs_ok'],
       op_flags=[['readonly'],['writeonly','allocate']])

if (it.index == 0):
    it[1] = 0
    it.iternext()

while not it.finished:
    if (sil[it.index] == 1.0): # preserve edges
        if (sil[it.index-1] == 0):
            it[1] = 1; # beginning of silence
        elif (sil[it.index+1] == 0):
            it[1] = 2; # end of silence
        else:
            it[1] = 0; # no change observed
    else:
        it[1] = 0;
    it.iternext()

pool.add('silenceEdges',it.operands[1]);

YamlOutput(filename = outputDir + inputFile + '.silences.yaml')(pool['silenceEdges'])

aggPool = PoolAggregator(defaultStats = ['mean','var'])(pool)
YamlOutput(filename = outputDir + inputFile + '.features.yaml')(aggPool)

