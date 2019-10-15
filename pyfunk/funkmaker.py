# 1. Zorgen voor betere chord changes zonder hooktheory, mss werken aan timing van de changes (soms heel veel en soms geen!)
# 2. Meer variatie in speelstijlen:
    # 1. Unisono met drumfills en variabele lead rol
    # 2. Staccato door duration aan te passen
    # 3. Rubato met alleen keys, variabel bass
    # 4. Half time
# Let op dat fills moeten blijven werken
# Variabele lengtes per part
# 3. CCs voor Sound design?

import random, sys, time, sched, rtmidi, requests, json, getpass, npyscreen
import threading
from midiutil.MidiFile import MIDIFile
from HookTheory import HookTheory
from requests.exceptions import ConnectionError
from tqdm import tqdm


endplay = 0
length = 0
repeats = 0
key = 2
swing = 0
bpm = 0
timesigchoice = 0
beatsPerMeasure = 0
countlist = 0
scheduler = None
pause = 0
partmode = 0
measureCount = 0
#List to later store our progressions so we can prepare these progressions in advance
progressions = []
history = []

# Generate 5 midi outputs
midiouts = [rtmidi.MidiOut() for i in range(5)]
# List for the tracknames to assign to tracks
tracknames = ['Bass', 'Lead', 'Drums', 'Keys', 'Chords']
# Open the midiports
for i in range(len(midiouts)):
    midiouts[i].open_virtual_port(tracknames[i])

# Count the number of measures, for fills and changes

# Key, this variable can change with modulations
key = 0
# Variable for pausing the scheduler
pause = 0
# Our starting chord for offline chord gen
chordchoice = 2
donepercentage = 0

parts = [[0 for i in range(length)] for x in range(5)]
lastparts = [[[0, key+60] for i in range(length)] for z in range(len(parts))]

def welcome():
    global ht, offlinemode, progressions, progbar
    progressions = []
    print("\x1b[8;24;80t")
    print("                 Would you like to run in online mode? (y/n)\n\n\n\n\n\n\n\n\n")
    # Variable to switch between HookTheory API or the offline chord generator algorithm
    offlinemode = ['y', 'n'].index(custom_input('string', ['y', 'n']))
    if offlinemode == 0:
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPlease enter your HookTheory username and password: \n")
        username = input('Username:\n')
        password = getpass.getpass()
        print("\n")
        try:
            ht = HookTheory(username, password)
            ht.getAuth()
        except ConnectionError:
            offlinemode = 1
            print('No Network connection, falling back to offline mode')
        progbar = 0
        hookthread = threading.Thread(target=HookTheoryGet)
        hookthread.daemon = True
        hookthread.start()
        lastlen = 0
        with tqdm(total=12, desc='Getting progessions from HookTheory', bar_format='{l_bar}{bar}|{n_fmt}/{total_fmt}') as pbar:
            while len(progressions) < 4:
                if lastlen != progbar:
                    pbar.update(progbar - lastlen)
                    lastlen = progbar
                time.sleep(0.5)
    else:
        progressions = [[backupchordgen() for i in range(6)] for i in range(4)]
        chordchoice = random.randint(1, 4)
    menu()

def menu():
    global bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, key, swing, playthread, progbar, progressions, endplay, pause, measureCount, partmode
    print("\x1b[8;24;80t")
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n What would you like PyFunk to do?                         \n")
    print(" ______________________________________________________________________________\n")
    print("    1: Generate sequence with random settings\n")
    print("    2: Generate sequence with custom settings\n")
    print("    3: Generate sequence with default settings\n")
    print("    4: Generate custom output as midi file only\n")
    print("    5: Switch to online mode\n")
    print("    6: Quit PyFunk\n")
    print(" ______________________________________________________________________________\n\n\n")
    choice = custom_input('int', 1, 6)
    if choice == 1:
        partmode = 0
        bpm = random.randint(95, 120)
        key = random.randint(0, 11)
        swing = random.randint(15, 30)/bpm
        timesigchoice = 0
        composerSetup(bpm, key, swing, timesigchoice)
    elif choice == 2:
        partmode = 1
        composerSetup()
    elif choice == 3:
        partmode = 0
        composerSetup(105, 0, 0.25, 0)
    elif choice == 4:
        partmode = 1
        composerSetup()
        compose()
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        savemidi()
    elif choice == 5:
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        welcome()
    elif choice == 6:
        offlinemode = 1
        sys.exit()
    pause = 0
    endplay = 0
    measureCount = 0
    if choice < 4:
        playthread = threading.Thread(target=playseq)
        playthread.daemon = True
        playthread.start()
        playmenu()
    else:
        menu()


