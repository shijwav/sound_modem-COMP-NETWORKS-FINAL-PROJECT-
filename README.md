# sound_modem-COMP-NETWORKS-FINAL-PROJECT-


Section 1 — Explanation:

This project implements an acoustic modem that transmits text data over sound using Frequency Shift Keying (FSK) modulation — the same technique used by dial-up modems. It demonstrates the Physical Layer (Layer 1) of the OSI model, where raw bits are encoded as physical signals. Real-world systems that use this same principle include dial-up modems (V.22/V.34), DTMF telephone tones, and underwater acoustic communication networks.

Section 2 — Implementation:

The system has three components: a sender, a receiver, and a loopback demo. The sender converts text to 8-bit ASCII, then plays each bit as either a 1000 Hz tone (0) or 2000 Hz tone (1) through the speaker, preceded by a 500 Hz preamble to signal the start of a message. Each bit lasts 80ms giving ~12.5 bits/second throughput. The receiver records audio, splits it into 80ms chunks, runs an FFT on each chunk to find the dominant frequency, and maps it back to a 0 or 1. Tools used: Python 3, numpy (signal generation + FFT), sounddevice (audio I/O), scipy.

Section 3 — Demonstration:

<img width="565" height="413" alt="Screenshot from 2026-05-15 20-52-06" src="https://github.com/user-attachments/assets/368e0776-230a-4142-89c0-b19f8d54076d" />
<img width="1228" height="435" alt="Screenshot from 2026-05-15 20-55-18" src="https://github.com/user-attachments/assets/dc880e37-0c7c-406b-8fcb-84bc1fe0e624" />
<img width="551" height="840" alt="Screenshot from 2026-05-15 20-51-52" src="https://github.com/user-attachments/assets/18a564f3-ca9c-4e17-b301-c4ca27a71b12" />

