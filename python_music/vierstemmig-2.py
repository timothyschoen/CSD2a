import time
import random
import rtmidi
from collections import Counter

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
midiout.open_virtual_port("My virtual output")
# set bpm
bpm = 120
# calculate the duration of a quarter note
quarterNoteDuration = 240 / bpm
# calculate the duration of a sixteenth note
sixteenthNoteDuration = quarterNoteDuration / 4.0
# number of beats per sequence (time signature: 3 / 4 = 3 beats per sequence)
beatsPerMeasure = 4
measureCount = 0
# calculate the duration of a measure
measureDuration = beatsPerMeasure  * quarterNoteDuration
cadence = 10
lastmoves = [[0, 0, 0, 0]]
events = []
lastnotes = [[60, 60, 60, 72], [60, 60, 60, 60], [60, 60, 60, 60], [60, 60, 60, 60], [60, 60, 60, 60], [60, 60, 60, 60], [60, 60, 60, 60], [60, 60, 60, 60]]
choice = [0, 0, 0, 0]
key = 0

def composer():
    global key
    global choice
    global lastnotes
    global lastmoves
    global cadence
    global voices
    voices = [[] for x in range(4)]
    for seq in range(16):
        if cadence >= 21:
            cadence = cadence-1
            choices = lastnotes[0]
            continue
        scale = [0,2,4,5,7,9,11]
        scale = [(x+key)%12 for x in scale]
        scale = spreadNotes(scale)
        # List of possibilities by interval, based on counterpoint
        counterpoint = [[[-1, 1]], [[lastmoves[0][3], lastmoves[0][1]]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, 1], [1, 1], [-1, -1]], [[0, 1], [1, 0], [-1, 0], [0, 1], [-1, 1], [-2, 0], [0, 2]], [[1, 0], [-1, 0], [0, -1], [1, -1], [-1, 0], [2, 0], [0, -2]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [1, 1], [1, -1]], [[lastmoves[0][3], lastmoves[0][1]]], [[1, -1]]]
        middlevoice = [[5], [4, 5, 6], [4, 5, 6, 7], [2, 3, 5, 6, 7], [2, 3, 4, 6, 7], [3, 4, 5], [3, 4, 5], [5]]
        # Grab the correct list for the current interval
        intervalindex = interval(lastnotes[0][1], lastnotes[0][3])[0]-1
        options = [0 for x in range(len(counterpoint[intervalindex%8]))]
        for i in range(len(counterpoint[intervalindex%8])):
            options[i] = [0, counterpoint[intervalindex%8][i][0], 0, counterpoint[intervalindex%8][i][1]]
        # Create empty lists to fill later
        addedlist = []
        ratings = [0 for x in range(len(options))]
        # Calculate what each possible option would look like when added to our current notes
        # We can use this to easily see which options are valid and which aren't in a counterpoint context
        for i in range(len(options)):
            addedlist.append([scale[scale.index(lastnotes[0][0])+options[i][0]], scale[scale.index(lastnotes[0][1])+options[i][1]], scale[scale.index(lastnotes[0][2])+options[i][2]], scale[scale.index(lastnotes[0][3])+options[i][3]]])
        for i in range(len(addedlist)):
            # Give each option a rating based on how well it abides by counterpoint rules
            # High rating == bad
            rating = 0
            # No tritones, octaves or unisons
            if abs(addedlist[i][3]-addedlist[i][1]) == 6 or abs(addedlist[i][3]-addedlist[i][1]) >= 12 or abs(addedlist[i][3]-addedlist[i][1]) <= 0:
                rating = rating+40
            if interval(addedlist[i][0], addedlist[i][1])[0] == 2 or interval(addedlist[i][0], addedlist[i][1])[0] == 7:
                rating = rating + random.randint(0, 2)
            elif interval(addedlist[i][0], addedlist[i][1])[0] == 4 or interval(addedlist[i][0], addedlist[i][1])[0] == 5:
                rating = rating + random.randint(0, 1)
            elif interval(addedlist[i][0], addedlist[i][1])[0] == 6 and cadence < 0:
                rating = rating + (cadence/2)
            for y in [1, 3]:
                # Invert direction after a jump
                if lastmoves[0][y] >= 2 and options[i][y] >= 0 or lastmoves[0][y] <= -2 and options[i][y] <= 0:
                   rating = rating + 20
                # Stay within the range of 48-72
                if lastnotes[0][y] > 72 and options[i][y] >= 0:
                    rating = rating + (lastnotes[0][y] - 72)
                if lastnotes[0][y] < 60 and options[i][y] <= 0:
                    rating = rating + (60 - lastnotes[0][y])
                for x in range(5):
                    # No serial tritones as well
                    if abs(lastnotes[x][y]-addedlist[i][y]) == 6:
                        rating = rating+10
                    #prevent heavy repetition
                    if lastnotes[x][y] == addedlist[i][y]:
                        rating = rating + random.randint(0, 2)
            thirdvoices = middlevoice[abs(interval(addedlist[i][0], addedlist[i][2])[0]-1)%8]
            thirdratings = [0 for x in range(len(thirdvoices))]
            for y in range(len(thirdvoices)):
                thirdrating = 0
                thirdoption = scale[scale.index(addedlist[i][0])+thirdvoices[y]]
                if lastmoves[0][2] >= 2 and abs(thirdoption - lastnotes[0][2]) >= 0 or lastmoves[0][2] <= -2 and abs(thirdoption - lastnotes[0][2]) <= 0:
                   thirdrating = thirdrating + 10
                if interval(addedlist[i][1], addedlist[i][3])[0] == 6 and thirdoption - addedlist[i][1] == 5 and cadence < 0:
                    thirdrating = thirdrating + cadence
                if abs(thirdoption - lastnotes[0][2]) > 2:
                    thirdrating = thirdrating + abs(thirdoption - lastnotes[0][2])*2
                for x in [1, 3]:
                    if abs(addedlist[i][x] - thirdoption) == 6 or abs(addedlist[i][x] - thirdoption) >= 12 or abs(addedlist[i][x] - thirdoption) <= 0:
                        thirdrating = thirdrating + 10
                    if abs(addedlist[i][x] - thirdoption) == 7 and abs(lastnotes[0][2]- lastnotes[0][x]) == 7 or abs(addedlist[i][x] - thirdoption) == 2 and abs(lastnotes[0][2]- lastnotes[0][x]) == 2:
                        thirdrating = thirdrating + 10
                for x in range(5):
                    # No serial tritones as well
                    if abs(lastnotes[x][2] - thirdoption) == 6:
                        thirdrating = thirdrating+5
                    if lastnotes[x][2] == thirdoption:
                        thirdrating = thirdrating+3
                if x == 2 or x == 7:
                    thirdrating = thirdrating + random.randint(0, 3)
                if thirdoption >= lastnotes[0][2]:
                    thirdrating = thirdrating + 10
                thirdratings[y] = thirdrating
            minpos = min(range(len(thirdratings)), key=thirdratings.__getitem__)
            addedlist[i][2] = scale[scale.index(addedlist[i][0])+(thirdvoices[minpos])]
            #print(addedlist[i])
            ratings[i] = rating + thirdratings[minpos]
            #print(thirdratings[minpos])
            #print(rating)
        # Find positions of the lowest ratings, and choose a random value from all the lowest options (in case there's two equally valid options)
        choice = addedlist[random.choice([i for i, x in enumerate(ratings) if x == min(ratings)])]
        print(choice)
        basschoices = []
        for y in range(1, 4):
            for x in range(1, 4):
                    n = [choice[x], choice[y]]
                    n.sort()
                    interv = interval(n[0], n[1])[0]
                    offset = (int(n[0]/12)-1)*12
                    if offset < 36:
                        offset = offset + 12
                    if interv == 5 or interv == 3:
                        basschoices.append(int(n[0])%12+offset)
                    elif interv == 4 or interv == 6:
                        basschoices.append(int(n[1])%12+offset)
        basschoices = [note for note, note_count in Counter(basschoices).most_common(2)]
        if len(basschoices) > 1:
            distancelist = []
            for i in range(len(basschoices)):
                distancelist.append(abs(lastnotes[0][0]-basschoices[i]))
            minimums = [y for y, x in enumerate(distancelist) if x == min(distancelist)]
            basschoices = int(basschoices[random.choice(minimums)])
        elif len(basschoices) == 1:
            basschoices = basschoices[0]
        else:
            basschoices = lastnotes[0][0]
        choice[0] = basschoices
        lastnotes.insert(0, list(choice))
        lastmoves.insert(0, [scale.index(lastnotes[0][x]) - scale.index(lastnotes[1][x]) for x in range(4)])
        if interval(lastnotes[0][1], lastnotes[0][3])[0] == 6 and lastnotes[0][2] - lastnotes[0][1] == 5 and cadence <= 0 and seq <= 15:
            if lastnotes[0][3] - lastnotes[0][1] == 8:
                choice[1] = choice[1]-1
                print('cool', choice)
            for i in range(4):
                voices[i].append([seq, int(choice[i])])
            choice = [scale[scale.index(lastnotes[0][1]) - 1]-12, scale[scale.index(lastnotes[0][1]) - 1], scale[scale.index(lastnotes[0][1]) - 1]+7, scale[scale.index(lastnotes[0][1]) - 1]+12]
            print('hey!', choice)
            lastnotes.insert(0, list(choice))
            for i in range(4):
                voices[i].append([seq+1, int(choice[i])])
            key = choice[0]%12
            cadence = 24
        else:
            for i in range(4):
                timing = random.randint(i, (i*2)+1)
                timing = [0, 0, 0, 0.5, 0.5, 0.5, 0.5, 0.5][timing]
                if lastmoves[0][i] != 0 and random.randint(0, 10) != 0:
                    voices[i].append([seq+timing, int(choice[i])])
            cadence = cadence - 1

def playseq():
    global measureCount
    composer()
    noteoffs = [60, 60, 60, 60]
    measureCount = measureCount + 1
    for i in range(4):
        for x in range(len(voices[i])):
            events.append([voices[i][x][0] * sixteenthNoteDuration, i, voices[i][x][1]])
    # transform the sixteenthNoteSequece to an eventlist with time values
    events.sort()
    velocity = 70
    maxlength = 4
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
        for i in range(1, 4):
            if event[1] == i:
                midiout.send_message([0x80, noteoffs[i], 90])
                time.sleep(0.001)
                if velocity > 105:
                    velocity = velocity + random.randint(-3, 0)
                elif velocity < 30:
                    velocity = velocity + random.randint(0, 2)
                else:
                    velocity = velocity + random.randint(-2, 2)
                midiout.send_message([0x90, event[2], velocity])

                noteoffs[i] = event[2]
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
            for i in range(4):
                midiout.send_message([0x80, noteoffs[i], 90])
            playseq()
        else:
            time.sleep(0.001)

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

playseq()
