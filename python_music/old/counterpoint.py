from pyo import *
import time
import random

currentnotes = [60, 60]
lastnotes = [[60, 60],[60, 60],[60, 60],[60, 60],[60, 60]]
choice = [0, 0]
s = Server(nchnls=2, duplex=0, sr=20068, buffersize=512).boot()
s.start()
square = SquareTable()
a = Osc(table=square, freq=262.18197150917126, mul=0.2).out()
b = Osc(table=square, freq=262.18197150917126, mul=0.2).out()

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
        addedlist[i] = [scaletomidi(miditoscale(currentnotes[0], 0) + options[i][0], 0), scaletomidi((miditoscale(currentnotes[1], 0) + options[i][1]), 0)]
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
        for y in range(2):
            # Invert direction after a jump
            if choice[y] >= 2 and options[i][y] >= 0 or choice[y] <= -2 and options[i][y] <= 0:
                rating = rating + 10
            # Stay within the range of 48-72
            if currentnotes[y] > 72 and options[i][y] >= 0:
                rating = rating+15
            if currentnotes[y] < 48 and options[i][y] <= 0:
                rating = rating+15
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
    choice = options[minimums[random.randrange(len(minimums))]]
    # Add the chosen option to the current notes
    currentnotes[0] = scaletomidi((miditoscale(currentnotes[0], 0) + choice[0]), 0)
    currentnotes[1] = scaletomidi((miditoscale(currentnotes[1], 0) + choice[1]), 0)
    # Sort, in case one note passes the other
    currentnotes.sort()
    lastnotes.insert(0, list(currentnotes))
    print(currentnotes)
    time.sleep(0.5)
    a.freq = noteToFreq(currentnotes[0])
    b.freq = noteToFreq(currentnotes[1])
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
