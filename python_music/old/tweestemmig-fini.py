import time
import random
import rtmidi

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
    global voices
    voices = [[] for x in range(4)]
    for seq in range(16):
        scale = [0,2,4,5,7,9,11]
        scale = [(x+key)%12 for x in scale]
        scale = spreadNotes(scale)
        # List of possibilities by interval, based on counterpoint
        counterpoint = [[[-1, 1]], [[lastmoves[0][3], lastmoves[0][1]]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, 1], [1, 1], [-1, -1]], [[0, 1], [1, 0], [-1, 0], [0, 1], [-1, 1], [-2, 0], [0, 2]], [[1, 0], [-1, 0], [0, -1], [1, -1], [-1, 0], [2, 0], [0, -2]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [1, 1], [1, -1]], [[lastmoves[0][3], lastmoves[0][1]]], [[1, -1]]]
        middlevoice = [[5], [4, 5, 6], [4, 5, 6, 7], [2, 3, 5, 6, 7], [2, 3, 4, 6, 7], [3, 4, 5], [3, 4, 5], [5]]
        # Grab the correct list for the current interval
        intervalindex = interval(lastnotes[0][1], lastnotes[0][3])[0]-1
        print(intervalindex+1)
        options = [0 for x in range(len(counterpoint[intervalindex%8]))]
        print(counterpoint[intervalindex%8])
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
            if abs(addedlist[i][3]-addedlist[i][1]) == 6:
                rating = rating+40
            elif abs(addedlist[i][3]-addedlist[i][1]) >= 12:
                rating = rating+40
            elif abs(addedlist[i][3]-addedlist[i][1]) <= 0:
                rating = rating+40
            if interval(addedlist[i][0], addedlist[i][1])[0] == 2 or interval(addedlist[i][0], addedlist[i][1])[0] == 7:
                rating = rating + random.randint(0, 2)
            elif interval(addedlist[i][0], addedlist[i][1])[0] == 4 or interval(addedlist[i][0], addedlist[i][1])[0] == 5:
                rating = rating + random.randint(0, 1)
            for y in [1, 3]:
                # Invert direction after a jump
                if lastmoves[0][y] >= 2 and options[i][y] >= 0 or lastmoves[0][y] <= -2 and options[i][y] <= 0:
                   rating = rating + 10
                # Stay within the range of 48-72
                if lastnotes[0][y] > 72 and options[i][y] >= 0:
                    rating = rating+25
                if lastnotes[0][y] < 48 and options[i][y] <= 0:
                    rating = rating+25
                for x in range(5):
                    # No serial tritones as well
                    if abs(lastnotes[x][y]-addedlist[i][y]) == 6:
                        rating = rating+10
                    #prevent heavy repetition
                    if lastnotes[x][y] == addedlist[i][y]:
                        rating = rating + random.randint(0, 2)
            ratings[i] = rating
        # Find positions of the lowest ratings
        minimums = [i for i, x in enumerate(ratings) if x == min(ratings)]
        choicenum = random.choice(minimums)
        choice = addedlist[choicenum]
        choice[0] = choice[1] - 12
        choice[2] = choice[3] - 12
        # Add the chosen option to the current notes
        lastmoves.insert(0, options[choicenum])
        for i in [1, 3]:
            if lastmoves[0][i] != 0:
                voices[i].append([seq, int(choice[i])])
            elif seq - len(voices[i]) > 4:
                voices[i].append([seq, int(choice[i])])
        # Sort, in case one note passes the other
        lastnotes.insert(0, list(choice))
def playseq():
    global measureCount
    composer()
    measureCount = measureCount + 1
    for i in range(4):
        for x in range(len(voices[i])):
            events.append([voices[i][x][0] * sixteenthNoteDuration, i, voices[i][x][1]])
    noteoffs = [60, 60, 60, 60]
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
                midiout.send_message([0x80, noteoffs[i], 0])
                midiout.send_message([0x90, event[2], 80])
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
