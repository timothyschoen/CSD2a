import simpleaudio as sa
import time

def playsample(bpm, *args):
    # Loop through all the wait times
    for arg in args:
        #Load Sample
        wave_obj = sa.WaveObject.from_wave_file("audio.wav")
        #Play sample
        play_obj = wave_obj.play()
        # Sleep time, converted from note to time
        time.sleep (float (arg) * (60 / bpm))

# Driver code:
# playsample(135, 1, 1, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 1, 1, 1, 1)
