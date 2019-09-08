from pyo import *
import time
import random

currentnotes = [60, 67, 72]
lastnotes = [[60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72],[60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72]]
choice = [0, 0]
s = Server(nchnls=2, duplex=0, sr=20068, buffersize=512).boot()
s.start()
square = SquareTable()
Aadsr = Adsr(attack=0, decay=0.4, sustain=0, release=0, dur=0.2, mul=0.3)
Badsr = Adsr(attack=0, decay=0.4, sustain=0, release=0, dur=0.2, mul=0.3)
Cadsr = Adsr(attack=0, decay=0.4, sustain=0, release=0, dur=0.2, mul=0.3)
LPFadsr = Adsr(attack=0.4, decay=0.3, sustain=0, release=0, dur=0.2, mul=-7000, add=8500)
a = Osc(table=square, freq=262.18197150917126, mul=Aadsr)
b = Osc(table=square, freq=393.2729572638, mul=Badsr)
c = Osc(table=square, freq=524.3639430183, mul=Cadsr)
alpf = MoogLP(a, LPFadsr, 0.7).out()
blpf = MoogLP(b, LPFadsr, 0.7).out()
clpf = MoogLP(c, LPFadsr, 0.7).out()

def composer():
    global choice
    global lastnotes
    # List of possibilities by interval, based on counterpoint
    counterpoint = [[[-1, 1]], [choice[::-1]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, 1], [1, 1], [-1, -1]], [[0, 1], [1, 0], [-1, 0], [0, 1], [-1, 1], [-2, 0], [0, 2]], [[1, 0], [-1, 0], [0, -1], [1, -1], [-1, 0], [2, 0], [0, -2]], [[1, 0], [-1, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [1, 1], [1, -1]], [choice[::-1]], [[1, -1]]]
    currentnotes.sort()
    # Grab the correct list for the current interval
    intervalindex = interval(currentnotes[0], currentnotes[1])[0]-1
    options = counterpoint[intervalindex%8]
    # Create empty lists to fill later
    addedlist = [0 for x in range(len(options))]
    ratings = [0 for x in range(len(options))]
    # Calculate what each possible option would look like when added to our current notes
    # We can use this to easily see which options are valid and which aren't in a counterpoint context
    for i in range(len(options)):
        addedlist[i] = [scaletomidi(miditoscale(currentnotes[0], 0) + options[i][0], 0), scaletomidi((miditoscale(currentnotes[2], 0) + options[i][1]), 0)]
    for i in range(len(addedlist)):
        # Give each option a rating based on how well it abides by counterpoint rules
        # High rating == bad
        rating = 0
        addedlist[i].sort()
        # No tritones, octaves or unisons
        if abs(addedlist[i][1]-addedlist[i][0]) == 6:
            rating = rating+40
        elif abs(addedlist[i][1]-addedlist[i][0]) >= 12:
            rating = rating+50
        elif abs(addedlist[i][1]-addedlist[i][0]) <= 0:
            rating = rating+50
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
                rating = rating+15
            if currentnotes[y] < 48 and options[i][int(y/2)] <= 0:
                rating = rating+15
            for x in range(10):
                # No serial tritones as well
                if abs(lastnotes[x][y]-addedlist[i][int(y/2)]) == 6:
                    rating = rating+10
                #prevent heavy repetition
                if lastnotes[x][y] == addedlist[i][int(y/2)]:
                    rating = rating + 6
        if addedlist[i][1] <= currentnotes[1]:
            rating = rating + 10
        ratings[i] = rating
    # Find positions of the lowest ratings
    minimums = [i for i, x in enumerate(ratings) if x == min(ratings)]
    choice = options[minimums[random.randrange(len(minimums))]]
    # Add the chosen option to the current notes
    currentnotes[0] = scaletomidi((miditoscale(currentnotes[0], 0) + choice[0]), 0)
    currentnotes[2] = scaletomidi((miditoscale(currentnotes[1], 0) + choice[1]), 0)
    # Add the third note!
    thirdnote = [[5], [4, 5, 6], [4, 5, 6, 7], [2, 3, 5, 6, 7], [2, 3, 4, 6, 7], [2, 3, 4, 5], [3, 4, 5], [5]]
    thirdpos = interval(currentnotes[0], currentnotes[1])[0]-1
    thirdoptions = thirdnote[thirdpos%8]
    addedthird = [0 for x in range(len(thirdoptions))]
    thirdratings = [0 for x in range(len(thirdoptions))]
    # Same mechanism for the selection, we calculate how well the note fits with a rating
    for i in range(len(thirdoptions)):
        addedthird[i] = scaletomidi(miditoscale(currentnotes[0], 0) + thirdoptions[i], 0)
    for i in range(len(addedthird)):
        thirdrating = 0
        for x in [0, 2]:
            if abs(currentnotes[x] - addedthird[i]) == 6:
                thirdrating = thirdrating + 20
            if abs(currentnotes[x] - addedthird[i]) >= 12:
                thirdrating = thirdrating + 20
            if abs(currentnotes[x] - addedthird[i]) <= 0:
                thirdrating = thirdrating + 20
        for x in range(5):
            # No serial tritones as well
            if abs(lastnotes[x][1] - addedthird[i]) == 6:
                thirdrating = thirdrating+10
            if lastnotes[x][1] == addedthird[i]:
                thirdrating = thirdrating+4
        if thirdoptions[i] == 2 or thirdoptions[i] == 7:
            thirdrating = thirdrating + random.randint(0, 3)
        thirdrating = thirdrating + (abs(lastnotes[0][1] - addedthird[i]))*5
        if addedthird[i] >= currentnotes[2]:
            thirdrating = thirdrating + 5
        thirdratings[i] = thirdrating
    thirdminimums = [i for i, x in enumerate(thirdratings) if x == min(thirdratings)]
    thirdchoice = addedthird[thirdminimums[random.randrange(len(thirdminimums))]]
    currentnotes[1] = thirdchoice
    # Sort, in case one note passes the other
    currentnotes.sort()
    lastnotes.insert(0, list(currentnotes))
    print(currentnotes)
    time.sleep(0.3)
    a.freq = noteToFreq(currentnotes[0])
    b.freq = noteToFreq(currentnotes[1])
    c.freq = noteToFreq(currentnotes[2])
    for i in [[0, Aadsr], [1, Badsr], [2, Cadsr]]:
        if currentnotes[i[0]] != lastnotes[1][i[0]]:
            i[1].play()
    LPFadsr.play()
    composer()


def noteToFreq(note):
    a = 440 #frequency of A (common value is 440Hz)
    return (a / 32) * (2.001 ** ((note - 9) / 12))

def interval(low, high):
    octdif = int((high-low)/12)*7
    low = low % 12
    high = high % 12
    intervals = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    qualities = ['p', 'min', 'maj', 'min', 'maj', 'p', 'aug', 'p', 'min', 'maj', 'min', 'maj', 'p']
    return [intervals[high - low]+octdif, qualities[high - low]]

def scaletomidi(note, key):
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale = [(x+key)%12 for x in scale]
    newnote = (note%7)
    oct = int((note-1) / 7)*12
    return scale[newnote-1]+oct

def miditoscale(note, key):
    scale = [1, '#1/b2', 2, '#2/b3', 3, 4, '#4/b5', 5, '#5/b6', 6, '#6/b7', 7, 8]
    newnote = note % 12
    oct = int(note / 12)*7
    if isinstance(scale[newnote], int):
        return scale[newnote]+oct
    else:
        return scale[newnote]

composer()
