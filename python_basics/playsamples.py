import simpleaudio as sa
import time

def playsample(bpm, *args):
    for arg in args:

        wave_obj = sa.WaveObject.from_wave_file("audio.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()
        time.sleep (float (arg) * (float (60) / bpm))
