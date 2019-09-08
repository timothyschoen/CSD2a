## 0. Lijsten samenvoegen, for loops vervangen met list comprehensions waar mogelijk
## 1. Parts balancen aan de hand van hoe vol de afgelopen 8x16e waren ofzo
## 2. Unison modus, mss meer modi voor variatie
## 3. Meer verschil in chord progressions en extentions etc, akkoorden buiten de key (negative harmony?)
## 4. Sound design
## 5. CC's voor timbral changes etc.

import random
import time, sched
import rtmidi
import _thread as thread
import sys
from midiutil.MidiFile import MIDIFile

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
midiout.open_virtual_port("Drums")

midiout2 = rtmidi.MidiOut()
available_ports = midiout2.get_ports()
midiout2.open_virtual_port("Bass")

midiout3 = rtmidi.MidiOut()
available_ports = midiout3.get_ports()
midiout3.open_virtual_port("Keys")

midiout4 = rtmidi.MidiOut()
available_ports = midiout4.get_ports()
midiout4.open_virtual_port("Lead")
# set bpm
bpm = 90
swing = 0.23
measureCount = 0
events = []
noteoffs = []
key = random.randint(0, 11)
scale = [0, 2, 4, 5, 7, 9, 11]
print("0: 4/4       1:5/4       2:7/8")
meterchoice = input("Choose meter: \n >")
if meterchoice == '0':
    meter = 8
    length = 32
    countlist = [i for i in range(32)]
elif meterchoice == '1':
    meter = 2.5
    countlist = [0, 1, 2, 1, 0, 1, 4, 1, 2, 1, 2, 1, 0, 1, 4, 1]
    length = 10
elif meterchoice == '2':
    meter = 3.5
    length = 14
    countlist = [i for i in range(32)]
else:
    print("selected 4/4")
    meter = 8
    length = 32
    countlist = [i for i in range(32)]

parts = [[0 for i in range(length)] for x in range(15)]

