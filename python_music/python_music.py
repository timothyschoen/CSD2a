from pyo import *
import forms
import random
import threading
import itertools


#Define our basic musical data
key = random.randrange(0, 11)
scale = [0,2,4,5,7,9,11]
scale = [(x+key)%12 for x in scale]
rhythmlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
chordlst = [2, 7, 5, 3, 1, 6, 4]
chordprogression = []
fullscale = []
#Start our audioserver
s = Server(nchnls=2, duplex=0, sr=20068, buffersize=512).boot()
s.start()

# set bpm
bpm = 140
# calculate the duration of a quarter note
quarterNoteDuration = 60 / bpm
# calculate the duration of a sixteenth note
sixteenthNoteDuration = quarterNoteDuration / 4.0
# number of beats per sequence (time signature: 3 / 4 = 3 beats per sequence)
beatsPerMeasure = 10
measureCount = 0

subdivision = 5;
# calculate the duration of a measure
measureDuration = beatsPerMeasure  * quarterNoteDuration

events = []
# create lists with the moments (in 16th) at which we should play the samples
leadsynth = []
harmonysynth = []
basssynth = []
arpsynth = []
#Set startnotes
prevnote = 60;
prevbass = 48;
prevarp = 60;
lastnotes = []

#kick and snare patterns
kickpatt = []
snarepatt = []
#Vibrato on the lead that we can trigger when we want
VibrEnv = Adsr(attack=0.01, decay=0.5, sustain=0.6, release=0.5, dur=2, mul=15)
VibrLFO = Sine(freq=6, mul=VibrEnv)
#Create 3 square wave oscillators
square = SquareTable()
#triangle = TableRec(RCOsc(freq=a.freq,  table=t, fadetime=0.01)

oscadsr = Adsr(attack=0, decay=1, sustain=0.2, release=1, dur=sixteenthNoteDuration, mul=0.3)
a = Osc(table=square, freq=0, mul=oscadsr)
b = Osc(table=square, freq=0, mul=oscadsr)
arpadsr = Adsr(attack=0, decay=0.1, sustain=0.2, release=0.2, dur=0.1, mul=0)
arpeggiosynth = Osc(square, freq=0, mul=arpadsr)
bassadsr = Adsr(attack=0, decay=1, sustain=0.2, release=1, dur=sixteenthNoteDuration, mul=0.4)
c = Osc(square, freq=0, mul=bassadsr)
#Make a snare out of noise, with adsr we can trigger
snare = Adsr(attack=0, decay=0.1, sustain=0.1, release=0.1, dur=0.1, mul=8)
snareosc = Noise(mul=snare)
#Make a kick with a low square wave
kick = Adsr(attack=0, decay=0.1, sustain=0.3, release=0.3, dur=0.2, mul=25)
kickosc = Round(Osc(square, freq=55, mul=kick), mul=0.6)
#Master bus with 4-bit, just like a NES
effect = Degrade(a+b+c+kickosc+snareosc+arpeggiosynth, bitdepth=5, mul=0.13).out()
# Function to generate one measure of music

def composeProgression():
    chordlst = [1, 6, 4, 2, 7, 5, 3]
    options = subset_sum([-2, -1, 1, 2, -1, 1], 1)
    newlst = list(options for options,_ in itertools.groupby(options))
    movelist = random.choice(newlst)
    random.shuffle(movelist)
    fixedlist = []
    for i in range(len(movelist)):
        fixedlist.append((chordlst[sum(movelist[:i])])%7)
    return fixedlist


