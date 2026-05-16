import numpy as np
import sounddevice as sd
import sys

SAMPLE_RATE       = 44100
BIT_DURATION      = 0.08
FREQ_ZERO         = 1000
FREQ_ONE          = 2000
FREQ_PREAMBLE     = 500
PREAMBLE_DURATION = 0.3
FREQ_TOLERANCE    = 150
PREAMBLE_HOLD     = 2
MAX_CHARS         = 256
LISTEN_TIMEOUT    = 30

CHUNK_SIZE = int(SAMPLE_RATE * BIT_DURATION)

def dominant_freq(chunk):
    windowed = chunk * np.hanning(len(chunk))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs    = np.fft.rfftfreq(len(chunk), d=1.0 / SAMPLE_RATE)
    return float(freqs[np.argmax(spectrum)])

def near(freq, target):
    return abs(freq - target) < FREQ_TOLERANCE

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        if byte == 0:
            break
        if 32 <= byte <= 126:
            chars.append(chr(byte))
    return "".join(chars)

def receive_message():
    print("[RECEIVER] Listening … (start sender now)")
    print(f"[RECEIVER] Timeout in {LISTEN_TIMEOUT}s  |  Ctrl-C to quit\n")
    total_chunks = int(LISTEN_TIMEOUT * SAMPLE_RATE / CHUNK_SIZE)
    audio = sd.rec(
        total_chunks * CHUNK_SIZE,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    preamble_count = 0
    found_preamble = False
    bits           = []
    decoded        = ""
    for i in range(total_chunks):
        sd.sleep(int(BIT_DURATION * 1000))
        chunk = audio[i * CHUNK_SIZE : (i+1) * CHUNK_SIZE, 0]
        if len(chunk) < CHUNK_SIZE:
            break
        freq = dominant_freq(chunk)
        if not found_preamble:
            if near(freq, FREQ_PREAMBLE):
                preamble_count += 1
                if preamble_count >= PREAMBLE_HOLD:
                    print("[RECEIVER] Preamble detected — receiving …")
                    found_preamble = True
            else:
                preamble_count = 0
        else:
            if near(freq, FREQ_ONE):
                bits.append(1)
            elif near(freq, FREQ_ZERO):
                bits.append(0)
            if len(bits) % 8 == 0 and len(bits) > 0:
                decoded = bits_to_text(bits)
                sys.stdout.write(f"\r[RECEIVER] Received: '{decoded}'   ")
                sys.stdout.flush()
            if len(decoded) >= MAX_CHARS:
                break
    sd.stop()
    print(f"\n[RECEIVER] Final message: '{decoded}'")
    return decoded

if __name__ == "__main__":
    receive_message()
