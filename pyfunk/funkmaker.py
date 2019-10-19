import random, sys, time, rtmidi, requests, json, getpass
import threading
import atexit
from midiutil.MidiFile import MIDIFile
from HookTheory import HookTheory
from requests.exceptions import ConnectionError
from tqdm import tqdm


# Variable to set when we want to stop playback
endplay = 0
# Variable for meaure length in sixtheenths
length = 0
# Amount of times we want to repeat before writing a new part
repeats = 0
# The key in semitones from C (0)
key = 2
# Decimal number to indicate swing feel, 0.3 is normal
swing = 0
# Tempo of our piece in BPM
bpm = 0
# Time signature, 0 = 4/4, 1 = 5/4, 2 = 7/8
timesigchoice = 0
# Amount of quarter notes in a measure
beatsPerMeasure = 0
# list we use to define accents in different signatures
countlist = []
# Variable to pause playback
pause = 0
# Different modes that will influence the rhythmical patterns
partmode = 0
# Count the number of measures, for fills and changes
barCount = 0
#List to later store our progressions so we can prepare these progressions in advance
progressions = []
# List of all the generated parts so we can export longer midi files
history = []
# Our starting chord for offline chord gen
chordchoice = 2
# how long has it been since the last accent?
timepassed = 0


# Generate 5 midi outputs
midiouts = [rtmidi.MidiOut() for i in range(5)]
# List for the tracknames to assign to tracks
tracknames = ['Bass', 'Lead', 'Drums', 'Keys', 'Chords']
# Open the midiports
for i in range(len(midiouts)):
    midiouts[i].open_virtual_port(tracknames[i])
# List spaces to write our instruments to
parts = [[0 for i in range(length)] for x in range(5)]
# The last played part, used to decied what notes can follow
lastparts = [[[0, key+60] for i in range(length)] for z in range(len(parts))]

def welcome():
    global ht, offlinemode, progressions, progbar
    progressions = []
    # Set terminal window size for smooth UI display
    print("\x1b[8;24;80t")
    print("                 Would you like to run in online mode? (y/n)\n\n\n\n\n\n\n\n\n")
    # Variable to switch between HookTheory API or the offline chord generator algorithm
    offlinemode = ['y', 'n'].index(custom_input('string', ['y', 'n']))
    if offlinemode == 0:
        # Log in to Hooktheory
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPlease enter your HookTheory username and password: \n")
        username = input('Username:\n')
        password = getpass.getpass()
        # If this fails, we ask again when we get an error in the HookTheoryGet function
        print("\n")
        try:
            ht = HookTheory(username, password)
            ht.getAuth()
        except ConnectionError:
            # This will be thrown if there is no internet or Hooktheory is offline
            offlinemode = 1
            print('No Network connection, falling back to offline mode')
        # Variable to check the progress on our downloads from HookTheory
        progbar = 0
        # Start downloading progressions in a seperate thread
        hookthread = threading.Thread(target=HookTheoryGet)
        # This will ensure the thread closes when the program exits
        hookthread.daemon = True
        hookthread.start()
        # Variable to calculate progress
        lastlen = 0
        with tqdm(total=12, desc='Getting progessions from HookTheory', bar_format='{l_bar}{bar}|{n_fmt}/{total_fmt}') as pbar:
            while len(progressions) < 4:
                if lastlen != progbar:
                    pbar.update(progbar - lastlen)
                    lastlen = progbar
                time.sleep(0.5)
    else:
        # If we don't use hooktheory's API, we generate our chords with a backup algorithm
        chordchoice = random.randint(1, 4) #starting chord
        progressions = [[backupchordgen() for i in range(6)] for i in range(4)]
    menu()

# Main menu function
def menu():
    global bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, key, swing, playthread, progbar, progressions, endplay, pause, barCount, partmode
    print("\x1b[8;24;80t") #resize window
    # Our main menu
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
    #handle the responses for each choice
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
    # make sure we're not paused or in quitting mode, reset the barCount
    pause = 0
    endplay = 0
    barCount = 0
    # all choices below 4 will lead to instant playback
    if choice < 4:
        compose()
        playthread = threading.Thread(target=playseq)
        playthread.daemon = True
        playthread.start()
        playmenu()
    else:
        menu()

