# image_stego.py
from PIL import Image
import numpy as np
import os

# Utility helpers reused across modules
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

# ----------------- LSB -----------------
def hide_lsb_image(img_path, message, output_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    bits = build_binary_with_header(message)
    img = Image.open(img_path).convert("RGB")
    pixels = np.array(img, dtype=np.uint8).copy()
    flat_pixels = pixels.ravel()
    if len(bits) > len(flat_pixels):
        raise ValueError("Message too large for image")
    for i, bit in enumerate(bits):
        flat_pixels[i] = (int(flat_pixels[i]) & 0xFE) | int(bit)
    pixels = flat_pixels.reshape(pixels.shape)
    Image.fromarray(pixels).save(output_path)
    return output_path

def extract_lsb_image(img_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    img = Image.open(img_path).convert("RGB")
    flat = np.array(img, dtype=np.uint8).ravel()
    bits = ''.join(str(int(x) & 1) for x in flat)
    if len(bits) < 32:
        return ''
    header_bits = bits[:32]
    length = int(header_bits, 2)
    total_bits_needed = 32 + length * 8
    if len(bits) < total_bits_needed:
        return ''
    message_bits = bits[32:32 + length * 8]
    return bits_to_message_by_length(message_bits, length)

# ----------------- Parity -----------------
def hide_parity_image(img_path, message, output_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    bits = build_binary_with_header(message)
    img = Image.open(img_path).convert("RGB")
    pixels = np.array(img, dtype=np.uint8).copy()
    flat = pixels.ravel()
    if len(bits) > len(flat):
        raise ValueError("Message too large for image")
    for i, bit in enumerate(bits):
        b = int(flat[i])
        parity = bin(b).count('1') % 2
        if parity != int(bit):
            flat[i] ^= 1
    pixels = flat.reshape(pixels.shape)
    Image.fromarray(pixels).save(output_path)
    return output_path

def extract_parity_image(img_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    img = Image.open(img_path).convert("RGB")
    flat = np.array(img, dtype=np.uint8).ravel()
    bits = ''.join(str(bin(int(x)).count('1') % 2) for x in flat)
    if len(bits) < 32:
        return ''
    header_bits = bits[:32]
    length = int(header_bits, 2)
    total_bits_needed = 32 + length * 8
    if len(bits) < total_bits_needed:
        return ''
    message_bits = bits[32:32 + length * 8]
    return bits_to_message_by_length(message_bits, length)

# ----------------- Bit Plane -----------------
def hide_bitplane_image(img_path, message, output_path, plane=1):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    bits = build_binary_with_header(message)
    img = Image.open(img_path).convert("RGB")
    pixels = np.array(img, dtype=np.int32).copy()
    flat = pixels.ravel()
    if len(bits) > len(flat):
        raise ValueError("Message too large for image")
    for i, bit in enumerate(bits):
        mask = 1 << plane
        if int(bit) == 1:
            flat[i] = int(flat[i]) | mask
        else:
            flat[i] = int(flat[i]) & (~mask)
    pixels = flat.reshape(pixels.shape)
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    Image.fromarray(pixels).save(output_path)
    return output_path

def extract_bitplane_image(img_path, plane=1):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image path not found")
    img = Image.open(img_path).convert("RGB")
    flat = np.array(img, dtype=np.uint8).ravel()
    bits = ''.join(str((int(b) >> plane) & 1) for b in flat)
    if len(bits) < 32:
        return ''
    length = int(bits[:32], 2)
    total = 32 + length * 8
    if len(bits) < total:
        return ''
    message_bits = bits[32:32 + length * 8]
    return bits_to_message_by_length(message_bits, length)
