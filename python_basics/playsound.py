import simpleaudio as sa

#Play function
def play(n, audiofile="audio.wav"):
    # Load audio file
    wave_obj = sa.WaveObject.from_wave_file(audiofile)
    # Loop play function n times
    for i in range(n):
        play_obj = wave_obj.play()
        play_obj.wait_done()
