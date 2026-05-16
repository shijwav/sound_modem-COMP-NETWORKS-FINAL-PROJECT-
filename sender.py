import numpy as np
import sounddevice as sd
import sys

SAMPLE_RATE   = 44100
BIT_DURATION  = 0.08
FREQ_ZERO     = 1000
FREQ_ONE      = 2000
FREQ_PREAMBLE = 500
PREAMBLE_DURATION = 0.3
AMPLITUDE     = 0.7

def make_tone(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    fade = int(SAMPLE_RATE * 0.005)
    wave = AMPLITUDE * np.sin(2 * np.pi * freq * t)
    wave[:fade]  *= np.linspace(0, 1, fade)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return wave.astype(np.float32)

def text_to_bits(text):
    bits = []
    for char in text:
        byte = ord(char)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def send_message(message):
    print(f"[SENDER] Message : '{message}'")
    bits = text_to_bits(message)
    print(f"[SENDER] Bits    : {len(bits)} bits")
    print("[SENDER] Playing …")
    chunks = [make_tone(FREQ_PREAMBLE, PREAMBLE_DURATION)]
    for bit in bits:
        freq = FREQ_ONE if bit == 1 else FREQ_ZERO
        chunks.append(make_tone(freq, BIT_DURATION))
    audio = np.concatenate(chunks)
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()
    print("[SENDER] Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        msg = input("Enter message to send: ")
    else:
        msg = " ".join(sys.argv[1:])
    send_message(msg)
