### Commercial Detector
# Paul Jacobs
# v0.1.2
# Updated 12/19/14
# Some comments adjusted 4/4/17

from essentia.standard import *
from pylab import plot, show, figure, imshow, axis, subplot
from numpy import *
from ordereddict import OrderedDict
import yaml
import sys


# config constants
silenceThreshold = 1.0e-4
commercialLengthVariance = 0.15 # 0.0 - 1.0 / 1.0 = 100%
commercialUnitLength = 15.0 # seconds
minimumCommercialLength = 7.5 # seconds

#constants
sr = 44100
inputDir = 'input/'
outputDir = 'output/'

#hopSz = 5120 ## too big - innacurate start times for commercials
#hopSz = 2048 ## too small - split the third commercial into 3 pieces
hopSz = 3000

frameDuration = (hopSz * 1.0) / sr

# converters for time
def framesToSeconds(frame):
	return frame*frameDuration;

def secondsToTime(sec):
	return str(int(sec/60))+':'+str(trunc((sec%60.0)*10)*0.1)+'/'+str(int(sec*10)*.1)+'/'+str(int(sec/frameDuration))

def secondsToShortTime(sec):
	return str(int(sec/60))+':'+str(trunc((sec%60.0)*10)*0.1)


def framesToTime(frame):
	return secondsToTime(framesToSeconds(frame))

## Default Inputs
### Tested and Working Great
#inputFile = 'Safari_20141212_1103_CommercialDetection_pandora.aiff'
#inputFile = 'Safari_20141219_0353_CommercialDetection_pandora.aiff'
inputFile = 'Safari_20141129_1443_CommercialDetection_irregular_short.aiff'
# inputFile = 'Safari_20141129_1547_CommercialDetection_Colbert.aiff'


# storage
pool = essentia.Pool()

if (len(sys.argv) > 1):
	inputFile = sys.argv[1]
	inputDir = ''
else:
    print "Using default " + inputDir+inputFile
# processing module setup
audio = MonoLoader(filename = inputDir+inputFile)()

w = Windowing(type = 'hann')
levels = LevelExtractor(frameSize = hopSz*4, hopSize = hopSz)

# Additional audio data to operate on if/when useful
#    spectrum = Spectrum()  # FFT() would return the complex FFT, here we just want the magnitude spectrum
#    mfcc = MFCC()
#    rms = RMS()
#    loudness = Loudness()



# processing stream

# get levels
pool.add('lowlevel.levels',levels(audio))

# find silent frames
pool.add('silenceDetected',essentia.array(pool['lowlevel.levels'][0] < silenceThreshold))

# find beginning and end frames of silence periods
sil = pool['silenceDetected'][0];
silences = OrderedDict()
silencesInSecs = OrderedDict()

it = nditer([sil, None], 
       flags=['c_index', 'refs_ok'],
       op_flags=[['readonly'],['writeonly','allocate']])

while not it.finished:
    if (sil[it.index] == 1.0): # preserve edges
        if (it.index > 0 and sil[it.index-1] == 0):
            it[1] = 1; # beginning of silence
            silences[it.index] = 1
            silencesInSecs[framesToTime(it.index)] = 1
        elif (it.index < (sil.shape[0]-1) and sil[it.index+1] == 0):
            it[1] = 2; # end of silence
            silences[it.index] = 2
            silencesInSecs[framesToTime(it.index)] = 2
        else:
            it[1] = 0; # no change observed
    else:
        it[1] = 0;
    it.iternext()

silenceEdges = it.operands[1]
pool.add('silenceEdges',silenceEdges)

segments = OrderedDict()
commercials = OrderedDict()
commercialsBySample = OrderedDict()

thisSilenceStartTime = 0;
lastSilenceFinishTime = 0;
lastSilenceFinishTimeInSeconds = 0.0;
soundDuration = 0;
soundDurationInSeconds = 0.0;
for timeIndex in sorted(silences):
#	print "timeIndex "+framesToTime(timeIndex)
	edgeType = silences[timeIndex]
	if edgeType == 1: # start of silence
		thisSilenceStartTime = timeIndex
		soundDuration = thisSilenceStartTime - lastSilenceFinishTime
		soundDurationInSeconds = framesToSeconds(soundDuration)
		segments[secondsToShortTime(framesToSeconds(lastSilenceFinishTime))] = secondsToShortTime(framesToSeconds(soundDuration))
#		print "segment starting "+framesToTime(lastSilenceFinishTime)+" - "+str(soundDurationInSeconds)+"\n"
		if ((soundDurationInSeconds <= commercialUnitLength * 5) and \
			(soundDurationInSeconds > minimumCommercialLength) and \
			((soundDurationInSeconds % commercialUnitLength) <= \
				commercialUnitLength*commercialLengthVariance or \
				((soundDurationInSeconds % commercialUnitLength) >= \
				(commercialUnitLength - commercialUnitLength*commercialLengthVariance)))):
					commercials[framesToTime(lastSilenceFinishTime)] = secondsToShortTime(soundDurationInSeconds)
					commercialsBySample[lastSilenceFinishTime*hopSz] = soundDuration
					commercialsBySample[(lastSilenceFinishTime+soundDuration)*hopSz] = soundDuration
					
	if edgeType == 2: # end of silence
		lastSilenceFinishTime = timeIndex;
		lastSilenceFinishTimeInSeconds = framesToSeconds(lastSilenceFinishTime)

# Save / Print results (time ranges of detected commercials in input file)
#YamlOutput(filename = outputDir + inputFile + '.silences.yaml')([pool['silenceEdges'],{'silences':silences, 'segments':segments, 'commercials':commercials}])
print yaml.dump({'silences':silences, 'segments':segments, 'commercials':commercials})

# Save Features Data (when uncommented)
#aggPool = PoolAggregator(defaultStats = ['mean','var'])(pool)
#YamlOutput(filename = outputDir + inputFile + '.features.yaml')(aggPool)

# TODO: Edit audio file to remove commercials, save edited audio.




