# audio_stego.py
import wave
import os
import struct
import numpy as np

# Utilities
def build_binary_with_header(message):
    length = len(message.encode('utf-8'))
    header = format(length, '032b')
    payload = ''.join(format(b, '08b') for b in message.encode('utf-8'))
    return header + payload

def bits_to_message_by_length(bits, byte_length):
    needed = byte_length * 8
    if len(bits) < needed:
        return None
    message = ''
    for i in range(0, needed, 8):
        byte = bits[i:i+8]
        message += chr(int(byte, 2))
    try:
        return bytes([ord(c) for c in message]).decode('utf-8', errors='replace')
    except Exception:
        return message

# ---------------- LSB ----------------
def hide_audio_lsb(wav_path, message, output_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    bits = build_binary_with_header(message)
    with wave.open(wav_path, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
    samples = bytearray(frames)
    if len(bits) > len(samples):
        raise ValueError('Message too long for audio')
    for i, bit in enumerate(bits):
        samples[i] = (samples[i] & 0xFE) | int(bit)
    with wave.open(output_path, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(bytes(samples))
    return output_path

def extract_audio_lsb(wav_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    with wave.open(wav_path, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
    samples = bytearray(frames)
    bits = ''.join(str(samples[i] & 1) for i in range(len(samples)))
    if len(bits) < 32:
        return ''
    length = int(bits[:32], 2)
    total = 32 + length * 8
    if len(bits) < total:
        return ''
    message_bits = bits[32:32 + length * 8]
    return bits_to_message_by_length(message_bits, length)

# ---------------- Parity ----------------
def hide_audio_parity(wav_path, message, output_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    bits = build_binary_with_header(message)
    with wave.open(wav_path, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
    samples = bytearray(frames)
    if len(bits) > len(samples):
        raise ValueError('Message too long')
    for i, bit in enumerate(bits):
        parity = bin(samples[i]).count('1') % 2
        if parity != int(bit):
            samples[i] ^= 1
    with wave.open(output_path, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(bytes(samples))
    return output_path

def extract_audio_parity(wav_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
    samples = bytearray(frames)
    bits = ''.join(str(bin(s).count('1') % 2) for s in samples)
    if len(bits) < 32:
        return ''
    length = int(bits[:32], 2)
    total = 32 + length * 8
    if len(bits) < total:
        return ''
    message_bits = bits[32:32 + length * 8]
    return bits_to_message_by_length(message_bits, length)

# ---------------- Phase (mono 16-bit support) ----------------
def hide_audio_phase(wav_path, message, output_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    bits = build_binary_with_header(message)
    try:
        with wave.open(wav_path, 'rb') as wav:
            params = wav.getparams()
            n_channels, sampwidth, framerate, n_frames, comptype, compname = params
            frames = wav.readframes(n_frames)
            if sampwidth != 2:
                raise ValueError("Only 16-bit PCM WAV supported.")
            audio = np.frombuffer(frames, dtype=np.int16)
            if n_channels > 1:
                audio = audio.reshape(-1, n_channels)
                audio = np.mean(audio, axis=1).astype(np.int16)
    except Exception as e:
        raise RuntimeError(f"Error reading WAV: {e}")

    if len(bits) > audio.size // 2:
        raise ValueError("Message too large for this audio file.")

    audio_fft = np.fft.fft(audio)
    magnitude = np.abs(audio_fft)
    phase = np.angle(audio_fft)

    max_bins = len(phase)//2
    if len(bits) > max_bins:
        raise ValueError("Message too large for available phase bins.")

    for i, bit in enumerate(bits, start=1):
        phase[i] = 0.0 if bit == '0' else (np.pi / 2)
        phase[-i] = -phase[i]

    modified_fft = magnitude * np.exp(1j * phase)
    modified_audio = np.fft.ifft(modified_fft).real
    modified_audio = np.round(modified_audio).astype(np.int16)

    try:
        with wave.open(output_path, 'wb') as out_wav:
            out_wav.setparams((1, 2, framerate, len(modified_audio), comptype, compname))
            out_wav.writeframes(modified_audio.tobytes())
    except Exception as e:
        raise RuntimeError(f"Error writing WAV file: {e}")
    return output_path

def extract_audio_phase(wav_path):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    try:
        with wave.open(wav_path, 'rb') as wav:
            n_channels, sampwidth, framerate, n_frames, comptype, compname = wav.getparams()
            frames = wav.readframes(n_frames)
            if sampwidth != 2:
                raise ValueError("Only 16-bit PCM WAV supported.")
            audio = np.frombuffer(frames, dtype=np.int16)
            if n_channels > 1:
                audio = audio.reshape(-1, n_channels)
                audio = np.mean(audio, axis=1).astype(np.int16)
    except Exception as e:
        raise RuntimeError(f"Error reading WAV: {e}")

    audio_fft = np.fft.fft(audio)
    phase = np.angle(audio_fft)

    max_bins = len(phase)//2
    raw_bits = []
    for i in range(1, max_bins):
        p = phase[i]
        if abs(p) < (np.pi/4):
            raw_bits.append('0')
        elif abs(abs(p) - (np.pi/2)) < (np.pi/4):
            raw_bits.append('1')
        else:
            raw_bits.append('0')

    if len(raw_bits) < 32:
        return ''

    header_bits = ''.join(raw_bits[:32])
    length = int(header_bits, 2)
    total_needed = 32 + length * 8
    if len(raw_bits) < total_needed:
        return ''
    payload_bits = ''.join(raw_bits[32:32 + length * 8])
    return bits_to_message_by_length(payload_bits, length)

# ---------------- Echo ----------------
def hide_audio_echo(wav_path, message, output_path, delay_samples=120):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    message += "\0"
    bits = "".join(format(ord(c), "08b") for c in message)

    with wave.open(wav_path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())

    if params.sampwidth != 2:
        raise ValueError("Echo method expects 16-bit PCM WAV")

    fmt = "<" + "h" * (len(frames) // 2)
    samples = np.array(struct.unpack(fmt, frames), dtype=np.int16)

    step = delay_samples + 2
    max_bits = len(samples) // step
    if len(bits) > max_bits:
        raise ValueError("Message too long for audio (echo)")

    for i, bit in enumerate(bits):
        p = i * step
        idx = p + delay_samples
        if idx >= len(samples):
            break
        if bit == "1":
            samples[idx] = samples[p]
        else:
            samples[idx] = -samples[p]

    packed = struct.pack(fmt, *samples.tolist())
    with wave.open(output_path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(packed)
    return output_path

def extract_audio_echo(wav_path, delay_samples=120):
    if not os.path.exists(wav_path):
        raise FileNotFoundError("WAV file not found")
    with wave.open(wav_path, "rb") as wf:
        n_channels, sampwidth, framerate, n_frames = wf.getparams()[:4]
        frames = wf.readframes(n_frames)

    if sampwidth != 2:
        raise ValueError("Echo method expects 16-bit PCM WAV")

    fmt = "<" + "h" * (len(frames) // 2)
    samples = np.array(struct.unpack(fmt, frames), dtype=np.int16)

    step = delay_samples + 2
    nbits = len(samples) // step
    bits = ""

    for i in range(nbits):
        p = i * step
        idx = p + delay_samples
        if idx >= len(samples):
            break
        a = int(samples[p])
        b = int(samples[idx])

        if a == 0 or b == 0:
            bit = "0"
        else:
            same_sign = (a >= 0 and b >= 0) or (a < 0 and b < 0)
            bit = "1" if same_sign else "0"

        bits += bit
        if len(bits) >= 8 and bits.endswith("00000000"):
            break

    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            break
        c = chr(int(byte, 2))
        if c == "\0":
            return message
        message += c
    return message
