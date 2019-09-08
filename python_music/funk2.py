## TODO:
## 1. Verschillende maatsoorten (4/5 en 7/8, met verschillende subdivisions)
##  Misschien:
## 1. Parts balancen aan de hand van hoe vol de afgelopen 8x16e waren ofzo
## 2. Unison modus, mss meer modi voor variatie
## 3. Meer verschil in chord progressions en extentions etc.

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
basslist = [0 for x in range(32)]
leadlist = [0 for x in range(32)]
kicklist = [0 for x in range(32)]
snarelist = [0 for x in range(32)]
filllist = [0 for x in range(32)]
hatlist = [0 for x in range(32)]
chords = [0 for x in range(32)]
keys = [[0 for x in range(32)] for x in range(0, 5)]
lastlead = key+60

def compose():
    global basslist, leadlist, snarelist, kicklist, hatlist, filllist, keys, chords, swing, voices, key, scale, lastlead, measureCount, bpm
    if measureCount % 5 == 0:
        measureCount = 1
        if random.randint(0, 1) == 0:
            bpm = random.randint(85, 120)
        if random.randint(0, 2) == 0:
            key = abs(key + random.choice([-5, -2, 2, 7]))%12
        lastlead = key+60
        fill = 0
        mode = 1
        basslist = [0 for x in range(32)]
        kicklist = [0 for x in range(32)]
        snarelist = [0 for x in range(32)]
        hatlist = [0 for x in range(32)]
        chords = [0 for x in range(32)]
        keys = [[0 for x in range(32)] for x in range(0, 5)]
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
    lastbass = 48
    lastchord = [60, 64, 67]
    direction = 1
    dir = 1
    openhat = 0
    voices = [[0 for x in range(32)] for x in range(0, 11)]
    filllist = [0 for x in range(32)]
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale = spreadNotes(scale)
    scale = [(x+key) for x in scale]
    leadlist = [0 for x in range(32)]
    for i in range(32):
        if  i == 0 and mode == 1:
            scalepos = scale[random.randint(0, 5)]
            chords[i] = [movement(scalepos+60, scale, 0), movement(scalepos+60, scale, 2), movement(scalepos+60, scale, 4), movement(scalepos+60, scale, 6)]
            change = 1
        elif (i%4 == 0 and random.randint(0, 2) == 0) and mode == 1:
            scalepos = scale[random.randint(0, 5)]
            chords[i] = [movement(scalepos+60, scale, 0), movement(scalepos+60, scale, 2), movement(scalepos+60, scale, 4), movement(scalepos+60, scale, 6)]
            change = 1
        elif i > 0 and mode == 1:
            chords[i] = chords[i-1]
            change = 0
        elif i > 0 and chords[i] != chords[i-1]:
            change = 1
        elif i == 0:
            change = 1
        else:
            change = 0
        rootnote = chords[i][0]
        rootnotes = spreadNotes([chords[i][0]])
        fullchord = spreadNotes(chords[i])
        if i%8 == 0:
            emphasis = random.choice([0, 1])
        if random.randint(0, 1) == 0  and i%2 == 1 or mode == 1:
            if random.choice([1, 1, basslist[i-1]==0, basslist[i-1]==0, basslist[i-1]==0, basslist[i-1]==0, change, change, i%2==0, i%2==0, i%2==0, i%2==0, i%2==emphasis, i%2==emphasis, i%4==0, i%4==0, i%2==0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) == 1 or i%8 == 0 and random.randint(0, 3) == 0 or i%16 == 0:
                if lastbass > 48:
                    direction = -1
                elif lastbass < 36:
                    direction = 1
                if i % 8 == 0 or (change == 1 and random.randint(0,2) == 0):
                    basslist[i] = movement(lastbass, rootnotes, 0)
                elif i % 2 == 0:
                    basslist[i] = movement(lastbass, fullchord, direction)
                elif i % 2 == 1 and random.choice([0, 1]) == 0:
                    basslist[i] = movement(lastbass, scale, direction)
                elif random.randint(0, 1) == 0:
                    basslist[i] = movement(movement(lastbass, scale, (8*direction)), fullchord, 0)
                elif random.randint(0, 1) == 0:
                    basslist[i] = movement(movement(lastbass, scale, [-4, 5, 5][direction+1]), fullchord, 0)
                elif random.randint(0, 1) == 0:
                    basslist[i] = lastbass+direction
                else:
                    basslist[i] = 0
                if basslist[i] != 0 and abs(lastbass-basslist[i]) > 2:
                    direction = direction*-1
                basslist[i] = basslist[i]%24+36
        if i == 0  or basslist[i] != basslist[i-1] or mode == 1 and basslist[i] != 0:
            basschange = 1
        else:
            basschange = 0
        lastbass = int(basslist[i])
        if mode == 1 or random.randint(0, 4) == 0:
            if i % 8 == 0 and random.randint(0, 2) == 1 or i%16 == 0 or random.randint(0, (i%2)+2) == 0 and random.randint(0, [3, 9, 15, 6][(i+emphasis)%4]) == 0 or basschange == 1 and random.randint(0, 2) == 0:
                kicklist[i] = 36
            else:
                kicklist[i] = 0
            if i >= 4 and (kicklist[i-1]+kicklist[i-2]+kicklist[i-3]+kicklist[i-4]) > 72:
                kicklist[i] = 0
        if random.randint(0, 2) == 0 or mode == 1:
            if i % 8 == 4 or random.randint(0, (i%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or keys[0][i] > 0 and random.randint(0, 1+abs(0-i)%4) == 2:
                snarelist[i] = 38
            else:
                snarelist[i] = 0
        if openhat == 1:
            hatlist[i] = 44
            openhat = 0
        elif random.randint(0, 1) == 0 or mode == 1:
            if random.randint(0, 7+(i%2)*5) == 0:
                openhat = 1
                hatlist[i] = 46
            elif kicklist[i] == 0 and snarelist[i] == 0 and random.randint(0, 2) == 0:
                hatlist[i] = 42
            else:
                hatlist[i] = 0
        if fill == 1 and i > 16 and random.randint(0, 3) != 0:
            fillchoice = random.randint(0, 8)+(i-16)
            note = [47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38][fillchoice]
            filllist[i] = note
        if mode == 1:
            filllist[0] = random.choice([49, 50])
        if mode == 1 or random.randint(0, 2) == 0:
            if random.choice([1, 1, 1, 1, i%2==1, i%2==1, i%2==emphasis, i%2==emphasis, i%4==2, i%4==2, i%2==0, basschange, basschange, change, change, change, 0, 0, 0, 0, 0, 0]) == 1 or i%8 == 0:
                voicing = arrange(chords[i], lastchord)
                if random.randrange(0, 2) != 0:
                    for y in range(3):
                        keys[y][i] = voicing[y]
                        lastchord[y] = voicing[y]
                    keys[3][i] = chords[i][0]-12
                    keys[4][i] = chords[i][3]
                else:
                    for y in range(3):
                        keys[y][i] = (voicing[y]%12)+60
                        keys[3][i] = (chords[i][0]%12) + 48
                        lastchord[y] = voicing[y]
            else:
                for y in range(5):
                    keys[y][i] = 0
        if i % 8 == 0:
            silence = random.randint(0, 2) == 0
        if random.choice([1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]) and silence == 0:
            if lastlead > 84:
                dir = -1
            elif lastlead < 60:
                dir = 1
            if lastlead not in fullchord:
                chorddir = 0
            else:
                chorddir = int(dir/abs(dir))
            if lastlead not in rootnotes:
                rootdir = 0
            else:
                rootdir = int(dir/abs(dir))
            if i % 2 == 0:
                leadlist[i] = movement(lastlead, fullchord, chorddir)
                lastlead = leadlist[i]
            elif i % 2 == 1 and random.randint(0, 3) != 0:
                leadlist[i] = movement(lastlead, scale, dir)
                lastlead = leadlist[i]
            elif random.randint(0, 4) == 0:
                leadlist[i] = lastlead+dir
                lastlead = leadlist[i]
            elif i%4 == 0:
                leadlist[i] = movement(lastlead, rootnotes, rootdir)
                lastlead = leadlist[i]
                silence = 1
            else:
                leadlist[i] = movement(lastlead, rootnotes, rootdir)
                lastlead = leadlist[i]
            #if leadlist[i] == lastlead and random.randint(0, 2) != 0:
            #    leadlist[i] = 0
            if leadlist[i] != 0 and abs(lastlead-leadlist[i]) > 2 and lastlead < 84 and lastlead > 60:
                dir = int(dir/abs(dir))*-1
    # Generate velocity list
    velocity = [random.randint(80, ((1-i%2)*10)+117) for i in range(32)]
    # Calculate the distance to the next note so we can determine the maximum duration of the note
    keydist = lengthgenerator(keys[1])
    leaddist = lengthgenerator(leadlist)
    bassdist = lengthgenerator(basslist)
    # Voice lists are made up of: [time in 16ths, note, velocity, length]
    # These will later be used for live midi playback or midi file output
    # In these lines we also apply the swing feel, velocity and semi-random duration of each note
    for y in range(5):
        voices[y+6] = list([i+((i%2==1)*swing)+random.choice([-0.02, 0.02, 0.05, -0.05]), x, velocity[i], random.randint(0, keydist[i]+(1-i%2))] for i, x in enumerate(keys[y]))
    voices[0] = list([i+((i%2==1)*swing), x, velocity[i], random.randint((1-i%2), bassdist[i]+(1-i%2))] for i, x in enumerate(basslist))
    voices[1] = list([i+((i%2==1)*swing), x, velocity[i], 1] for i, x in enumerate(kicklist))
    voices[2] = list([i+((i%2==1)*swing), x, velocity[i], 1] for i, x in enumerate(snarelist))
    voices[3] = list([i+((i%2==1)*swing), x, velocity[i], 1] for i, x in enumerate(hatlist))
    voices[4] = list([i+((i%2==1)*swing), x, velocity[i], 1] for i, x in enumerate(filllist))
    voices[5] = list([i+((i%2==1)*swing), x, velocity[i], random.randint(1, leaddist[i]+1)] for i, x in enumerate(leadlist))

def playseq():
    compose()
    quarterNoteDuration = 60 / bpm
    sixteenthNoteDuration =  (60 / bpm) / 4.0
    beatsPerMeasure = 4
    measureDuration = beatsPerMeasure  * quarterNoteDuration*2
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(measureDuration, 2, playseq)
    for i in range(10):
        for x in range(len(voices[i])):
            if voices[i][x][1] != 0:
                length = voices[i][x][3]
                scheduler.enter((voices[i][x][0]) * sixteenthNoteDuration, 1, makenote, (voices[i][x][1], i, 1, voices[i][x][2]))
                scheduler.enter((voices[i][x][0]+length) * sixteenthNoteDuration, 3, makenote, (voices[i][x][1], i, 0, 0))
    scheduler.run()

# MIDI TOOLS
#Midi tool to do note-ons and note-offs
def makenote(note, i, type, velocity):
    action = [0x80, 0x90][type]
    if i == 0:
        midiout2.send_message([action, note, velocity])
    elif i >= 1 and i <= 4:
        midiout.send_message([action, note, velocity])
    elif i == 5:
        midiout4.send_message([action, note, velocity])
    elif i >= 6 and i <= 10:
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
# Useful for walking up and down chords and scales
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

def lengthgenerator(list):
    distlist = [0 for x in range(32)]
    sum = 0
    list = list[::-1]
    for i in range(len(list)):
        if list[i] != 0:
            distlist[31-i] = sum
            sum = 0
        else:
            sum = sum+1
    return distlist

thread.start_new_thread(midisaver, ())
playseq()