# Function for manually entering bpm, key, etc.
# I needed to use this in many places so making a function for it was shorter
# Passing arguments will cause it to use those numbers and skip manual input
def composerSetup(*args):
    global bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, key, swing
    # check if any arguments are given
    # if so, use those values instead of manual input
    if len(args) > 0:
        bpm = args[0]
        key = args[1]
        swing = args[2]
        timesigchoice = args[3]
    else:
        # Manual input
        print("\x1b[8;24;80t")
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose tempo (bpm): ")
        bpm = custom_input('int', 50, 200)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose key (E.G: C# or 1): ")
        askkey = custom_input('string', ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'])
        key = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'].index(askkey)%12
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nChoose swing percentage (decimal number):")
        swing = custom_input('float', 0, 1)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n0: 4/4       1:5/4       2:7/8")
        print("\nChoose time signature: ")
        timesigchoice = custom_input('int', 0, 2)
    # Process our input
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
        length = 32
        repeats = 4
        countlist = [i for i in range(length)]



def compose():
    global parts, lastparts, swing, voices, key, scale, barCount, bpm, partmode, timepassed, timesigchoice
    # Count the bars to place fills
    if barCount % repeats == 0:
        barCount = 0
        # Modulation and other changes after a certain number of repeats
        if random.randint(0, 1) == 0 and partmode == 0:
            bpm = random.randint(95, 120)
            swing = random.randint(15, 30)/bpm
            key = random.randint(0, 11)
        # variable to decide when we have fills
        fill = 0
        # set the mode to 0: create new bar, 1: make a variation on the previous bar
        mode = 1
        # clear some parts
        parts = [[0 for i in range(length)] for x in range(5)]
        parts[2] = [[0 for i in range(5)] for i in range(length)]
        parts[3] = [[0 for i in range(5)] for i in range(length)]
        # UI element that shows our current bpm, key, timesig and also shows the possible actions the user can undertake
        # These actions are processed by a different thread
        print("\x1b[8;24;80t")
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        print(" ______________________________________________________________________________\n")
        print('Key: ', ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C'][int(key%12)])
        print('Tempo:', bpm, "bpm")
        print('Time Signature:', ['4/4', '5/4', '7/8'][timesigchoice] )
        print(" ______________________________________________________________________________\n")
        print('\n\n\n\n\n\n\n\n\n\n\n\n')
        print(" ______________________________________________________________________________\n")
        print("s = Save    n = New Sequence    p=Pause/Play   m=Toggle modulations   q = Quit")
        print('>')
    # Place fills
    elif barCount % repeats == repeats-1:
        mode = 0
        fill = 1
    else:
        fill = 0
        mode = 0
    # If the hi-hat is open we probably want to close it
    openhat = 0
    # direction for the bass part, 1=up, 0=down
    bassDirection = 1
    # direction for the lead part
    leadDirection= 1
    # next bar
    barCount = barCount + 1
    # final list we will write our parts to, this list will be read by the scheduler
    voices = [[0 for x in range(length)] for x in range(5)]
    # Create a diatonic scale
    scale = [0, 2, 4, 5, 7, 9, 11]
    # repeat over full 0-127 midi range
    scale = spreadNotes(scale)
    # transpose to our key
    scale = [(x+key) for x in scale]
    # The following part will fill rhythmlist with a syncopated rhythm that will hold all the parts together
    rhythmlist = [0 for i in range(length)]
    for i in range(int(length/2)):
        if timepassed > 2 and random.randint(0, timepassed+1) != 0:
            # decide if we want syncopation
            if random.randint(0, 2) != 0:
                # first we build a rhythm of 8th notes, then we move a few ones by a sixtheenth note
                # The longer there has been no accent, the larger the chance that we will have one now
                # 4 variables in this list, for 4 instruments!
                rhythmlist[i*2] = [int(random.randint(0, 2) != 0) for i in range(4)]
                rhythmlist[(i*2)+1] = [0, 0, 0, 0]
            else:
                rhythmlist[i*2] = [0, 0, 0, 0]
                rhythmlist[(i*2)+1] = [random.randint(0, 1) for i in range(4)]
            # set to 0 because we had a note
            timepassed = 0
        else:
            # silence
            rhythmlist[i*2] = [0, 0, 0, 0]
            rhythmlist[(i*2)+1] = [0, 0, 0, 0]
        timepassed = timepassed+1
    # check if we have chord progressions left
    if len(progressions) > 0:
        progression = progressions.pop(0)
    # if not (because Hooktheory cant keep up or we are in offline mode), use the backupchordgen
    else:
        progression = [backupchordgen() for i in range(6)]
    # Let's start making some music!
    # this for loop will run on each of the sixteenth notes in our specified length
    for i in range(length):
        # find out what we played last time
        lastparts = [lastplayed(parts[z], i) for z in range(len(parts))]
        # countlist contains timesig related accents
        x = countlist[i%len(countlist)]
        #Generate Chords in scale, this chance will decide when the changes happen
        if ((x%2 == 0 and random.randint(0, 3) == 0) or x == 0) and mode != 0 and len(progression) > 0:
            # prevent any weird responses from HookTheory from creeping in
            if isinstance(progression[0], list) == True:
                parts[4][i] = [note+60+key for note in progression.pop(0)]
                change = 1
            else:
                # if that happens just go with it and use the previous chord
                parts[4][i] = parts[4][i-1]
                change = 0
            # also use the previous chord if there is no chordchange
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
            #
            rootnotes = spreadNotes([parts[4][i][0]])
            fullchord = spreadNotes(parts[4][i])
        except TypeError as e:
            # Maybe I fixed this already, i havent encountered the error in a while...
            # Scared to take it out though
            print('error:', parts[4][i], e)
        # BASS
        # Check if we want to write a whole new part or make changes to the previous part
        if random.randint(0, 2) == 0 or mode != 0:
            # Use rhythmlist to decide if we want a bassnote, then add a random chance for variation
            if rhythmlist[i][0] == 1 or random.randint(0, 2) == 0:
                # Change direction if we get too high or low
                if lastparts[0][1] > 48:
                    bassDirection = -1
                elif lastparts[0][1] < 36:
                    bassDirection = 1
                # On some strong beats, play the root of the chord
                if (x % 8 == 0 and random.randint(0, 1) == 0) or (change == 1 and random.randint(0,1) == 0):
                    parts[0][i] = movement(lastparts[0][1], rootnotes, 0)
                # slightly less strong, chordtones
                elif x % 2 == 0:
                    parts[0][i] = movement(lastparts[0][1], fullchord, bassDirection)
                # weak beats get scale tones
                elif x % 2 == 1 and random.randint(0, 1) == 0:
                    parts[0][i] = movement(lastparts[0][1], scale, bassDirection)
                # sometimes we want an octave jump because funk bass players do that
                elif x % 8 == 0 and random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, (8*bassDirection)), fullchord, 0)
                # we can also jump in fourths or fifths
                elif random.randint(0, 1) == 0:
                    parts[0][i] = movement(movement(lastparts[0][1], scale, [-4, 5, 5][bassDirection+1]), fullchord, 0)
                # every now and then, a spice chromatic note, only do it if there is a note coming after this
                elif lengthgenerator(parts[0])[i] == 0:
                    parts[0][i] = lastparts[0][1]+bassDirection
                # if all these chances end up without a not, default to a chord tone
                else:
                    parts[0][i] = movement(lastparts[0][1], fullchord, bassDirection)
                # Change direction after a jump
                if parts[0][i] != 0 and abs(lastparts[0][1]-parts[0][i]) > 2:
                    bassDirection = bassDirection*-1
                # If we octave jump down from a low point we can accidentally get in bad situations
                # So if we are too far from home we correct the octave
                if parts[0][i] != 0 and (parts[0][i] > 50 or parts[0][i] < 30):
                    parts[0][i] = parts[0][i]%24+36
            # Or play nothing
            else:
                 parts[0][i] = 0
        # LEAD
        # The lead always changes its part completely, while bass, drums and keys will repeat a pattern
        # This simulates the behavior of a lead player improvising with a backing band
        if i == 0:
            parts[1] = [0 for x in range(length)]
        # Adding silence to make some nice phrases
        if i % 8 == 0:
            silence = random.randint(0, 5) == 0
        # chance that decides if there will be a lead note
        if (rhythmlist[i][1] == 1 or random.randint(0, 1) == 0) and silence != 1:
            # sometimes you can get in strange situations where this is necessary
            if leadDirection != -1 and leadDirection != 1:
                leadDirection= 1
            # Switch directions if we are too high or low
            if lastparts[1][1] > 84:
                leadDirection= -1
            elif lastparts[1][1] < 60:
                leadDirection= 1
            # octave correction for large jumps at unfortunate times
            if (lastparts[1][1] > 100 or lastparts[1][1] < 48) and lastparts[1][1] != 0:
                lastparts[1][1] = lastparts[1][1]%12+60
            # chordtones on strong beats
            if x % 2 == 0:
                parts[1][i] = movement(lastparts[1][1], fullchord, leadDirection)
            # scaletones on weak beats
            elif x % 2 == 1 and random.randint(0, 3) != 0:
                parts[1][i] = movement(lastparts[1][1], scale, leadDirection)
            # Chromatic notes
            elif lengthgenerator(parts[0])[i] == 0:
                parts[1][i] = lastparts[1][1]+leadDirection
            # Root notes can happen but not too often
            elif x%4 == 0:
                parts[1][i] = movement(lastparts[1][1], rootnotes, 0)
                silence = random.randint(0, 1) == 0
            # change direction after a jump
            if parts[1][i] != 0 and abs(lastparts[1][1]-parts[1][i]) > 2 and lastparts[1][1] < 84 and lastparts[1][1] > 60:
                leadDirection= int(leadDirection/abs(leadDirection)*-1)
        # DRUMS
        # kick
        # Kicks are decided by the rhythmlist
        if rhythmlist[i][2] == 1:
            if x % 8 == 0 and random.randint(0, 3) != 0 or x%16 == 0 or random.randint(0, (1-(x%2))+5) == 0 or parts[0][i] != 0 and random.randint(0, 2) == 0:
                parts[2][i][0] = 36
            else:
                parts[2][i][0] = 0
            # Not too many kicks in a row
            if x >= 4 and (parts[2][i-1][0]+parts[2][i-2][0]+parts[2][i-3][0]+parts[2][i-4][0]) > 72:
                parts[2][i][0] = 0
        # Snares are decided by guided random chance
        elif (random.randint(0, 2) == 0 and mode == 0) or mode == 1:
            if x % 8 == 4 or random.randint(0, (x%2)+2) == 0 and random.randint(0, 1+abs(0-i)%4) == 2 or parts[2][i][1] > 0 and random.randint(0, 1+abs(0-i)%4) == 2:
                parts[2][i][1] = 38
        # Hats
        # Check if we left the hi-hat open last time, if so, close it
        if openhat == 1:
            parts[2][i][2] = 44
            openhat = 0
        # lets make some nice, semi-random parts for this
        elif random.randint(0, 1) == 0 or mode == 1:
            if random.randint(0, 7+(x%2)*5) == 0:
                openhat = 1
                parts[2][i][2] = 46
            elif parts[2][i][0] == 0 and parts[2][i][1] == 0 and random.randint(0, 1) == 0:
                parts[2][i][2] = 42
        # Toms, snares and cymbals for fills
        # only happen during fills
        if (fill == 1 and x > 16 and random.randint(0, 3) != 0) or mode == 2:
            fillchoice = random.randint(0, 8)+(i-16)
            note = [47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38, 47, 38, 47, 38, 47, 40, 45, 38, 38, 38, 69, 45, 38, 40, 40, 45, 38, 38, 45, 38, 38, 40, 43, 43, 38, 43, 40, 43, 38][fillchoice]
            parts[2][i][3] = note
        if mode != 0:
            parts[2][0][3] = random.choice([49, 50])
        # KEYS, this part has variable amount of notes, but normally around 4-6
        if mode != 0 or random.randint(0, 2) == 0 and i != length:
            if rhythmlist[i][3] == 1:
                # arrange function makes nice quasi-counterpoint voicing
                voicing = arrange(parts[4][i], lastparts[3][1][0:3], scale)
                if random.randrange(0, 2) == 0:
                    parts[3][i] = voicing
                    # add a lower note
                    parts[3][i].append(parts[3][i][0]-12)
                # sometimes, do those jazzy chromatic movements, only of there is a chord next on the sixtheenth
                elif lengthgenerator(parts[3])[i] == 0 and mode != 1 and i != length-1 and random.randint(0, 1) == 0:
                    chromatic = random.choice([-1, 1])
                    parts[3][i] = [z+chromatic for z in parts[3][i+1]]
                else:
                # switch between higher and lower voicings
                    parts[3][i] = [(voicing[y]%12)+60 for y in range(len(voicing))]
                    parts[3][i].append((parts[3][i][0]%12)+48)
#            else:
#                parts[3][i] = []
    # Generate velocity list
    velocity = [random.randint(80, ((1-x%2)*20)+97) for i in range(length)]
    # set some maximum lengths, there is no reason why a kick should be sustained, looks odd on a piano roll too
    lengthperpart = [8, 8, 2, 4, 2, 2, 2, 2]
    # Calculate the distance to the next note so we can determine the maximum duration of the note
    partdist = [lengthgenerator(parts[x]) for x in range(len(parts))]
    duration = [[y if y < lengthperpart[z] else lengthperpart[z] for y in partdist[z]] for z in range(len(partdist))]
    # Voice lists are made up of: [time in 16ths, note, velocity, length]
    # These will later be used for live midi playback or midi file output
    # In these lines we also apply the swing feel, velocity and semi-random duration of each note
    # Sorry for the long list comprehension, but I feel like it's not that hard to decipher if you know what each part is, and it is also the most efficient method in python (that's important because composer runs between bar changes)
    voices = [[[i+((i%2)*swing), x, velocity[i]+random.randint(-5, 5), random.randint(((duration[y][i]-2)+(1-i%2))+1, duration[y][i]+1+(1-i%2))] for i, x in enumerate(parts[y])] for y in range(len(parts))]
    # remember our output to we can export longer midi files
    history.append(voices)

# This is the scheduler function
def playseq():
    global events, endplay
    # list of events that we can write our notes to
    events = []
    # Time when the function starts, for later comparision
    startTime = time.time()
    # Define note and measure lengths
    quarterNoteDuration = 60 / bpm
    sixteenthNoteDuration =  quarterNoteDuration / 4.0
    measureDuration = beatsPerMeasure  * quarterNoteDuration
    # We have 5 different instruments with their own midi outputs
    for i in range(5):
        # loop through all the notes in all the instruments
        for x in range(len(voices[i])):
            if voices[i][x][1] != 0:
                # Note-on
                events.append([voices[i][x][0] * sixteenthNoteDuration, voices[i][x][1], i, 1, voices[i][x][2]])
                # Note-off after duration
                events.append([(voices[i][x][0]+voices[i][x][3]) * sixteenthNoteDuration, voices[i][x][1], i, 0, voices[i][x][2]])
    # while there is something to play and we are not quitting
    while events and endplay == False:
        # Sort based on the first elements of the list
        events.sort(key=lambda x: x[0])
        # Current time to compare to starttime
        currentTime = time.time()
        # Note-offs can surpass the measureDuration, in that case we flush the midi notes and skip whatever was left
        if (currentTime - startTime >= measureDuration):
            break
        # Check if its time to play
        if (currentTime - startTime) >= events[0][0]:
            # Play the note!
            makenote(events[0][1], events[0][2], events[0][3], events[0][4])
            events.pop(0)
        else:
            # function that allows us to magically stop time
            pausesleep((events[0][0] - (currentTime - startTime))/2000)
    # compose here so we have a little bit more time before we need to start again
    compose()
    while endplay == False:
        currentTime = time.time()
        # check if the measure is over
        if(currentTime - startTime >= measureDuration):
            # End midi note-offs that cross our barline
            flush()
            # Do it again!
            playseq()
        else:
            pausesleep((measureDuration - (currentTime - startTime))/2000)

def pausesleep(arg):
    global pause
    while pause == 1:
        for event in events:
            # Move all event times so they don't all start playing when we unpause
            event[0] = event[0]+1
        # Check, move, sleep, repeat
        time.sleep(1)
    # if it's not paused, just wait as usual
    time.sleep(arg)

# MIDI TOOLS
#Midi tool to do note-ons and note-offs
# i is the Midi output it will be routed to, type can be 0 or 1 for note-off or note-on
# If takes both lists of notes (arrays) and single notes (ints)
def makenote(notes, i, type, velocity):
    # Note-on or Note-off
    action = [0x80, 0x90][type]
    # If we send one note, place it in an array
    if isinstance(notes, int) or isinstance(notes, float):
        notes = [notes]
    # Play all the sent notes
    for note in notes:
        if note > 0:
                midiouts[i].send_message([action, note, velocity])

def savemidi():
    global length
    print('How many bars would you like to save?')
    hist = custom_input('int', 1, 50)
    # create a list that is as long as the user wanted
    if hist > len(history):
        # Create new parts if they requested more bars than we had ready
        for i in range((hist - len(history))+1):
            compose()
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    # select the right part of our history and flip it
    histlist = history[int(hist*-1):][::-1]
    # I get errors if I deinterleave, but this works
    mf = MIDIFile(len(parts), deinterleave=False)
    time = 0
    # prepare for 5 instruments
    for i in range(len(parts)):
        # make tracks for each instrument
        mf.addTrackName(i, 0, tracknames[i])
        mf.addTempo(i, 0, bpm)
        channel = 0
        # cycle though our history, turn everything into midi
        for y in range(len(histlist)):
            for x in range(len(histlist[y][i])):
                if isinstance(histlist[y][i][x][1], int):
                    histlist[y][i][x][1] = [histlist[y][i][x][1]]
                for pitch in histlist[y][i][x][1]:
                    if pitch != 0:
                        volume = histlist[y][i][x][2]
                        time = (histlist[y][i][x][0]+(y*length))/4  #convert from beats to sixteenths
                        duration = abs(histlist[y][i][x][3])/4  # This doesn't seem to work somehow???
                        # add the note!!
                        mf.addNote(i, channel, pitch, time, duration, volume)
    filename = (input('Save As:') +  ".mid")
    with open(filename, 'wb') as outf:
        # Appearantly MIDIUtil is still pretty glitchy on python3
        # The fact that we give users the choice to export massive amounts of MIDI makes it a lot more likely for these errors to show up
        # Usually it still succesfully exports if we just except the error so whatever
        try:
            mf.writeFile(outf)
        except:
            print('An Error has occured when exporting MIDI')

# Custom input function so I can easily check if the input is correction
# Range can contain an array of possible input values, or a min and max value
def custom_input(type, *range):
    correct = 0
    # While we are not satisfied with the answer, keep asking!
    while correct == 0:
        try:
            value = input('> ').casefold() # Casefold to prevent case issues
            # Different checks for different types of input
            if type == 'int':
                    value = int(value)
                    #Check if in range
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

# UI function during playback to allow changes or go back to the main menu
def playmenu():
    global pause, barCount, bpm, timesigchoice, beatsPerMeasure, length, repeats, countlist, events, playthread, endplay, partmode
    while True:
        # Getting our input
        choice = custom_input('string', ['s', 'q', 'n', 'p', 'm'])
        # Handling it
        if choice == 's': # save midi
            pause = 1 # pause the playback
            flush() # no hanging notes
            savemidi()
            pause = 0
            playmenu()
        elif choice == 'q': # quit to main menu
            events = []
            endplay = 1
            flush()
            menu()
        elif choice == 'n': # create a new sequence with custom settings
            events = []
            endplay = 1
            barCount = 0
            flush()
            composerSetup()
            endplay = 0
            partmode = 1
            playthread = threading.Thread(target=playseq)
            playthread.daemon = True
            playthread.start()
            playmenu()
        elif choice == 'm': # Varying keys and tempo
            if partmode == 0:
                print('Varying keys and tempo are now turned on')
            else:
                print('Varying keys and tempo are now turned off')
            partmode = 1-partmode
            playmenu()
        elif choice == 'p': # Play/pause
            if pause == 0:
                print('Paused, press p to start playing')
            else:
                print('Playing, press p to pause')
            pause = 1-pause
            flush()
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
# Also adds some extentions
def arrange(chord, lastchord, scale):
    # First, sort them
    chord.sort()
    lastchord.sort()
    # Get the the outer interval and prevent parallel fifths
    outerdistance = interval(lastchord[0], lastchord[2])[0]
    if outerdistance == 6 and chord != lastchord:
        options = [[12, 0, 0], [0, 0, -12], [0, 0, 0]]
    else:
        options = [[12, 0, 0], [0, 0, -12]]
    # Find the inversion that is closest to the last chord
    distlist = [0 for i in range(len(options))]
    for i in range(len(options)):
        for x in range(3):
            options[i][x] = options[i][x] + chord[x]
            if options[i][x] > 84 or options[i][x] < 60:
                distlist[i] + distlist[i] + 3
            distlist[i] = distlist[i] + abs(options[i][x] - lastchord[x])
    random.shuffle(options)
    bestchord = options[distlist.index(min(distlist))]
    # add some extentions
    extlst = [[6, 7, 9, 11], [7, 9], [7], [6, 7], [7, 9, 11, 13], [7, 9], [7]][interval(scale[0], chord[0])[0]%7]
    extentionchoice = random.sample(set(extlst), random.randint(1, len(extlst)))
    extended = bestchord + [movement(chord[0], scale, i) for i in extentionchoice]
    extended.sort()
    return extended

# This function reads our 'parts' syntax to determine what the last note was from the specified index
def lastplayed(lst, index):
    matchlist = [index-i if (isinstance(x, int) and x != 0 or isinstance(x, list) and sum(x) != 0) and index-i>0 else 999 for i, x in enumerate(lst)]
    mindex = matchlist.index(min(matchlist))
    minval = lst[mindex]
    return [index-mindex, minval]

# This function reads our 'parts' syntax to determine how far away the next note is
# We use this to determine our note durations and place chromatic passing tones
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
    while True and offlinemode == 0:
        if len(progressions) < 4:
            # chordIDs will be written in a way that hooktheory understands it
            chordIDs = str(random.randint(1, 6))
            progression = [0 for x in range(4)]
            # These IDs are pretty hard to decipher... So I made a function for it
            progression[0] = translatechord(chordIDs[0])
            for x in range(4):
                try:
                    # Prevents going over the 10 chords per 10 seconds rule
                    time.sleep(0.5)
                    receivedchord = ht.getChords(chordIDs).json()
                # Sometimes the HookTheory API doesn't pass a valid value, nothing else I can do but except the error ¯\_(ツ)_/¯
                except json.decoder.JSONDecodeError:
                    print('Intercepted HookTheory Error: 0 (invalid response)')
                    break
                # When our login fails, we find out here, and ask again
                except AssertionError:
                    correct = 0
                    while correct == 0:
                        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                        print('Invalid login credentials, do you want to try again? (y/n)')
                        correct = ['y', 'n'].index(custom_input('string', ['y', 'n']))
                        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                        # If you dont want to try again
                        if correct == 1:
                            offlinemode = 1
                            progressions = [[backupchordgen() for i in range(6)] for i in range(4)]
                            sys.exit()
                        # If you do want to try again
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
                # Hooktheory gives us a dictionary with all the possible next chords and the chance of that chord
                options = [[]  for i in range(len(receivedchord))]
                # Generate a random number between 0 and the highest probability number in the list
                chordprob = random.random()*receivedchord[-1]['probability']
                totalprob = 0
                for i in range(len(options)):
                    # Hooktheory has a 10 requests per 10 seconds maximum, the SDK should automatically enforce this but somehow it still goes wrong Sometimes
                    # I introduced some extra sleep time and also excepted the error just to be safe
                    try:
                        # make a probability table in range 0-1 so we can pick a random number to decide
                        options[i] = [[totalprob, receivedchord[i]['probability']+totalprob], receivedchord[i]['chord_ID']]
                        totalprob = options[i][0][1]
                    except KeyError as e:
                        print('Intercepted HookTheory Error: 1 (too many requests)')
                        break
                    # find out what chord we picked
                    if chordprob >= options[i][0][0] and chordprob <= options[i][0][1]:
                        chord = options[i][1]
                # This is the way Hooktheory wants their requests
                chordIDs = chordIDs + "," + chord
                # Add it to our current progression list!
                progression[x] = translatechord(chord)
                # move our progressbar
                progbar = progbar + 1
            # Add the progression to the global progressions list
            progressions.append(progression)

# This function turns HookTheory's cryptic chordIDs in to midi notes
def translatechord(chrd):
    inversions = {"0" : [0, 2, 4], "6" : [2, 4, 0], "64" : [4, 0, 2], "7" : [0, 2, 4, 6], "65" : [2, 4, 6, 0], "43" : [4, 6, 0, 2], "42" : [6, 0, 2, 4]}
    # Everything after the slash is a transposition
    chord = chrd.split('/')
    # If it starts with a letter we are dealing with modal interchange
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
        # If it starts with a number, it's a chord degree
        mode = 0
        degree = chord[0][0]
        # using variable lengths for notating inversions seems like a great idea...
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
    # place it on a scale
    scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]
    # deal with modal interchange
    smode = scale[mode]
    scale = [(x-smode) for x in scale]
    # add it all together
    finalchord = [(scale[(int(degree)-1+mode+int(i))%14]+scale[int(extention)-1])%24 for i in inversion]
    # Rare cases where finalchord doesn't come out as a list but as an integer. Probably something to do with the chord_ID decoder, I'll fix this later
    # This will work for now though
    if isinstance(finalchord, list):
        return finalchord
    else:
        print('Intercepted HookTheory Error: 2')

# Very basic chord generator for offline mode
def backupchordgen():
    global key, chordchoice
    scale = [0, 2, 4, 5, 7, 9, 11]
    scale  = spreadNotes(scale)
    # List of possible follow-up chords for each chord
    options = [[0, 5], [4, 6], [5], [4, 6], [0, 5], [1, 3], [0, 5]][chordchoice]
    chordchoice = random.choice(options)
    # place it on our scale
    scalepos = scale[chordchoice]
    # return our chord!
    return [movement(scalepos, scale, 0), movement(scalepos, scale, 2), movement(scalepos, scale, 4), movement(scalepos, scale, 6)]

# Flush midinotes
def flush():
    global events
    # send note-offs at all notes on all channels
    for x in range(5):
        for i in range(128):
            makenote(i, x, 0, 0)

# welcome banner we only want when starting up
print("\x1b[8;24;80t")
print("\n\n\n\n\n\n\n")
print(" ______________________________________________________________________________\n")
print("                               Welcome to PyFunk!                            \n")
print(" ______________________________________________________________________________\n\n\n\n\n\n\n")

# flush when we quit
atexit.register(flush)

# Go!!
welcome()
