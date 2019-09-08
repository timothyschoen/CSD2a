import time
import random
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()


midiout.open_virtual_port("My virtual output")
rounds = 0
key = random.randint(0, 11)
currentnotes = [60+key, 67+key, 72+key]
allnotes = [48+key, 60+key, 67+key, 72+key]
lastnotes = 10*list([allnotes])
choice = [0, 0]
lastchoices = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
modulating = 20


seperatevoices = [[] for x in range(4)]

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

events = []
# create lists with the moments (in 16th) at which we should play the samples

# TODO:
# 1. seriele tritonus-herkenning verbeteren
# 2. puntensysteem goed balanceren
# 3. Barok frasering
# Toekomst:
# 5. In de toekomst kijken om de meest optimale route te kiezen??

def composer():
    global seperatevoices
    sequence = [0 for x in range(16)]
    rests = 0
    seperatevoices = [[] for x in range(4)]
    for seqs in range(len(sequence)):
        global modulating
        global choice
        global rounds
        global lastnotes
        global allnotes
        global key
        if modulating == 25 or modulating == 24:
            modulating = modulating-1
            sequence[seqs] = lastnotes[0]
            continue
        scale = [0,2,4,5,7,9,11]
        scale = [(x+key)%12 for x in scale]
        scale = spreadNotes(scale)
        # List of possibilities by interval, based on counterpoint
        counterpoint = [[[-1, 1]], [choice[::-1]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, 1], [1, 1], [-1, -1]], [[0, 1], [1, 0], [-1, 0], [0, 1], [-1, 1], [-2, 0], [0, 2]], [[1, 0], [-1, 0], [0, -1], [1, -1], [-1, 0], [2, 0], [0, -2]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [1, 1], [1, -1]], [choice[::-1]], [[1, -1]]]
        currentnotes.sort()
        # Grab the correct list for the current interval
        intervalindex = interval(currentnotes[0], currentnotes[2])[0]-1
        options = counterpoint[intervalindex%8]
        # Create empty lists to fill later
        addedlist = [0 for x in range(len(options))]
        ratings = [0 for x in range(len(options))]
        # Calculate what each possible option would look like when added to our current notes
        # We can use this to easily see which options are valid and which aren't in a counterpoint context
        for i in range(len(options)):
            addedlist[i] = [scale[scale.index(currentnotes[0])+options[i][0]], scale[scale.index(currentnotes[2])+options[i][1]]]
        for i in range(len(addedlist)):
            # Give each option a rating based on how well it abides by counterpoint rules
            # High rating == bad
            rating = 0
            breaks = []
            addedlist[i].sort()
            # No tritones, octaves or unisons
            if abs(addedlist[i][1]-addedlist[i][0]) == 6:
                rating = rating+40
            elif abs(addedlist[i][1]-addedlist[i][0]) >= 12:
                rating = rating+40
            elif abs(addedlist[i][1]-addedlist[i][0]) <= 0:
                rating = rating+40
            # A randomized preference for 6/3 over 4/5 and 4/5 over 7/2 balances the sound
            if interval(addedlist[i][0], addedlist[i][1])[0] == 2 or interval(addedlist[i][0], addedlist[i][1])[0] == 7:
                rating = rating + random.randint(0, 2)
            elif interval(addedlist[i][0], addedlist[i][1])[0] == 4 or interval(addedlist[i][0], addedlist[i][1])[0] == 5:
                rating = rating + random.randint(0, 1)
            for y in [0, 2]:
                # Invert direction after a jump
                if choice[int(y/2)] >= 2 and options[i][int(y/2)] >= 0 or choice[int(y/2)] <= -2 and options[i][int(y/2)] <= 0:
                    rating = rating + 10
                # Stay within the range of 48-72
                if currentnotes[y] > 72 and options[i][int(y/2)] >= 0:
                    rating = rating + (currentnotes[y] - 72)*5
                if currentnotes[y] < 60 and options[i][int(y/2)] <= 0:
                    rating = rating + (48 - currentnotes[y])*5
                for x in range(8):
                    if lastchoices[x][int(y/2)] >= 2 or lastchoices[x][int(y/2)] <= -2 or lastchoices[x][int(y/2)] == (lastchoices[x-1][int(y/2)])*-1 and lastchoices[x][int(y/2)] != 0:
                        breaks.insert(0, 1)
                    else:
                        breaks.insert(0, 0)
                    # No serial tritones as well
                    if abs(lastnotes[x][y+1]-addedlist[i][int(y/2)]) == 6:
                        rating = rating+4
                    #prevent heavy repetition
                    if lastnotes[x][y+1] == addedlist[i][int(y/2)]:
                        rating = rating + 10
            if addedlist[i][1] <= currentnotes[1]:
                rating = rating + 10
            ratings[i] = rating
        print(breaks)
        # Find positions of the lowest ratings
        minimums = [i for i, x in enumerate(ratings) if x == min(ratings)]
        choice = options[minimums[random.randrange(len(minimums))]]
        lastchoices.insert(0, list(choice))
        # Add the chosen option to the current notes
        currentnotes[0] = scale[scale.index(currentnotes[0])+choice[0]]
        currentnotes[2] = scale[scale.index(currentnotes[2])+choice[1]]
        # Add the third note!
        thirdnote = [[5], [4, 5, 6], [4, 5, 6, 7], [2, 3, 5, 6, 7], [2, 3, 4, 6, 7], [3, 4, 5], [3, 4, 5], [5]]
        thirdpos = interval(currentnotes[0], currentnotes[2])[0]-1
        thirdoptions = thirdnote[thirdpos%8]
        addedthird = [0 for x in range(len(thirdoptions))]
        thirdratings = [0 for x in range(len(thirdoptions))]
        # Same mechanism for the selection, we calculate how well the note fits with a rating
        for i in range(len(thirdoptions)):
            addedthird[i] = scale[scale.index(currentnotes[0])+thirdoptions[i]]
        for i in range(len(addedthird)):
            thirdrating = 0
            for x in [0, 2]:
                if abs(currentnotes[x] - addedthird[i]) == 6:
                    thirdrating = thirdrating + 40
                if abs(currentnotes[x] - addedthird[i]) >= 12:
                    thirdrating = thirdrating + 20
                if abs(currentnotes[x] - addedthird[i]) <= 0:
                    thirdrating = thirdrating + 20
            for x in range(5):
                # No serial tritones as well
                if abs(lastnotes[x][2] - addedthird[i]) == 6:
                    thirdrating = thirdrating+5
                if lastnotes[x][2] == addedthird[i]:
                    thirdrating = thirdrating+3
            if thirdoptions[i] == 2 or thirdoptions[i] == 7:
                thirdrating = thirdrating + random.randint(0, 3)
            thirdrating = thirdrating + (abs(lastnotes[0][2] - addedthird[i]))*5
            if addedthird[i] >= currentnotes[2]:
                thirdrating = thirdrating + 5
            thirdratings[i] = thirdrating
        thirdminimums = [i for i, x in enumerate(thirdratings) if x == min(thirdratings)]
        thirdchoice = addedthird[thirdminimums[random.randrange(len(thirdminimums))]]
        currentnotes[1] = thirdchoice
        # Sort, in case one note passes the other
        currentnotes.sort()
        bassnote = (findroot(currentnotes)%12)+48
        if currentnotes[2] - currentnotes[0] == 9 and currentnotes[1] - currentnotes[0] == 5 and modulating == 2 and seqs < 14:
            modulating = 1
            allnotes = [bassnote] + currentnotes
        elif currentnotes[2] - currentnotes[0] == 8 and currentnotes[1] - currentnotes[0] == 5 and modulating == 2 and seqs < 14:
            modulating = 1
            allnotes = [bassnote] + [currentnotes[0]-1] + [currentnotes[1]] + [currentnotes[2]]
            print('m6 -> M6')
            print('deze:', allnotes)
        else:
            allnotes = [bassnote] + currentnotes
        allnotes.sort()
        lastnotes.insert(0, list(allnotes))
        rounds = rounds+1
        if  modulating > 2:
            modulating = modulating - 1
            sequence[seqs] = allnotes
        elif modulating == 2:
            sequence[seqs] = allnotes
        else:
            print('modulatie')
            currentnotes[0] = scale[scale.index(currentnotes[0]) - 1]
            currentnotes[1] = currentnotes[0] + 7
            currentnotes[2] = currentnotes[0] + 12
            bassnote = currentnotes[0] - 12
            allnotes = [bassnote] + list(currentnotes) + [0]
            lastnotes.insert(0, list(allnotes))
            key = currentnotes[0]%12
            modulating = 25
            sequence[seqs] = allnotes
        for i in range(4):
            timing = [0, 0, 0.5, 0.5, 0.5, 0.5][random.randint(0,i)]
            if allnotes[i] != lastnotes[1][i]:
                seperatevoices[i].insert(0, [seqs+timing, allnotes[i]])
            seperatevoices[i].sort()
    print(seperatevoices)
