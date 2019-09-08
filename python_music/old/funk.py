import random
import itertools
import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
midiout.open_virtual_port("Drums")

midiout2 = rtmidi.MidiOut()
available_ports = midiout2.get_ports()
midiout2.open_virtual_port("Bass")

midiout3 = rtmidi.MidiOut()
available_ports = midiout3.get_ports()
midiout3.open_virtual_port("Keys")
# set bpm
bpm = 110
# calculate the duration of a quarter note
quarterNoteDuration = 60 / bpm
# calculate the duration of a sixteenth note
sixteenthNoteDuration = quarterNoteDuration / 4.0
# number of beats per sequence (time signature: 3 / 4 = 3 beats per sequence)
beatsPerMeasure = 4
measureCount = 0
# calculate the duration of a measure
measureDuration = beatsPerMeasure  * quarterNoteDuration*2
events = []
noteoffs = []

chordprogression = []
key = 0
scale = [0, 2, 4, 5, 7, 9, 11]

voices = [[] for x in range(8)]

def compose():
    global voices
    voices = [[] for x in range(8)]
    lastplayed = [48, 0, 0, 0, 60, 64, 67, 71, 72]
    direction = 1
    openhat = 0
    scale = []
    scale = [(x+key)%12 for x in scale]
    scale = spreadNotes(scale)
    chordlist = [1, 6, 4, 2, 5, 3]
    random.shuffle(chordlist)
    chordprogression = []
    basslist = [0 for x in range(32)]
    kicklist = [0 for x in range(32)]
    snarelist = [0 for x in range(32)]
    hatlist = [0 for x in range(32)]
    rootnotes = [0 for x in range(32)]
    for y in range(4, 8):
        voices[y] = [0 for x in range(32)]
    print(progression)
    for x in range(32):
        if i%4 == 0 and random.randint(0, 3) == 0:
            scalepos = scale[random.randint(0, 5)]
            if progression[i] == 1 or progression[i] == 4:
                chord = [scalepos+60, scalepos+64, scalepos+67, scalepos+71]
            elif progression[i] == 5:
                chord = [scalepos, scalepos+4, scalepos+7, scalepos+10]
            elif progression[i] == 2 or progression[i] == 3 or progression[i] == 6:
                chord = [scalepos, scalepos+3, scalepos+7, scalepos+10]
            else:
                chord = [scalepos, scalepos+3, scalepos+6, scalepos+10]
    for i in range(32):
        if i%8 == 0:
            emphasis = random.choice([0, 1])
        chord = chordprogression[i]
        if i != 0 and chordprogression[i-1] != chord:
            change = 1
        else:
            change = 0
        if random.choice([1, 1, 1, 1, 1, change, change, i%2==0, i%2==0, i%2==emphasis, i%2==emphasis, i%4==0, i%4==0, i%2==0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) == 1 or i%8 == 0 and random.randint(0, 3) == 0 or i%16 == 0:
            basschange = 1
            if lastplayed[0] > 48:
                direction = -1
            elif lastplayed[0] < 36:
                direction = 1
            if i % 8 == 0 or (change == 1 and random.randint(0,2) == 0):
                basslist[i] = movement(lastplayed[0], rootnotes[i], 0)
            elif i % 2 == 0:
                basslist[i] = movement(lastplayed[0], chord, direction)
            elif i % 4 == 1 or i % 4 == 3 and random.choice([0, 1]) == 0:
                basslist[i] = movement(lastplayed[0], scale, direction)
            elif random.randint(0, 1) == 0:
                basslist[i] = movement(movement(lastplayed[0], scale, (8*direction)), chord, 0)
            elif random.randint(0, 1) == 0:
                basslist[i] = movement(movement(lastplayed[0], scale, [-4, 5, 5][direction+1]), chord, 0)
            elif random.randint(0, 1) == 0:
                basslist[i] = lastplayed[0]+direction
            if basslist[i] != 0 and abs(lastplayed[0]-basslist[i]) > 2:
                direction = direction*-1
            basslist[i] = basslist[i]%24+36
            if basslist[i] == lastplayed[0] and random.randint(0, 2) != 0:
                basslist[i] = 0
            lastplayed[0] = int(basslist[i])
        else:
            basschange = 0
        if i%8 == 0 and random.randint(0, 2) == 1 or i%16 == 0:
            kicklist[i] = 36
        if i%8 == 4:
            snarelist[i] = 38
        if random.randint(0, (i%2)+2) == 0 and random.randint(0, [3, 9, 15, 6][(i+emphasis)%4]) == 0 or basschange == 1 and random.randint(0, 2) != 0:
            kicklist[i] = 36
        if random.randint(0, (i%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or change == 1 and random.randint(0, 1+abs(0-i)%4) == 2:
            snarelist[i] = 38
        if random.randint(0, 7+(i%2)*5) == 0:
            openhat = 1
            hatlist[i] = 46
        elif kicklist[i] == 0 and snarelist[i] == 0 and random.randint(0, 2) != 0:
            hatlist[i] = 42
        if openhat == 1:
            hatlist[i] = 44
            openhat = 0
        if random.choice([1, 1, 0, i%2==0, i%2==0, i%2==emphasis, i%2==emphasis, i%4==0, i%4==0, i%2==0, basschange, basschange, change, change, change, 0, 0, 0, 0, 0, 0]) == 1:
            for y in range(4, 8):
                newnote = movement(lastplayed[y], chord, [0, 0, 0, 0, 0, 1, 2, 3, 4][y])
                lastplayed[y] = newnote%12+60
                voices[y][i] = newnote
    for y in range(4, 8):
        voices[y] = list([i+((i%2==1)*0.23), x] for i, x in enumerate(voices[y]))
    voices[0] = list([i+((i%2==1)*0.23), x] for i, x in enumerate(basslist))
    voices[1] = list([i+((i%2==1)*0.23), x] for i, x in enumerate(kicklist))
    voices[2] = list([i+((i%2==1)*0.23), x] for i, x in enumerate(snarelist))
    voices[3] = list([i+((i%2==1)*0.23), x] for i, x in enumerate(hatlist))

def playseq():
    global measureCount
    if measureCount % 5 == 0:
        measureCount = 1
        compose()
    measureCount = measureCount + 1
    for i in range(8):
        for x in range(len(voices[i])):
            if voices[i][x][1] != 0:
                length = (1-(int(voices[i][x][0])%2))+1
                events.append([voices[i][x][0] * sixteenthNoteDuration, i, voices[i][x][1]])
                noteoffs.append([(voices[i][x][0]+length) * sixteenthNoteDuration, i, voices[i][x][1]])
    # transform the sixteenthNoteSequece to an eventlist with time values
    events.sort()
    noteoffs.sort()
    velocity = 100
    event = events.pop(0)
    noteoff = noteoffs.pop(0)
    # retrieve the startime: current time
    startTime = time.time()
    keepPlaying = True
    lastnotes = [0 for i in range(8)]
    # play the sequence
    while keepPlaying:
      # retrieve current time
      currentTime = time.time()
      # check if the event's time (which is at index 0 of event) is passed
      if(currentTime - startTime >= event[0]):
        for i in range(8):
            if event[1] == i:
                time.sleep(0.001)
                if velocity > 107:
                    velocity = velocity + random.randint(-3, 0)
                elif velocity < 90:
                    velocity = velocity + random.randint(0, 2)
                else:
                    velocity = velocity + random.randint(-2, 2)
                if i == 0 and event[2] != 0:
                    midiout2.send_message([0x80, lastnotes[i], 0])
                    midiout2.send_message([0x90, event[2], velocity+random.randint(0, 20)])
                elif i >= 4 and i <= 8 and event[2] != 0:
                    midiout3.send_message([0x80, lastnotes[i], 0])
                    midiout3.send_message([0x90, event[2], velocity+random.randint(0, 10)])
                elif event[2] != 0:
                    midiout.send_message([0x80, lastnotes[i], 0])
                    midiout.send_message([0x90, event[2], velocity+random.randint(0, 20)])
                lastnotes[i] = event[2]
        if(currentTime - startTime >= noteoff[0]):
            for i in range(8):
                if noteoff[1] == i:
                    if noteoff[1] == 0 and noteoff[2] != 0:
                        midiout2.send_message([0x90, noteoff[2], 0])
                    elif noteoff[1] >= 4 and noteoff[1] <= 8 and noteoff[2] != 0:
                        midiout3.send_message([0x90, noteoff[2], 0])
                    elif noteoff[2] != 0:
                        midiout.send_message([0x90, noteoff[2], 0])
            noteoff = noteoffs.pop(0)

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
            playseq()
        else:
            time.sleep(0.001)

## TODO: functie die inversies en mooie voicings maakt

def interval(low, high):
    octdif = int((high-low)/12)*7
    intervals = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    qualities = ['p', 'min', 'maj', 'min', 'maj', 'p', 'aug', 'p', 'min', 'maj', 'min', 'maj', 'p']
    return [intervals[(high - low)%12]+octdif, qualities[(high - low)%12]]

def spreadNotes(notes):
    newnotes = []
    for i in notes:
        for j in range(-10, 10):
            if (i % 12) + (j * 12)  >= 0 and (i % 12) + (j * 12) <= 127:
                newnotes.append((i % 12) + (j * 12))
    newnotes.sort()
    return newnotes

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

def movement(lastnote, scale, distance):
    return scale[min(range(len(scale)), key = lambda i: abs(scale[i]-lastnote))+distance]

def arrange(chord, rootnote, lastchord, lastroot):
    chord = spreadNotes(chord)
    lastchord = spreadNotes(lastchord)
    rootindex = chord.index(rootnote)
    fullchord = [rootnote, chord[rootindex+1], chord[rootindex+2]]
    outerdistance = interval(lastroot, lastchord[lastchord.index(lastroot)+2])[0]
    print(outerdistance)
    if outerdistance == 6:
        options = [[12, 0, 0], [0, 0, -12], [0, 0, 0]]
    else:
        options = [[12, 0, 0], [0, 0, -12]]
    print(options)


playseq()