def compose():
    global parts, lastparts, swing, voices, key, scale, measureCount, bpm
    if measureCount % 5 == 0:
        measureCount = 1
        if random.randint(0, 1) == 0:
            bpm = random.randint(85, 120)
        if random.randint(0, 2) == 0:
            key = abs(key + random.choice([-5, -2, 2, 7]))%12
        fill = 0
        mode = 1
        parts = [[0 for i in range(length)] for x in range(15)]
        print('Key:', ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C'][key%12])
        print('Tempo:', bpm, "bpm")
        print('>')
    elif measureCount % 5 == 4:
        mode = 2
        fill = 1
    else:
        fill = 0
        mode = 2
    measureCount = measureCount + 1
    lastchord = [60, 64, 67]
    direction = 1
    dir = 1
    openhat = 0
    voices = [[0 for x in range(length)] for x in range(0, 11)]
    parts[1] = [0 for x in range(length)]
    parts[4] = [0 for x in range(length)]
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale = spreadNotes(scale)
    scale = [(x+key) for x in scale]
    for i in range(length):
        lastparts = [lastplayed(parts[z], i) for z in range(len(parts)) if z != 6]
        x = countlist[i%len(countlist)]
        #Generate Chords
        if  x == 0 and mode == 1:
            scalepos = scale[random.randint(0, 5)]
            parts[6][i] = [movement(scalepos+60, scale, 0), movement(scalepos+60, scale, 2), movement(scalepos+60, scale, 4), movement(scalepos+60, scale, 6)]
            change = 1
        elif (x%4 == 0 and random.randint(0, 2) == 0) and mode == 1:
            scalepos = scale[random.randint(0, 5)]
            parts[6][i] = [movement(scalepos+60, scale, 0), movement(scalepos+60, scale, 2), movement(scalepos+60, scale, 4), movement(scalepos+60, scale, 6)]
            change = 1
        elif x > 0 and mode == 1:
            parts[6][i] = parts[6][i-1]
            change = 0
        elif x > 0 and parts[6][i] != parts[6][i-1]:
            change = 1
        elif x == 0:
            change = 1
        else:
            change = 0
        rootnote = parts[6][i][0]
        rootnotes = spreadNotes([parts[6][i][0]])
        fullchord = spreadNotes(parts[6][i])
        if x%8 == 0:
            emphasis = random.choice([0, 1])
        # BASS
        if random.randint(0, 1) == 0  and x%2 == 1 or mode == 1:
            if random.choice([1, 1, parts[0][i-1]==0, parts[0][i-1]==0, parts[0][i-1]==0, parts[0][i-1]==0, change, change, x%2==0, x%2==0, x%2==0, x%2==0, x%2==emphasis, x%2==emphasis, x%4==0, x%4==0, x%2==0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) == 1 or x%8 == 0 and random.randint(0, 1) == 0 or x%16 == 0:
                if lastparts[0][1] > 48:
                    direction = -1
                elif lastparts[0][1] < 36:
                    direction = 1
                if x % 8 == 0 or (change == 1 and random.randint(0,2) == 0):
                    parts[0][i] = movement(lastparts[0][1], rootnotes, 0)
                elif x % 2 == 0:
                    parts[0][i] = movement(lastparts[0][1], fullchord, direction)
                elif x % 2 == 1 and random.choice([0, 1]) == 0:
                    parts[0][i] = movement(lastparts[0][1], scale, direction)
                elif random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, (8*direction)), fullchord, 0)
                elif random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, [-4, 5, 5][direction+1]), fullchord, 0)
                elif random.randint(0, 1) == 0:
                    parts[0][i] = lastparts[0][1]+direction
                else:
                    parts[0][i] = 0
                if parts[0][i] != 0 and abs(lastparts[0][1]-parts[0][i]) > 2:
                    direction = direction*-1
                parts[0][i] = parts[0][i]%24+36
        if x == 0  or parts[0][i] != parts[0][i-1] or mode == 1 and parts[0][i] != 0:
            basschange = 1
        else:
            basschange = 0
        # DRUMS
        # kick
        if mode == 1 or random.randint(0, 4) == 0:
            if x % 8 == 0 and random.randint(0, 3) != 0 or x%16 == 0 or random.randint(0, (x%2)+2) == 0 and random.randint(0, [3, 9, 15, 6][(x+emphasis)%4]) == 0 or basschange == 1 and random.randint(0, 2) == 0:
                parts[2][i] = 36
            else:
                parts[2][i] = 0
            if x >= 4 and (parts[2][i-1]+parts[2][i-2]+parts[2][i-3]+parts[2][i-4]) > 72:
                parts[2][i] = 0
        # Snare
        if random.randint(0, 2) == 0 or mode == 1:
            if x % 8 == 4 or random.randint(0, (x%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or parts[7][i] > 0 and random.randint(0, 1+abs(0-i)%4) == 2:
                parts[3][i] = 38
            else:
                parts[3][i] = 0
        # Hats
        if openhat == 1:
            parts[5][i] = 44
            openhat = 0
        elif random.randint(0, 1) == 0 or mode == 1:
            if random.randint(0, 7+(x%2)*5) == 0:
                openhat = 1
                parts[5][i] = 46
            elif parts[2][i] == 0 and parts[3][i] == 0 and random.randint(0, 1) == 0:
                parts[5][i] = 42
            else:
                parts[5][i] = 0
        # Toms, snares and cymbals for fills
        if fill == 1 and x > 16 and random.randint(0, 3) != 0:
            fillchoice = random.randint(0, 8)+(i-16)
            note = [47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38, 47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38][fillchoice]
            parts[4][i] = note
        if mode == 1:
            parts[4][0] = random.choice([49, 50])
        # KEYS
        if mode == 1 or random.randint(0, 2) == 0:
            if random.choice([1, 1, 1, 1, x%2==1, x%2==1, x%2==emphasis, x%2==emphasis, x%4==2, x%4==2, x%2==0, basschange, basschange, change, change, change, 0, 0, 0, 0, 0, 0]) == 1 or x%8 == 0:
                voicing = arrange(parts[6][i], lastchord)
                if random.randrange(0, 2) != 0:
                    for y in range(7, 10):
                        parts[y][i] = voicing[1]
                        lastchord[y-7] = voicing[y-7]
                    parts[10][i] = parts[6][i][0]-12
                    parts[11][i] = parts[6][i][3]
                else:
                    for y in range(7, 10):
                        parts[y][i] = (voicing[y-7]%12)+60
                        parts[10][i] = (parts[6][i][0]%12) + 48
                        lastchord[y-7] = voicing[y-7]
            else:
                for y in range(7, 12):
                    parts[y][i] = 0
        # LEAD
        if x % 8 == 0:
            silence = random.randint(0, 2) == 0
        if random.choice([1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]) and silence == 0:
            if lastparts[1][1] > 84:
                dir = -1
            elif lastparts[1][1] < 60:
                dir = 1
            if lastparts[1][1] > 90 or lastparts[1][1] < 50:
                lastparts[1][1] = lastparts[1][1]%24+60
            if lastparts[1][1] not in fullchord:
                chorddir = 0
            else:
                chorddir = int(dir/abs(dir))
            if lastparts[1][1] not in rootnotes:
                rootdir = 0
            else:
                rootdir = int(dir/abs(dir))
            if x % 2 == 0:
                parts[1][i] = movement(lastparts[1][1], fullchord, chorddir)
                lastparts[1][1] = parts[1][i]
            elif x % 2 == 1 and random.randint(0, 3) != 0:
                parts[1][i] = movement(lastparts[1][1], scale, dir)
                lastparts[1][1] = parts[1][i]
            elif random.randint(0, 4) == 0:
                parts[1][i] = lastparts[1][1]+dir
                lastparts[1][1] = parts[1][i]
            elif x%4 == 0:
                parts[1][i] = movement(lastparts[1][1], rootnotes, rootdir)
                lastparts[1][1] = parts[1][i]
                silence = 1
            else:
                parts[1][i] = movement(lastparts[1][1], rootnotes, rootdir)
                lastparts[1][1] = parts[1][i]
            if parts[1][i] != 0 and abs(lastparts[1][1]-parts[1][i]) > 2 and lastparts[1][1] < 84 and lastparts[1][1] > 60:
                dir = int(dir/abs(dir))*-1
    # Generate velocity list
    velocity = [random.randint(80, ((1-x%2)*10)+117) for i in range(length)]
    # Calculate the distance to the next note so we can determine the maximum duration of the note
    partdist = [lengthgenerator(parts[x]) for x in range(len(parts))]
    partdist[8:11] = [partdist[7] for i in range(4)]
    # Voice lists are made up of: [time in 16ths, note, velocity, length]
    # These will later be used for live midi playback or midi file output
    # In these lines we also apply the swing feel, velocity and semi-random duration of each note
    voices = [[[i+((i%2==1)*swing), x, velocity[i], random.randint((1-i%2), partdist[y][i]+(1-i%2))] for i, x in enumerate(parts[y])] for y in range(len(parts)) if y != 6]

def playseq():
    compose()
    quarterNoteDuration = 60 / bpm
    sixteenthNoteDuration =  quarterNoteDuration / 4.0
    beatsPerMeasure = meter
    measureDuration = beatsPerMeasure  * quarterNoteDuration
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(measureDuration, 2, playseq)
    for i in range(10):
        for x in range(len(voices[i])):
            if voices[i][x][1] != 0:
                duration = voices[i][x][3]
                scheduler.enter((voices[i][x][0]) * sixteenthNoteDuration, 1, makenote, (voices[i][x][1], i, 1, voices[i][x][2]))
                scheduler.enter((voices[i][x][0]+duration) * sixteenthNoteDuration, 3, makenote, (voices[i][x][1], i, 0, 0))
    scheduler.run()

# MIDI TOOLS
#Midi tool to do note-ons and note-offs
def makenote(note, i, type, velocity):
    action = [0x80, 0x90][type]
    if i == 0:
        midiout2.send_message([action, note, velocity])
    elif i >= 2 and i <= 5:
        midiout.send_message([action, note, velocity])
    elif i == 1:
        midiout4.send_message([action, note, velocity])
    elif i >= 7 and i <= 10:
        midiout3.send_message([action, note, velocity])

# Function for midi file saving and other actions
# This function is ran in a seperate thread
def midisaver():
    print("s = Save         n = New Sequence        q = Quit")
    while True:
        choice = input("> ")
        if choice == 's':
            oldvoices = list(voices)
            mf = MIDIFile(4)
            time = 0
            tracklist = [0, 1, 1, 1, 1, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]
            tracknames = ['Bass', 'Drums', 'Keys', 'Lead']
            for i in range(len(oldvoices)):
                track = tracklist[i]
                mf.addTrackName(track, 0, tracknames[track])
                mf.addTempo(track, 0, bpm)
                channel = 0
                for x in range(len(oldvoices[i])):
                    if oldvoices[i][x][1] != 0:
                        pitch = oldvoices[i][x][1]
                        volume = oldvoices[i][x][2]
                        time = oldvoices[i][x][0]/4  #convert from beats to sixteenths
                        if time+1 > 8:
                            duration = oldvoices[i][x][3]
                        else:
                            duration = random.choice([0.20, 0.40, 0.60, 0.80, 1])
                        mf.addNote(track, channel, pitch, time, duration, volume)
            filename = (input('Save As:') +  ".mid")
            with open(filename, 'wb') as outf:
                mf.writeFile(outf)
        if choice == 'q':
            thread.interrupt_main()
            sys.exit()
        if choice == 'n':
            measureCount = 1
            compose()

#           MUSICAL TOOLS

#Function to calculate musical intervals from midi pitch
#Outputs an array with [number, type] of interval
def interval(low, high):
    octdif = int((high-low)/12)*7
    intervals = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    qualities = ['p', 'min', 'maj', 'min', 'maj', 'p', 'aug', 'p', 'min', 'maj', 'min', 'maj', 'p']
    return [intervals[(high - low)%12]+octdif, qualities[(high - low)%12]]

# Spead midi notes over the full 0-127 note range
# Useful for walking up and down parts[6] and scales
def spreadNotes(notes):
    newnotes = []
    for i in notes:
        for j in range(-10, 10):
            if (i % 12) + (j * 12)  >= 0 and (i % 12) + (j * 12) <= 127:
                newnotes.append((i % 12) + (j * 12))
    newnotes.sort()
    return newnotes

# Make moves up and down from a note and latch them to a scale
# Distance 0 gives the lowest, closest number, 1 takes the first higher note, -1 the first lower note etc.
def movement(lastnote, scale, distance):
    return scale[min(range(len(scale)), key = lambda i: abs(scale[i]-lastnote))+distance]

# Makes a smooth chord change based on the previous chord
# Enter the new chord in first inversion, enter the old chord as played
def arrange(chord, lastchord):
    chord.sort()
    lastchord.sort()
    outerdistance = interval(lastchord[0], lastchord[2])[0]
    if outerdistance == 6 and chord != lastchord:
        options = [[12, 0, 0], [0, 0, -12], [0, 0, 0]]
    else:
        options = [[12, 0, 0], [0, 0, -12]]
    distlist = [0 for i in range(len(options))]
    for i in range(len(options)):
        for x in range(3):
            options[i][x] = options[i][x] + chord[x]
            if options[i][x] > 84 or options[i][x] < 60:
                distlist[i] + distlist[i] + 3
            distlist[i] = distlist[i] + abs(options[i][x] - lastchord[x])
    random.shuffle(options)
    bestchord = options[distlist.index(min(distlist))]
    bestchord.sort()
    return bestchord

def lastplayed(lst, index):
    matchlist = [index-i  if x != 0 and index-i>0 else 999 for i, x in enumerate(lst)]
    mindex = matchlist.index(min(matchlist))
    minval = lst[mindex]
    return [index-mindex, minval]

def lengthgenerator(list):
    distlist = [0 for x in range(len(list))]
    sum = 0
    list = list[::-1]
    for i in range(len(list)):
        if list[i] != 0:
            distlist[(len(list)-1)-i] = sum
            sum = 0
        else:
            sum = sum+1
    return distlist

thread.start_new_thread(midisaver, ())
playseq()
