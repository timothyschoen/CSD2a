import simpleaudio as sa

def play(audiofile,n):
    wave_obj = sa.WaveObject.from_wave_file(audiofile)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    if n=0:
        return()
        play(audiofile , n - 1)
