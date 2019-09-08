# Python markov input tool
import rtmidi
import numpy as np

midiin = rtmidi.MidiIn()
midiin.open_virtual_port('Markov Input')

order = 3
#kut
chain = np.zeros(([order, 12, 12]))
print(chain)
