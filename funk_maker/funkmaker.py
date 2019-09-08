## 1. Parts converteren naar drukheid per part (en totaal?) en adhdv parts de voller of leger maken bij zowel 1e als latere iteraties
## 2. Unison modus, mss meer modi voor variatie
## 3. Akkoorden buiten de key (negative harmony?): Zorg dat hij altijd een optie vindt dmv. movement ipv index
## 4. Sound design
## 5. CC's voor timbral changes etc.

import random, sys, time, sched, rtmidi, requests, json, re
import _thread as thread
from midiutil.MidiFile import MIDIFile
from HookTheory import HookTheory

# create HookTheory instance
ht = HookTheory('timothyschoen', 'tommypien')

# aquire authorization so get requests to the
# HookTheory API may be made
ht.getAuth()

#List to later store our Hooktheory progressions so we can prepare these progressions in advance
progressions = []

midiouts = [rtmidi.MidiOut() for i in range(5)]
tracknames = ['Bass', 'Lead', 'Drums', 'Keys', 'Chords']
for i in range(len(midiouts)):
    midiouts[i].open_virtual_port(tracknames[i])

# set bpm
bpm = int(input("Choose BPM \n >"))
swing = random.randint(15, 30)/bpm
measureCount = 0
key = 0
negative = 0
pause = 0


print("0: 4/4       1:5/4       2:7/8")
timesigchoice = input("Choose time signature: \n >")
if timesigchoice == '0':
    beatsPerMeasure = 8
    length = 32
    repeats = 4
    countlist = [i for i in range(length)]
elif timesigchoice == '1':
    beatsPerMeasure = 2.5
    repeats = 12
    countlist = [0, 1, 2, 1, 0, 1, 4, 1, 2, 1, 2, 1, 0, 1, 4, 1]
    length = 10
elif timesigchoice == '2':
    beatsPerMeasure = 3.5
    repeats = 8
    length = 14
    countlist = [i for i in range(length)]
else:
    print("selected 4/4")
    timesig = 8
    length = 32
    repeats = 4
    countlist = [i for i in range(length)]

parts = [[0 for i in range(length)] for x in range(5)]
lastparts = [[[0, key+60] for i in range(length)] for z in range(len(parts))]