def composeseq():
    global key
    global a
    global b
    global scale
    global prevnote
    global lastnotes
    global snarepatt
    global kickpatt
    global leadsynth
    global harmonysynth
    global arpsynth
    global basssynth
    global chordprogression
    global fullscale
    global prevbass
    global prevarp
    global subdivision
    global lastnotes
    #generate new parts with different sound, rhythm and key
    arrangement = random.randrange(3)
    if arrangement == 0:
        shape = random.choice([square, square])
        a.table = shape
        b.table = shape
        #print(shape)
        scale = [(x+7)%12 for x in scale]
        key = (key+7)%12
        subdivision = random.choice([5,7])
        oscadsr.stop()
        bassadsr.stop()
        b.mul=oscadsr
        oscadsr.decay = 50
        bassadsr.decay = oscadsr.decay
        arpadsr.mul = 0
    elif arrangement == 1:
        oscadsr.decay = 0.3
        bassadsr.decay = oscadsr.decay
        b.mul=0
        arpadsr.mul = 0.4
        bpm = random.randrange(90, 130)
    elif arrangement == 2:
        oscadsr.decay = 0.3
        b.mul=oscadsr
        arpadsr.mul = 0.3
    #Generate chords
    progression = composeProgression()
    #Generate rhythm section
    snarepatt = [[4, 120]]
    random.shuffle(rhythmlist)
    for i in range(random.randrange(4, 7)):
        snarepatt.append([rhythmlist[i], 70])
    snarepatt.sort()
    kickpatt = [[1, 120],[subdivision,120], [11, 120], [subdivision+10, 120], [21, 120], [subdivision+20, 120], [31, 120], [subdivision+30, 120]]
    for i in range(random.randrange(3, 6)+7):
        kickpatt.append([rhythmlist[i], 80])
    kickpatt.sort()
    #synth rhythms
    leadsynth = [[1], [subdivision], [11], [subdivision+10], [21], [subdivision+20], [31], [subdivision+30]]
    harmonysynth = [[1], [subdivision], [11], [subdivision+10], [21], [subdivision+20], [31], [subdivision+30]]
    random.shuffle(rhythmlist)
    for i in range(random.randrange(5, 10)):
        leadsynth.append([rhythmlist[i]])
        harmonysynth.append([rhythmlist[i]])
    leadsynth.sort()
    harmonysynth.sort()
    previndex = 0
    basssynth = [[0]]
    for i in range(40):
        chordindex = int(i/(40 / len(progression)+1))
        if previndex != chordindex and i%2 == 0:
            basssynth.append([i])
            previndex = chordindex
        elif int((i+1)/6) != chordindex and i%2 == 1 and random.randrange(3) == 0:
            basssynth.append([i])
    #Generate harmony
    random.shuffle(chordlst)
    chordprogression = []
    for i in progression:
        scalepos = scale[i-1]
        if i == 1 or i == 4:
            chordprogression.append(spreadNotes([scalepos, scalepos+4, scalepos+7, scalepos+11]))
        elif i == 5:
            chordprogression.append(spreadNotes([scalepos, scalepos+4, scalepos+7, scalepos+10]))
        elif i == 2 or i == 3 or i == 6:
            chordprogression.append(spreadNotes([scalepos, scalepos+3, scalepos+7, scalepos+10]))
        else:
            chordprogression.append(spreadNotes([scalepos, scalepos+3, scalepos+6, scalepos+10]))
    fullscale = spreadNotes(scale)
    dir = random.choice([-1, 1])
    for i in range(len(leadsynth)):
        chordindex = int(leadsynth[i][0] / (40 / len(progression)+1))
        if random.randrange(4) == 0:
            dir = random.choice([-3, -2, -1, 1, 2, 3])
        if prevnote > 84 and dir > 0 or prevnote < 60 and dir < 0:
            dir = int(dir/abs(dir))*-1
        if leadsynth[i][0] % 2 == 0:
            print("index:", chordindex)
            print("length progression:", len(chordprogression))
            print("length chord:", len(chordprogression[chordindex]))
            print("nearest", find_nearest(chordprogression[chordindex], prevnote)+dir)
            leadnote = chordprogression[chordindex][find_nearest(chordprogression[chordindex], prevnote)+dir]
            harmonynote = chordprogression[chordindex][find_nearest(chordprogression[chordindex], leadnote)+dir]
            leadsynth[i].append(leadnote)
            harmonysynth[i].append(harmonynote)
            if abs(prevnote-leadnote) > 2:
                dir = int(dir/abs(dir))*-1
            lastnotes.append(leadnote)
            prevnote = leadnote
        else:
            leadnote = fullscale[find_nearest(fullscale, prevnote)+int(dir/abs(dir))]
            harmonynote = fullscale[find_nearest(fullscale, leadnote)+2]
            leadsynth[i].append(leadnote)
            harmonysynth[i].append(harmonynote)
            if abs(prevnote-leadnote) > 2:
                dir = int(dir/abs(dir))*-1
            prevnote = leadnote
        #generate bass notes
    if random.randrange(3) == 0:
        bassdir = random.choice([-2, 2])
    else:
        bassdir = random.choice([-1, 1])
    for i in range(len(basssynth)):
        chordindex = int(basssynth[i][0] / (40 / len(progression)+1))
        if prevbass > 60 and bassdir > 0 or prevbass < 48 and bassdir < 0:
            bassdir = int(bassdir/abs(bassdir))*-1
        if basssynth[i][0] % 2 == 0:
            bassnote = chordprogression[chordindex][find_nearest(chordprogression[chordindex], prevbass)+bassdir]
            basssynth[i].append(bassnote)
            if abs(prevbass-bassnote) > 2:
                bassdir = int(bassdir/abs(bassdir))*-1
            prevbass = bassnote
        else:
            bassnote = fullscale[find_nearest(fullscale, prevbass)+int(bassdir/abs(bassdir))]
            basssynth[i].append(bassnote)
            if abs(prevbass-bassnote) > 2:
                bassdir = int(bassdir/abs(bassdir))*-1
            prevbass = bassnote
    arpdir = 1
    prevarp = chordprogression[0][int(len(chordprogression[0])/2)]
    for i in range(40):
        chordindex = int(i / (40 / len(progression)+1))
        if (i % 5) == 0:
            arpdir = arpdir*-1
        arpnote = chordprogression[chordindex][find_nearest(chordprogression[chordindex], prevarp)+arpdir]
        prevarp = arpnote
        arpsynth.append([i, arpnote])

