import numpy as np
import sys
import math

SAMPLE_RATE       = 44100
BIT_DURATION      = 0.08
FREQ_ZERO         = 1000
FREQ_ONE          = 2000
FREQ_PREAMBLE     = 500
PREAMBLE_DURATION = 0.3
FREQ_TOLERANCE    = 150
AMPLITUDE         = 0.7

def make_tone(freq, duration):
    t    = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    fade = int(SAMPLE_RATE * 0.005)
    wave = AMPLITUDE * np.sin(2 * np.pi * freq * t).astype(np.float32)
    if fade > 0:
        wave[:fade]  *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)
    return wave

def dominant_freq(chunk):
    windowed = chunk * np.hanning(len(chunk))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs    = np.fft.rfftfreq(len(chunk), d=1.0 / SAMPLE_RATE)
    return float(freqs[np.argmax(spectrum)])

def near(freq, target):
    return abs(freq - target) < FREQ_TOLERANCE

def text_to_bits(text):
    bits = []
    for char in text:
        byte = ord(char)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

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

def encode_message(message):
    chunks = [make_tone(FREQ_PREAMBLE, PREAMBLE_DURATION)]
    for bit in text_to_bits(message):
        chunks.append(make_tone(FREQ_ONE if bit else FREQ_ZERO, BIT_DURATION))
    silence = np.zeros(int(SAMPLE_RATE * BIT_DURATION * 2), dtype=np.float32)
    chunks.append(silence)
    return np.concatenate(chunks)

def decode_audio(audio, message_len):
    CHUNK         = int(SAMPLE_RATE * BIT_DURATION)
    PREAMBLE_HOLD = math.ceil(PREAMBLE_DURATION / BIT_DURATION)
    preamble_count = 0
    found_preamble = False
    bits           = []
    for i in range(len(audio) // CHUNK):
        chunk = audio[i * CHUNK : (i + 1) * CHUNK]
        freq  = dominant_freq(chunk)
        if not found_preamble:
            if near(freq, FREQ_PREAMBLE):
                preamble_count += 1
                if preamble_count >= PREAMBLE_HOLD:
                    found_preamble = True
            else:
                preamble_count = 0
        else:
            if near(freq, FREQ_ONE):
                bits.append(1)
            elif near(freq, FREQ_ZERO):
                bits.append(0)
            if len(bits) == message_len * 8:
                break
    return bits_to_text(bits)

def run_demo(message):
    print("=" * 60)
    print("       SOUND MODEM — LOOPBACK DEMO")
    print("=" * 60)
    print(f"\n[SENDER]   Original message : '{message}'")
    bits = text_to_bits(message)
    print(f"[SENDER]   Total bits       : {len(bits)}")
    print(f"[SENDER]   Frequencies      : 0→{FREQ_ZERO}Hz  1→{FREQ_ONE}Hz  preamble→{FREQ_PREAMBLE}Hz")
    print("\n[ENCODER]  Building audio waveform …")
    audio    = encode_message(message)
    duration = len(audio) / SAMPLE_RATE
    print(f"[ENCODER]  Waveform length  : {len(audio)} samples  ({duration:.2f}s)")
    print("\n[DECODER]  Decoding waveform …")
    result = decode_audio(audio, len(message))
    print(f"[DECODER]  Recovered message: '{result}'")
    match  = result == message
    errors = 0 if match else sum(a != b for a, b in zip(text_to_bits(message), text_to_bits(result)))
    print(f"\n{'='*60}")
    print(f"  Bit Error Rate : {errors}/{len(bits)} errors  ({errors/len(bits):.1%})")
    print(f"  Match          : {'✓ PERFECT' if match else '✗ MISMATCH'}")
    print(f"{'='*60}")
    print("\n  Frequency timeline (first 40 bits):")
    print("  ", end="")
    for b in bits[:40]:
        print("▀" if b else "░", end="")
    print(f"\n  (▀={FREQ_ONE}Hz=1  ░={FREQ_ZERO}Hz=0)\n")

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello Network!"
    run_demo(msg)