def compose():
    global parts, lastparts, swing, voices, key, negative, scale, measureCount, bpm
    if measureCount % repeats == 0:
        measureCount = 0
        if random.randint(0, 1) == 0:
            bpm = random.randint(95, 120)
            swing = random.randint(15, 30)/bpm
        if random.randint(0, 1) == 0:
            key = abs(key + random.choice([-5, -2, 2, 7]))%12
        fill = 0
        mode = 1
        parts = [[0 for i in range(length)] for x in range(5)]
        parts[2] = [[0 for i in range(5)] for i in range(length)]
        parts[3] = [[0 for i in range(5)] for i in range(length)]
        print('Key:', ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C'][key%12])
        print('Tempo:', bpm, "bpm")
        print('>')
    elif measureCount % repeats == repeats-1:
        mode = 0
        fill = 1
    else:
        fill = 0
        mode = 0
    openhat = 0
    direction = 1
    dir = 1
    measureCount = measureCount + 1
    voices = [[0 for x in range(length)] for x in range(5)]
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale = spreadNotes(scale)
    scale = [(x+key) for x in scale]
    chordchoice = 2
    # TODO Use this rhythmlist to define accents
    # Adjust for 5/4 and 7/8
    rhythmlist = [random.randint((1-(i%2))*2, 4+(1-(i%2))*2) + (i%4==0)*2 for i in range(length)]
    progression = progressions.pop(0)
    for i in range(length):
        # These lines decide how full a measure is by looking at the amount of notes and the BPM (lots of notes on a high BPM sounds chaotic, few notes on low BPM sounds empty/boring)
        partsum = [sum([1 if (isinstance(note, int) and note != 0) or (isinstance(note, list) and sum(note) != 0) else 0 for note in part]) for part in parts]
        fullness = [int(sum*(pow(bpm/105, 4))) for sum in partsum]
        lastparts = [lastplayed(parts[z], i) for z in range(len(parts))]
        if lastparts[4][1] != 0:    #???
            lastparts[4][1].sort()
        x = countlist[i%len(countlist)]
        #Generate Chords in scale
        if (x%2 == 0 and random.randint(0, 2) == 0) or x == 0 and mode == 1:
            parts[4][i] = [note+60 for note in progression.pop(0)]
            change = 1
        elif x > 0 and mode == 1:
            parts[4][i] = parts[4][i-1]
            change = 0
        elif x > 0 and parts[4][i] != parts[4][i-1]:
            change = 1
        elif x == 0:
            change = 1
        else:
            change = 0
        rootnotes = spreadNotes([parts[4][i][0]])
        fullchord = spreadNotes(parts[4][i])
        # BASS
        if random.randint(0, 2) == 0 or mode == 1:
            if random.randint(0, 8-rhythmlist[i]) == 0 or x%8 == 0 and random.randint(0, 2) == 0 or x%16 == 0 or parts[2][i][0] == 36 and random.randint(0, 2) == 0:
                if lastparts[0][1] > 48:
                    direction = -1
                elif lastparts[0][1] < 36:
                    direction = 1
                if (x % 8 == 0 and random.randint(0, 1) == 0) or (change == 1 and random.randint(0,1) == 0):
                    parts[0][i] = movement(lastparts[0][1], rootnotes, 0)
                elif x % 2 == 0:
                    parts[0][i] = movement(lastparts[0][1], fullchord, direction)
                elif x % 2 == 1 and random.choice([0, 1]) == 0:
                    parts[0][i] = movement(lastparts[0][1], scale, direction)
                elif x % 8 == 0 and random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, (8*direction)), fullchord, 0)
                elif random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, [-4, 5, 5][direction+1]), fullchord, 0)
                elif random.randint(0, 1) == 0 and lengthgenerator(parts[0])[i] == 0:
                    parts[0][i] = lastparts[0][1]+direction
                else:
                    parts[0][i] = 0
                if parts[0][i] != 0 and abs(lastparts[0][1]-parts[0][i]) > 2:
                    direction = direction*-1
                if parts[0][i] != 0 and (parts[0][i] > 50 or parts[0][i] < 30):
                    parts[0][i] = parts[0][i]%24+36
            else:
                 parts[0][i] = 0
        # LEAD
        if i == 0:
            parts[1] = [0 for x in range(length)]
        if i % 8 == 0:
            silence = random.randint(0, 5) == 0
        if random.randint(0, 8-rhythmlist[i]) > 1 and silence == 0:
            if dir != -1 and dir != 1:
                dir = 1
            if lastparts[1][1] > 84:
                dir = -1
            elif lastparts[1][1] < 60:
                dir = 1
            if (lastparts[1][1] > 100 or lastparts[1][1] < 48) and lastparts[1][1] != 0:
                lastparts[1][1] = lastparts[1][1]%12+60
            if x % 2 == 0:
                parts[1][i] = movement(lastparts[1][1], fullchord, dir)
            elif x % 2 == 1 and random.randint(0, 3) != 0:
                parts[1][i] = movement(lastparts[1][1], scale, dir)
            elif random.randint(0, 2) == 0 and lengthgenerator(parts[0])[i] == 0:
                parts[1][i] = lastparts[1][1]+dir
            elif x%2 == 0 and random.randint(0, 3) == 0:
                parts[1][i] = movement(lastparts[1][1], rootnotes, 0)
                silence = random.randint(0, 1) == 0
            if lastparts[1][1] == parts[1][i] and random.randint(0, 1) == 0:
                parts[1][i] = 0
            if parts[1][i] != 0 and abs(lastparts[1][1]-parts[1][i]) > 2 and lastparts[1][1] < 84 and lastparts[1][1] > 60:
                dir = int(dir/abs(dir))*-1
        # DRUMS
        # kick
        if mode == 1 or random.randint(0, 4) == 0:
            if x % 8 == 0 and random.randint(0, 3) != 0 or x%16 == 0 or random.randint(0, (1-(x%2))+5) == 0 or parts[0][i] != 0 and random.randint(0, 2) == 0:
                parts[2][i][0] = 36
            else:
                parts[2][i][0] = 0
            if x >= 4 and (parts[2][i-1][0]+parts[2][i-2][0]+parts[2][i-3][0]+parts[2][i-4][0]) > 72:
                parts[2][i][0] = 0
        # Snare
        if random.randint(0, 2) == 0 or mode == 1:
            if x % 8 == 4 or random.randint(0, (x%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or parts[2][i][1] > 0 and random.randint(0, 1+abs(0-i)%4) == 2:
                parts[2][i][1] = 38
            else:
                parts[2][i][1] = 0
        # Hats
        if openhat == 1:
            parts[2][i][2] = 44
            openhat = 0
        elif random.randint(0, 1) == 0 or mode == 1:
            if random.randint(0, 7+(x%2)*5) == 0:
                openhat = 1
                parts[2][i][2] = 46
            elif parts[2][i][0] == 0 and parts[2][i][1] == 0 and random.randint(0, 1) == 0:
                parts[2][i][2] = 42
            else:
                parts[2][i][2] = 0
        # Toms, snares and cymbals for fills
        if fill == 1 and x > 16 and random.randint(0, 3) != 0:
            fillchoice = random.randint(0, 8)+(i-16)
            note = [47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38, 47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38][fillchoice]
            parts[2][i][3] = note
        if mode == 1:
            parts[2][0][3] = random.choice([49, 50])
        else:
            parts[2][0][3] = 0
        # KEYS
        if mode == 1 or random.randint(0, 2) == 0 and i != length:
            if random.choice([1, 1, 1, 1, x%2==1, x%2==1, x%4==2, x%4==2, x%2==0, parts[0][i] != 0, parts[0][i] != 0, change, change, change, 0, 0, 0, 0, 0, 0]) == 1 or x%8 == 0:
                voicing = arrange(parts[4][i], lastparts[3][1][0:3], scale)
                if random.randrange(0, 2) == 0:
                    parts[3][i] = voicing
                    parts[3][i].append(parts[3][i][0]-12)
                    parts[3][i].append(parts[3][i][3])
                elif lengthgenerator(parts[3])[i] == 0 and mode != 1 and i != length-1:
                    chromatic = random.choice([-1, 1])
                    parts[3][i] = [z+chromatic for z in parts[3][i+1]]
                else:
                    parts[3][i] = [(voicing[y]%12)+60 for y in range(len(voicing))]
                    parts[3][i].append((parts[3][i][0]%12)+48)
            else:
                parts[3][i] = []
    # Generate velocity list
    velocity = [random.randint(80, ((1-x%2)*20)+97) for i in range(length)]
    # Calculate the distance to the next note so we can determine the maximum duration of the note
    partdist = [lengthgenerator(parts[x]) for x in range(len(parts))]
    # Voice lists are made up of: [time in 16ths, note, velocity, length]
    # These will later be used for live midi playback or midi file output
    # In these lines we also apply the swing feel, velocity and semi-random duration of each note
    voices = [[[i+((i%2)*swing), x, velocity[i]+random.randint(-5, 5), random.randint(((partdist[y][i]-2)+(1-i%2))+1, partdist[y][i]+1+(1-i%2))] for i, x in enumerate(parts[y])] for y in range(len(parts))]

#       PLAYBACK TOOLS

def playseq():
    global scheduler
    compose()
    # Define note and measure lengths
    quarterNoteDuration = 60 / bpm
    sixteenthNoteDuration =  quarterNoteDuration / 4.0
    measureDuration = beatsPerMeasure  * quarterNoteDuration
    # Set up scheduler
    scheduler = sched.scheduler(time.time, pausesleep)
    # Schedule a repeat at measureDuration
    scheduler.enter(measureDuration, 2, playseq)
    for i in range(5):
        for x in range(len(voices[i])):
            if voices[i][x][1] != 0:
                duration = voices[i][x][3]
                scheduler.enter((voices[i][x][0]) * sixteenthNoteDuration, 1, makenote, (voices[i][x][1], i, 1, voices[i][x][2]))
                scheduler.enter((voices[i][x][0]+duration) * sixteenthNoteDuration, 3, makenote, (voices[i][x][1], i, 0, 0))
    scheduler.run()

def pausesleep(arg):
    global pause
    while pause == 1:
        time.sleep(1)
    time.sleep(arg)

# MIDI TOOLS
#Midi tool to do note-ons and note-offs
# i is the Midi output it will be routed to, type can be 0 or 1 for note-off or note-on
# If takes both lists of notes (arrays) and single notes (ints)
def makenote(notes, i, type, velocity):
    action = [0x80, 0x90][type]
    if isinstance(notes, int):
        notes = [notes]
    for note in notes:
        if note > 0:
                midiouts[i].send_message([action, note, velocity])

# Function for midi file saving and other actions
# This function is ran in a seperate thread
def midisaver():
    global pause, measureCount, bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist
    print("s = Save         n = New Sequence        q = Quit            p=Pause/Play")
    while True:
        choice = input("> ")
        if choice == 's':
            oldvoices = list(voices)
            mf = MIDIFile(len(parts), deinterleave=False)
            time = 0
            for i in range(len(parts)):
                mf.addTrackName(i, 0, tracknames[i])
                mf.addTempo(i, 0, bpm)
                channel = 0
                for x in range(len(oldvoices[i])):
                    if isinstance(oldvoices[i][x][1], int):
                        oldvoices[i][x][1] = [oldvoices[i][x][1]]
                    for pitch in oldvoices[i][x][1]:
                        if pitch != 0:
                            volume = oldvoices[i][x][2]
                            time = oldvoices[i][x][0]/4  #convert from beats to sixteenths
                            if time+1 < 8:
                                duration = oldvoices[i][x][3]/4
                            else:
                                duration = 0.1
                            mf.addNote(i, channel, pitch, time, duration, volume)
            filename = (input('Save As:') +  ".mid")
            with open(filename, 'wb') as outf:
                mf.writeFile(outf)
        if choice == 'q':
            thread.interrupt_main()
            sys.exit()
        if choice == 'n':
            measureCount = 0
            bpm = int(input("Choose BPM \n >"))
            timesigchoice = input("Choose time signature: \n >")
            if timesigchoice == '0':
                beatsPerMeasure = 8
                length = 32
                repeats = 4
                countlist = [i for i in range(length)]
            elif timesigchoice == '1':
                beatsPerMeasure = 2.5
                repeats = 12
                countlist = [0, 1, 2, 1, 0, 1, 4, 1, 2, 1, 2, 1, 0, 1, 4, 1]
                length = 10
            elif timesigchoice == '2':
                beatsPerMeasure = 3.5
                repeats = 8
                length = 14
                countlist = [i for i in range(length)]
            else:
                print("selected 4/4")
                timesig = 8
                length = 32
                repeats = 4
                countlist = [i for i in range(length)]
            scheduler.enter(0, 2, playseq)
            for i in scheduler.queue:
                if i[2] != playseq:
                    scheduler.cancel(i)
        if choice == 'p':
            print('Paused, press p to start playing')
            pause = 1-pause
            compose()

#           MUSICAL TOOLS

#Function to calculate musical intervals from midi pitch
#Outputs an array with [number, type] of interval (for example, [6, 'min'] for a minor 6th)
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
# Optionally add some extentions
def arrange(chord, lastchord, scale):
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
    extlst = [[6, 7, 9, 11], [7, 9], [7], [6, 7], [7, 9, 11, 13], [7, 9], [7]][interval(scale[0], chord[0])[0]%7]
    extentionchoice = random.sample(set(extlst), random.randint(1, len(extlst)))
    extended = bestchord + [movement(chord[0], scale, i) for i in extentionchoice]
    extended.sort()
    return extended

def lastplayed(lst, index):
    matchlist = [index-i if (isinstance(x, int) and x != 0 or isinstance(x, list) and sum(x) != 0) and index-i>0 else 999 for i, x in enumerate(lst)]
    mindex = matchlist.index(min(matchlist))
    minval = lst[mindex]
    return [index-mindex, minval]

def lengthgenerator(lst):
    distlist = [0 for x in range(len(lst))]
    totalsum = 0
    lst = lst[::-1]
    for i in range(len(lst)):
        if isinstance(lst[i], list):
            lst[i] = sum(lst[i])
        if lst[i] != 0:
            distlist[(len(lst)-1)-i] = totalsum
            totalsum = 0
        else:
            totalsum = totalsum+1
    return distlist

def makenegative(lst, scale, key):
    return [[7, 5, 3, 2, 0, 10, 8][scale.index(x%12)]+(int(x/12)*12) for x in lst]


# We use the HookTheory API to generate chords for us based on a database of over 5000 song chords

def HookTheoryGet():
    global progressions
    while True:
        if len(progressions) < 4:
            chordIDs = str(random.randint(1, 6))
            progression = [0 for x in range(4)]
            progression[0] = translatechord(chordIDs[0])
            for x in range(1, 4):
                receivedchord = ht.getChords(chordIDs).json()
                options = [[]  for i in range(len(receivedchord))]
                chordprob = random.randint(0, 1000000000000000)/1000000000000000
                for i in range(len(options)):
                    if i != 0:
                        options[i] = [[options[i-1][0][1], receivedchord[i]['probability']+options[i-1][0][1]], receivedchord[i]['chord_ID']]
                    else:
                        options[i] = [[0, receivedchord[i]['probability']], receivedchord[i]['chord_ID']]
                    if chordprob >= options[i][0][0] and chordprob <= options[i][0][1]:
                        chord = options[i][1]
                chordIDs = chordIDs + "," + chord
                progression[x] = translatechord(chord)
                print(chordIDs)
            progressions.append(progression)

def translatechord(chrd):
    inversions = {"0" : [0, 2, 4], "6" : [2, 4, 0], "64" : [4, 0, 2], "7" : [0, 2, 4, 6], "65" : [2, 4, 6, 0], "43" : [4, 6, 0, 2], "42" : [6, 0, 2, 4]}
    chord = chrd.split('/')
    if chord[0][0].isalpha():
        mode = ['', 'D','Y','L','M','b','C'].index(chord[0][0])
        degree = chord[0][1]
        if len(chord[0]) > 3 and chord[0][2:4] in ['65', '43', '42', '64']:
            inversion = inversions[chord[0][2:4]]
        elif len(chord[0]) > 2 and chord[0][2] in ['7','6']:
            inversion = inversions[chord[0][2]]
        else:
            inversion = inversions["0"]
    else:
        mode = 0
        degree = chord[0][0]
        if len(chord[0]) > 2 and chord[0][1:3] in ['65', '43', '42', '64']:
            inversion = inversions[chord[0][1:3]]
        elif len(chord[0]) > 1 and chord[0][1] in ['7','6']:
            inversion = inversions[chord[0][1]]
        else:
            inversion = inversions["0"]
    if len(chord) > 1 and len(chord[1]) > 0:
        extention = chord[1][0]
    else:
        extention = 0
    scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]
    smode = scale[mode]
    scale = [(x-smode) for x in scale]
    finalchord = [(scale[(int(degree)-1+mode+int(i))%14]+scale[int(extention)-1])%24 for i in inversion]
    return finalchord

#thread.start_new_thread(HookTheoryGet, ())
#thread.start_new_thread(midisaver, ())

if __name__ == '__main__':
    while len(progressions) < 4:
        print('Waiting for HookTheory...')
        time.sleep(2)
#playseq()