def playseq():
    global measureCount
    if measureCount % 4 == 0:
        composeseq()
    measureCount = measureCount + 1
    #Add each instrument's array to a sorted eventlist
    for note in leadsynth:
        events.append([note[0] * sixteenthNoteDuration, 0, note[1]])
    for note in harmonysynth:
        events.append([note[0] * sixteenthNoteDuration, 1, note[1]])
    for note in arpsynth:
        events.append([note[0] * sixteenthNoteDuration, 2, note[1]])
    for note in basssynth:
        events.append([note[0] * sixteenthNoteDuration, 3, note[1]])
    for note in snarepatt:
        events.append([note[0] * sixteenthNoteDuration, 4, note[1]])
    for note in kickpatt:
        events.append([note[0] * sixteenthNoteDuration, 5, note[1]])
    # transform the sixteenthNoteSequece to an eventlist with time values
    # NOTE: The line below is essential to enable a correct playback of the events
    events.sort()
    # display the event list
    #print(events)
    # retrieve first event
    # NOTE: pop(0) returns and removes the element at index 0
    event = events.pop(0)
    # retrieve the startime: current time
    startTime = time.time()
    keepPlaying = True
    # play the sequence
    while keepPlaying:
      # retrieve current time
      currentTime = time.time()
      # check if the event's time (which is at index 0 of event) is passed
      if(currentTime - startTime >= event[0]):
        # play sample -> sample index is at index 1
        #Change lead frequency
        if event[0] == 0 and event[1] == 0 and random.randrange(0, 2) == 1 and event[2] > 72:
            VibrEnv.play()
        elif event[0] > 1:
            VibrEnv.stop()
        if event[1] == 0:
            a.freq = noteToFreq(event[2])+VibrLFO
            oscadsr.stop()
            oscadsr.play()
        #Change harmony frequency
        elif event[1] == 1:
            b.freq = noteToFreq(event[2])+VibrLFO
            oscadsr.stop()
            oscadsr.play()
        #Change bass frequency
        elif event[1] == 2:
            arpeggiosynth.freq = noteToFreq(event[2])
            arpadsr.play()
        elif event[1] == 3:
            c.freq = noteToFreq(event[2])
            bassadsr.stop()
            bassadsr.play()
        #Trigger snare
        elif event[1] == 4:
            snare.mul = event[2]/127
            snare.play();
        #Trigger kick
        elif event[1] == 5:
            kick.mul = event[2]/127
            kick.play();
        # if there are events left in the events list
        if events:
          # retrieve the next event
          event = events.pop(0)
        else:
          # list is empty, stop loop
          keepPlaying = False
      else:
        # wait for a very short moment
        time.sleep(0.001)
    gottaRepeat = True
    # repeat it n times
    while gottaRepeat:
        currentTime = time.time()
        # check if the measure is over
        if(currentTime - startTime >= measureDuration):
            # if we havent, play again
            playseq()
        else:
            time.sleep(0.001)

#Function to convert MIDI pitch to frequency
def noteToFreq(note):
    a = 440 #frequency of A (common value is 440Hz)
    return (a / 32) * (2.001 ** ((note - 9) / 12))
#Find nearest note in an array, used to find suitable followup notes
def find_nearest(array, value):
    n = [abs(i-value) for i in array]
    return n.index(min(n))

def subset_sum(numbers, target, partial=[], output=[]):
    s = sum(partial)
    # check if the partial sum is equals to target
    if s == target:
        if len(partial) > 1 and len(partial) < 5:
            output.append(partial)
    if s >= target:
        return  # if we reach the number why bother to continue
    for i in range(len(numbers)):
        n = numbers[i]
        remaining = numbers[i+1:]
        subset_sum(remaining, target, partial + [n])
    else:
        return output

#function to spread any scale or chord over the full MIDI range
def spreadNotes(notes):
    newnotes = []
    for i in notes:
        for j in range(-10, 10):
            if (i % 12) + (j * 12)  >= 0 and (i % 12) + (j * 12) <= 127:
                newnotes.append((i % 12) + (j * 12))
    newnotes.sort()
    return newnotes
#Run the music in a thread so that asciimatics can use the terminal window
thread1 = threading.Thread(target=playseq)
thread1.start()

#Visuals using asciimatics
from math import sqrt
from asciimatics.renderers import Kaleidoscope, FigletText, Rainbow, RotatedDuplicate, \
    StaticRenderer
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Print
from asciimatics.exceptions import ResizeScreenError
import sys

def demo(screen):
    scenes = []
    cell = "    "
    size = int(sqrt(screen.height ** 2 + screen.width ** 2 // 4))
    for _ in range(size):
        for x in range(size):
            c = x * screen.colours // size
            cell += "${%d,2,%d}:" % (c, c)
        cell += "\n"
    scenes.append(
        Scene([Print(screen,
                     Kaleidoscope(screen.height, screen.width, StaticRenderer([cell]), 3),
                     0,
                     speed=1,
                     transparent=False)],
              duration=1000))
    screen.play(scenes, stop_on_resize=False, allow_int=True)


if __name__ == "__main__":
    while True:
        try:
            Screen.wrapper(demo)
            sys.exit(0)
        except ResizeScreenError:
            pass
