import simpleaudio as sa

def play(n, audiofile="audio.wav"):
    if n == 0:
        return()
    else:
        wave_obj = sa.WaveObject.from_wave_file(audiofile)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        play(n - 1 , audiofile)