def playseq():
    global measureCount
    composer()
    measureCount = measureCount + 1
    for i in range(4):
        for note in seperatevoices[i]:
            events.append([note[0] * sixteenthNoteDuration, i, note[1]])
    lastnotes = [60, 60, 60, 60]
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
        for i in range(4):
            if event[1] == i:
                midiout.send_message([0x80, lastnotes[i], 0])
                midiout.send_message([0x90, event[2], random.randint(60, 90)])
                lastnotes[i] = event[2]
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


#function to spread any scale or chord over the full MIDI range
def spreadNotes(notes):
    newnotes = []
    for i in notes:
        for j in range(-10, 10):
            if (i % 12) + (j * 12)  >= 0 and (i % 12) + (j * 12) <= 127:
                newnotes.append((i % 12) + (j * 12))
    newnotes.sort()
    return newnotes

def findroot(notes):
    intervals = []
    lst = []
    for x in notes:
        for y in notes:
            n = [x, y]
            n.sort()
            interv = n[1]-n[0]
            if interv == 7:
                lst.append(int(n[0]))
            if interv == 5:
                lst.append(int(n[1]))
    if len(lst) > 0:
        return lst[random.randint(0, 1)]
    else:
        return key+(4*12)

def noteToFreq(note):
    a = 440 #frequency of A (common value is 440Hz)
    return (a / 32) * (2.001 ** ((note - 9) / 12))

def interval(low, high):
    octdif = int((high-low)/12)*7
    intervals = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    qualities = ['p', 'min', 'maj', 'min', 'maj', 'p', 'aug', 'p', 'min', 'maj', 'min', 'maj', 'p']
    return [intervals[(high - low)%12]+octdif, qualities[(high - low)%12]]
playseq()