# create HookTheory instance
# aquire authorization so get requests to the
# HookTheory API may be made
# Turn on offlinemode if this fails

def composerSetup(*args):
    global bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, key, swing
    if len(args) > 0:
        bpm = args[0]
        key = args[1]
        swing = args[2]
        timesigchoice = args[3]
    else:
        print("\x1b[8;24;80t")
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose tempo (bpm): ")
        bpm = custom_input('int', 50, 200)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose key (E.G: C# or 1): ")
        askkey = input("> ")
        key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'].index(askkey)%12
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose swing percentage (decimal number):")
        swing = custom_input('float', 0, 1)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n0: 4/4       1:5/4       2:7/8")
        print("\nChoose time signature: ")
        timesigchoice = custom_input('int', 0, 2)
    if timesigchoice == 0:
        beatsPerMeasure = 8
        length = 32
        repeats = 4
        countlist = [i for i in range(length)]
    elif timesigchoice == 1:
        beatsPerMeasure = 2.5
        repeats = 12
        countlist = [0, 1, 2, 1, 0, 1, 4, 1, 2, 1, 2, 1, 0, 1, 4, 1]
        length = 10
    elif timesigchoice == 2:
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

timepassed = 0

def compose():
    global parts, lastparts, swing, voices, key, scale, measureCount, bpm, partmode, timepassed
    if measureCount % repeats == 0:
        measureCount = 0
        if random.randint(0, 1) == 0 and partmode == 0:
            bpm = random.randint(95, 120)
            swing = random.randint(15, 30)/bpm
            key = random.randint(0, 11)
        fill = 0
        mode = 1
        parts = [[0 for i in range(length)] for x in range(5)]
        parts[2] = [[0 for i in range(5)] for i in range(length)]
        parts[3] = [[0 for i in range(5)] for i in range(length)]
        print("\x1b[8;24;80t")
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        print(" ______________________________________________________________________________\n")
        print('Key: ', ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C'][int(key%12)])
        print('Tempo:', bpm, "bpm")
        print(" ______________________________________________________________________________\n")
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n')
        print(" ______________________________________________________________________________\n")
        print("s = Save    n = New Sequence    p=Pause/Play   m=Toggle modulations   q = Quit")
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
    # TODO Use this rhythmlist to define accents
    # Adjust for 5/4 and 7/8
    #rhythmlist = [random.randint((1-(i%2))*2, 4+(1-(i%2))*2) + (i%4==0)*2 for i in range(length)]
    rhythmlist = [0 for i in range(length)]
    for i in range(int(length/2)):
        if timepassed > 2 and random.randint(0, timepassed+1) != 0:
            # decide if we want syncopation
            if random.randint(0, 2) != 0:
                rhythmlist[i*2] = [int(random.randint(0, 2) != 0) for i in range(4)]
                rhythmlist[(i*2)+1] = [0, 0, 0, 0]
            else:
                rhythmlist[i*2] = [0, 0, 0, 0]
                rhythmlist[(i*2)+1] = [random.randint(0, 1) for i in range(4)]
            timepassed = 0
        else:
            rhythmlist[i*2] = [0, 0, 0, 0]
            rhythmlist[(i*2)+1] = [0, 0, 0, 0]
        timepassed = timepassed+1
    rhythmlist = [random.choice([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1]]) for i in range(length)]
    if len(progressions) > 0:
        progression = progressions.pop(0)
    else:
        progression = [backupchordgen() for i in range(6)]
    for i in range(length):
        # These lines decide how full a measure is by looking at the amount of notes and the BPM (lots of notes on a high BPM sounds chaotic, few notes on low BPM sounds empty/boring)
        partsum = [sum([1 if (isinstance(note, int) and note != 0) or (isinstance(note, list) and sum(note) != 0) else 0 for note in part]) for part in parts]
        fullness = [int(sum*(pow(bpm/105, 4))) for sum in partsum]
        lastparts = [lastplayed(parts[z], i) for z in range(len(parts))]
        if lastparts[4][1] != 0:    #???
            lastparts[4][1].sort()
        x = countlist[i%len(countlist)]
        #Generate Chords in scale
        if ((x%2 == 0 and random.randint(0, 3) == 0) or x == 0) and mode != 0 and len(progression) > 0:
            if isinstance(progression[0], list) == True:
                parts[4][i] = [note+60+key for note in progression.pop(0)]
                change = 1
            else:
                parts[4][i] = parts[4][i-1]
                change = 0
        elif x > 0 and mode == 1:
            parts[4][i] = parts[4][i-1]
            change = 0
        elif x > 0 and parts[4][i] != parts[4][i-1]:
            change = 1
        elif x == 0:
            change = 1
        else:
            change = 0
        try:
            rootnotes = spreadNotes([parts[4][i][0]])
            fullchord = spreadNotes(parts[4][i])
        except TypeError as e:
            print('error:', parts[4][i], e)
        # BASS
        if random.randint(0, 2) == 0 or mode != 0:
            if rhythmlist[i][0] == 1:
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
                    parts[0][i] = movement(lastparts[0][1], fullchord, direction)
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
        if rhythmlist[i][1] == 1:
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
            elif x%2 == 0:
                parts[1][i] = movement(lastparts[1][1], rootnotes, 0)
                silence = random.randint(0, 1) == 0
            if parts[1][i] != 0 and abs(lastparts[1][1]-parts[1][i]) > 2 and lastparts[1][1] < 84 and lastparts[1][1] > 60:
                dir = int(dir/abs(dir))*-1
        # DRUMS
        # kick
        if rhythmlist[i][2] == 1:
            if x % 8 == 0 and random.randint(0, 3) != 0 or x%16 == 0 or random.randint(0, (1-(x%2))+5) == 0 or parts[0][i] != 0 and random.randint(0, 2) == 0:
                parts[2][i][0] = 36
            else:
                parts[2][i][0] = 0
            if x >= 4 and (parts[2][i-1][0]+parts[2][i-2][0]+parts[2][i-3][0]+parts[2][i-4][0]) > 72:
                parts[2][i][0] = 0
        # Snare
        elif (random.randint(0, 2) == 0 and mode == 0) or mode == 1:
            if x % 8 == 4 or random.randint(0, (x%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or parts[2][i][1] > 0 and random.randint(0, 1+abs(0-i)%4) == 2:
                parts[2][i][1] = 38
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
        # Toms, snares and cymbals for fills
        if (fill == 1 and x > 16 and random.randint(0, 3) != 0) or mode == 2:
            fillchoice = random.randint(0, 8)+(i-16)
            note = [47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38, 47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38][fillchoice]
            parts[2][i][3] = note
        if mode != 0:
            parts[2][0][3] = random.choice([49, 50])
        # KEYS
        if mode != 0 or random.randint(0, 2) == 0 and i != length:
            if rhythmlist[i][3] == 1:
                voicing = arrange(parts[4][i], lastparts[3][1][0:3], scale)
                if random.randrange(0, 2) == 0:
                    parts[3][i] = voicing
                    parts[3][i].append(parts[3][i][0]-12)
                    parts[3][i].append(parts[3][i][3])
                elif lengthgenerator(parts[3])[i] == 0 and mode != 1 and i != length-1 and random.randint(0, 1) == 0:
                    chromatic = random.choice([-1, 1])
                    parts[3][i] = [z+chromatic for z in parts[3][i+1]]
                else:
                    parts[3][i] = [(voicing[y]%12)+60 for y in range(len(voicing))]
                    parts[3][i].append((parts[3][i][0]%12)+48)
#            else:
#                parts[3][i] = []
    # Generate velocity list
    velocity = [random.randint(80, ((1-x%2)*20)+97) for i in range(length)]
    # Calculate the distance to the next note so we can determine the maximum duration of the note
    lengthperpart = [8, 8, 2, 4, 2, 2, 2, 2]
    partdist = [lengthgenerator(parts[x]) for x in range(len(parts))]
    duration = [[y if y < lengthperpart[z] else lengthperpart[z] for y in partdist[z]] for z in range(len(partdist))]
    #print(duration)
    # Voice lists are made up of: [time in 16ths, note, velocity, length]
    # These will later be used for live midi playback or midi file output
    # In these lines we also apply the swing feel, velocity and semi-random duration of each note
    voices = [[[i+((i%2)*swing), x, velocity[i]+random.randint(-5, 5), random.randint(((duration[y][i]-2)+(1-i%2))+1, duration[y][i]+1+(1-i%2))] for i, x in enumerate(parts[y])] for y in range(len(parts))]
    history.append(voices)
#       PLAYBACK TOOLS

def playseq():
    global scheduler, endplay
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
    if endplay == 1:
        time.sleep(1)
    else:
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

def savemidi():
    global length
    print('How many bars would you like to save?')
    hist = custom_input('int', 1, 50)
    if hist > len(history):
        for i in range(hist - len(history)):
            compose()
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    histlist = history[int(hist*-1):][::-1]
    mf = MIDIFile(len(parts), deinterleave=False)
    time = 0
    for i in range(len(parts)):
        mf.addTrackName(i, 0, tracknames[i])
        mf.addTempo(i, 0, bpm)
        channel = 0
        for y in range(len(history)):
            for x in range(len(histlist[y][i])):
                if isinstance(histlist[y][i][x][1], int):
                    histlist[y][i][x][1] = [histlist[y][i][x][1]]
                for pitch in histlist[y][i][x][1]:
                    if pitch != 0:
                        volume = histlist[y][i][x][2]
                        time = (histlist[y][i][x][0]+(y*length))/4  #convert from beats to sixteenths
                        duration = abs(histlist[y][i][x][3])/4
                        print(duration)
                        mf.addNote(i, channel, pitch, time, duration, volume)
    filename = (input('Save As:') +  ".mid")
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)

def custom_input(type, *range):
    correct = 0
    while correct == 0:
        try:
            value = input('> ')
            if type == 'int':
                    value = int(value)
                    if len(range) == 0 or range[0] <= value and range[1] >= value:
                        correct = 1
                    else:
                        raise ValueError
            elif type == 'float':
                    value = float(value)
                    if len(range) == 0 or range[0] <= value and range[1] >= value:
                        correct = 1
                    else:
                        raise ValueError
            elif type == 'string':
                if len(range) == 0 or value in range[0]:
                    correct = 1
                else:
                    raise ValueError
        except ValueError:
            print('Invalid response, please try again')
    return value

# UI function during playback to allow changes and going back to the main menu
def playmenu():
    global pause, measureCount, bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, scheduler, playthread, endplay, partmode
    while True:
        choice = custom_input('string', ['s', 'q', 'n', 'p', 'm'])
        if choice == 's':
            pause = 1
            savemidi()
            pause = 0
            playmenu()
        elif choice == 'q':
            for i in scheduler.queue:
                scheduler.cancel(i)
            endplay = 1
            menu()
        elif choice == 'n':
            for i in scheduler.queue:
                scheduler.cancel(i)
            endplay = 1
            measureCount = 0
            composerSetup()
            endplay = 0
            partmode = 1
            playthread = threading.Thread(target=playseq)
            playthread.daemon = True
            playthread.start()
            playmenu()
        elif choice == 'm':
            if partmode == 0:
                print('Varying keys and tempo are now turned on')
            else:
                print('Varying keys and tempo are now turned off')
            partmode = 1-partmode
            playmenu()
        elif choice == 'p':
            if pause == 0:
                print('Paused, press p to start playing')
            else:
                print('Playing, press p to pause')
            pause = 1-pause
            playmenu()
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

# We use the HookTheory API to generate chords for us based on a database of over 5000 song chords
# TODO Make interceptions for errors!
# TODO Make a backup algorithm for when internet fails or HookTheory is too slow to keep up
def HookTheoryGet():
    global progressions, progbar, offlinemode, ht, ext
    fallback = 0
    while True and offlinemode == 0:
        if len(progressions) < 4:
            chordIDs = str(random.randint(1, 6))
            progression = [0 for x in range(4)]
            progression[0] = translatechord(chordIDs[0])
            for x in range(1, 4):
                try:
                    # Prevents going over the 10 chords per 10 seconds rule
                    time.sleep(0.5)
                    receivedchord = ht.getChords(chordIDs).json()
                # Sometimes the HookTheory API doesn't pass a valid value, nothing else I can do but except the error ¯\_(ツ)_/¯
                except json.decoder.JSONDecodeError:
                    print('Intercepted HookTheory Error: 0 (invalid response)')
                    break
                except AssertionError:
                    correct = 0
                    while correct == 0:
                        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                        print('Invalid login credentials, do you want to try again? (y/n)')
                        correct = ['y', 'n'].index(custom_input('string', ['y', 'n']))
                        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                        if correct == 1:
                            offlinemode = 1
                            progressions = [[backupchordgen() for i in range(6)] for i in range(4)]
                            sys.exit()
                        else:
                            username = input('Username:\n')
                            password = getpass.getpass()
                            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                            ht = HookTheory(username, password)
                            ht.getAuth()
                            try:
                                receivedchord = ht.getChords(chordIDs).json()
                            except AssertionError:
                                correct = 0
                            finally:
                                correct = 1
                options = [[]  for i in range(len(receivedchord))]
                chordprob = random.random()*receivedchord[-1]['probability']
                totalprob = 0
                for i in range(len(options)):
                    # Hooktheory has a 10 requests per 10 seconds maximum, the SDK should automatically enforce this but somehow it still goes wrong Sometimes
                    # I introduced some extra sleep time and also excepted the error just to be safe
                    try:
                        options[i] = [[totalprob, receivedchord[i]['probability']+totalprob], receivedchord[i]['chord_ID']]
                        totalprob = options[i][0][1]
                    except KeyError as e:
                        print('Intercepted HookTheory Error: 1 (too many requests)')
                        break
                    if chordprob >= options[i][0][0] and chordprob <= options[i][0][1]:
                        chord = options[i][1]
                chordIDs = chordIDs + "," + chord
                progression[x] = translatechord(chord)
                progbar = progbar + 1
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
    # Rare cases where finalchord doesn't come out as a list but as an integer. Probably something to do with the chord_ID decoder, I'll fix this later
    # This will work for now though
    if isinstance(finalchord, list):
        return finalchord
    else:
        print('Intercepted HookTheory Error: 2')


def backupchordgen():
    global key, chordchoice
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale  = spreadNotes(scale)
    #scale = [(x+key) for x in scale]
    options = [[0, 5], [4, 6], [5], [4, 6], [0, 5], [1, 3], [0, 5]][chordchoice]
    chordchoice = random.choice(options)
    scalepos = scale[chordchoice]
    return [movement(scalepos, scale, 0), movement(scalepos, scale, 2), movement(scalepos, scale, 4), movement(scalepos, scale, 6)]

print("\x1b[8;24;80t")
print("\n\n\n\n\n\n\n")
print(" ______________________________________________________________________________\n")
print("                               Welcome to PyFunk!                            \n")
print(" ______________________________________________________________________________\n\n\n\n\n\n\n")


welcome()
