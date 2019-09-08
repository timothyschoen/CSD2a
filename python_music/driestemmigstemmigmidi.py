import time
import random
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()


midiout.open_virtual_port("My virtual output")
rounds = 0
movingvoice = 3
currentnotes = [60, 67, 72]
lastnotes = [[60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72],[60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72], [60, 67, 72]]
lastall = [[48, 60, 67, 72]]
choice = [0, 0]
modulating = 0
key = 0

def composer():
    global modulating
    global choice
    global rounds
    global lastnotes
    global movingvoice
    global key
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
        addedlist[i] = [scaletomidi(miditoscale(currentnotes[0], int(key)) + options[i][0], int(key)), scaletomidi((miditoscale(currentnotes[2], int(key)) + options[i][1]), int(key))]
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
                    rating = rating + 10
        if addedlist[i][1] <= currentnotes[1]:
            rating = rating + 10
        ratings[i] = rating
    # Find positions of the lowest ratings
    minimums = [i for i, x in enumerate(ratings) if x == min(ratings)]
    choice = options[minimums[random.randrange(len(minimums))]]
    # Add the chosen option to the current notes
    currentnotes[0] = scaletomidi((miditoscale(currentnotes[0], int(key)) + choice[0]), int(key))
    currentnotes[2] = scaletomidi((miditoscale(currentnotes[2], int(key)) + choice[1]), int(key))
    # Add the third note!
    thirdnote = [[5], [4, 5, 6], [4, 5, 6, 7], [2, 3, 5, 6, 7], [2, 3, 4, 6, 7], [2, 3, 4, 5], [3, 4, 5], [5]]
    thirdpos = interval(currentnotes[0], currentnotes[2])[0]-1
    thirdoptions = thirdnote[thirdpos%8]
    addedthird = [0 for x in range(len(thirdoptions))]
    thirdratings = [0 for x in range(len(thirdoptions))]
    # Same mechanism for the selection, we calculate how well the note fits with a rating
    for i in range(len(thirdoptions)):
        addedthird[i] = scaletomidi(miditoscale(currentnotes[0], int(key)) + thirdoptions[i], int(key))
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
    for i in range(2):
        if currentnotes[i] > 80:
            currentnotes[i] = currentnotes[i] - 24
    currentnotes.sort()
    print(currentnotes[1] - currentnotes[0], currentnotes[2] - currentnotes[0])
    if abs(currentnotes[2] - currentnotes[0]) == 8 and currentnotes[1] - currentnotes[0] == 5 and modulating == 2:
        print('hierboven = 4-6')
        modulating = 1
    lastnotes.insert(0, list(currentnotes))
    bassnote = findroot(currentnotes)-12
    allnotes = [bassnote] + currentnotes
    print(allnotes)
    lastall.append(list(allnotes))
    if rounds%4 == 0:
        movingvoice = random.randint(0,3)
    for i in range(4):
        midiout.send_message([0x80, lastall[1][i], 0])
        if allnotes[i] != lastall[1][i]:
            if i == movingvoice or i + 1 == movingvoice:
                time.sleep(0)
            else:
                time.sleep(0.35)
            midiout.send_message([0x90, allnotes[i], random.randint(60, 90)])
        time.sleep(random.randint(0, 1)/200)
    for i in range(3):
        midiout.send_message([0x80, lastnotes[1][i], 0])
    rounds = rounds+1
    if modulating != 0 and modulating > 2:
        modulating = modulating - 1
        composer()
    elif modulating == 2:
        composer()
    else:
        print('modulatie')
        currentnotes[0] = scaletomidi((miditoscale(currentnotes[0], 0) -1), int(key))
        currentnotes[1] = currentnotes[0] + 7
        currentnotes[2] = currentnotes[0] + 12
        bassnote = currentnotes[0]-12
        allnotes = [bassnote] + list(currentnotes)
        print(allnotes)
        for i in range(4):
            midiout.send_message([0x80, lastall[1][i], 0])
            midiout.send_message([0x90, allnotes[i], random.randint(60, 90)])
        time.sleep(1.15)
        key = currentnotes[0]%12
        modulating = 40
        composer()
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
    low = low % 12
    high = high % 12
    intervals = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    qualities = ['p', 'min', 'maj', 'min', 'maj', 'p', 'aug', 'p', 'min', 'maj', 'min', 'maj', 'p']
    return [intervals[high - low]+octdif, qualities[high - low]]

def scaletomidi(note, key):
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale = [(x+int(key))%12 for x in scale]
    newnote = (int(note)%7)
    oct = int((note-1) / 7)*12
    return scale[newnote-1]+oct

def miditoscale(note, key):
    scale = [1, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    newnote = note % 12
    oct = int(note / 12)*7
    if isinstance(scale[newnote], int):
        return scale[(newnote+key)%12]+oct
    else:
        return scale[newnote]

composer()
