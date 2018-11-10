import simpleaudio as sa
import time
import random

"""
An example project in which a sequence (one measure, multiple samples) is played.
  - Sixteenth note is the smallest used note duration.
  - One meassure, time signature: 3 / 4
Instead of using steps to iterate through a sequence, we are checking the time.
We will trigger events based on their eventtime.
------ HANDS-ON TIPS ------
- Answer the following questions before running the code:
  - Line 74 is outcommented. However, this line is essential to enable correct
    playback of the sequence.
    Read the code: what will go wrong?
    Check your answer by running the script with the line outcommented.

    Zonder line 74 worden de events niet gesorteert
    Hierdoor zullen de getallen niet op volgorde van grootte staan, waardoor het probleem ontstaat
    dat python de noten niet verwerkt op volgorde van tijd, maar op de volgorde waarop ze
    toevallig staan. Noot 3 zou bijvoorbeeld gespeeld moeten worden, terwijl python wacht tot een latere noot
    aan de beurt is.

  - Remove the [#] at the of the line, what will happen now?
    Check your answer by running the script.

    Nu slaat hij geen noten meer over, wat hij eerst wel deed

- Add comments:
  A few comments are missing in this script.
  The lines: 63, 67, 71 contain the numbers 0, 1, 2, and are added to the
  timeEvents list. To 'what' do these numbers refer?
  Add meaningfull comments.
- Alter the code:
  Currently the sequence is only played once.
  Alter the code to play it multiple times.
  hint: The events list is emptied using the pop() function.
"""

#______________________________________________________________________________
# NOTE: THIS SCRIPT CONTAINS DUPLICATE CODE = USEFULL EXAMPLE, SEE HANDS-ON TIPS
#______________________________________________________________________________

# load 3 audioFiles and store it into a list
samples = [ sa.WaveObject.from_wave_file("audio.wav"),
            sa.WaveObject.from_wave_file("snare.wav"),
            sa.WaveObject.from_wave_file("cb.wav"), ]

# set bpm
bpm = 120
# calculate the duration of a quarter note
quarterNoteDuration = 60 / bpm
# calculate the duration of a sixteenth note
sixteenthNoteDuration = quarterNoteDuration / 4.0
# number of beats per sequence (time signature: 3 / 4 = 3 beats per sequence)
beatsPerMeasure = 3
# calculate the duration of a measure
measureDuration = beatsPerMeasure  * quarterNoteDuration

# create a list to hold the events
events = []
# create lists with the moments (in 16th) at which we should play the samples
sequence1 = [0, 2, 4, 8, 11]
sequence2 = [3, 6, 10]
sequence3 = [5, 9]

# transform the sixteenthNoteSequece to an eventlist with time values
# After each event in the list, a number (0, 1 or 2) will be appended to indicate which sample must be played
def playsequence(n):
    for sixteenNoteIndex in sequence1:
        events.append([sixteenNoteIndex * sixteenthNoteDuration, 0])
    # transform the sixteenthNoteSequece to an eventlist with time values
    for sixteenNoteIndex in sequence2:
        events.append([sixteenNoteIndex * sixteenthNoteDuration, 1])
    # transform the sixteenthNoteSequece to an eventlist with time values
    for sixteenNoteIndex in sequence3:
        events.append([sixteenNoteIndex * sixteenthNoteDuration, 2])
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
        # play sample -> sample index is at index 1
        samples[event[1]].play()
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
            gottaRepeat = False
            # check if we've reached n
            if n > 1:
                # if we havent, play again
                playsequence(n - 1)
            else:
                # else stop the program
                return()
        else:
            time.sleep(0.001)
