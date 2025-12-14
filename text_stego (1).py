# text_stego.py
ZWSP = '\u200b'
ZWNJ = '\u200c'

# ---------------- Zero-Width (ZW) ----------------
def hide_zw(cover_text, message):
    message += "\0"
    bits = ''.join(format(ord(c), '08b') for c in message)
    result = list(cover_text)
    insert_pos = 0
    for bit in bits:
        while insert_pos < len(result) and result[insert_pos] == ' ':
            insert_pos += 1
        if insert_pos >= len(result):
            raise ValueError("Cover text too short")
        zw = ZWSP if bit == '1' else ZWNJ
        result.insert(insert_pos+1, zw)
        insert_pos += 2
    return ''.join(result)

def extract_zw(text):
    bits = []
    for ch in text:
        if ch == ZWSP:
            bits.append('1')
        elif ch == ZWNJ:
            bits.append('0')
        if len(bits) % 8 == 0 and len(bits) > 0:
            byte = ''.join(bits[-8:])
            c = chr(int(byte, 2))
            if c == '\0':
                whole = ''.join(chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits)-8, 8))
                return whole
    return ''

# ---------------- Parity-based ----------------
def hide_parity_text(cover_text, message):
    message += "\0"
    bits = ''.join(format(ord(c), '08b') for c in message)
    result = ''
    bit_index = 0
    word_count = 0
    for ch in cover_text:
        result += ch
        if ch in ' \n' and bit_index < len(bits):
            word_count += 1
            parity = word_count % 2
            if parity != int(bits[bit_index]):
                result += ZWSP
            bit_index += 1
    if bit_index < len(bits):
        raise ValueError("Cover text too short")
    return result

def extract_parity_text(text):
    bits = ''
    word_count = 0
    i = 0
    while i < len(text):
        if text[i] in ' \n':
            word_count += 1
            parity = word_count % 2
            if i + 1 < len(text) and text[i+1] == ZWSP:
                parity = 1 - parity
                i += 1
            bits += str(parity)
            if len(bits) % 8 == 0:
                c = chr(int(bits[-8:], 2))
                if c == '\0':
                    return ''.join(chr(int(bits[j:j+8], 2)) for j in range(0, len(bits)-8, 8))
        i += 1
    return ''

# ---------------- Whitespace-based ----------------
def hide_whitespace(cover_text, message):
    message += "\0"
    bits = ''.join(format(ord(c), '08b') for c in message)
    lines = cover_text.splitlines(True)
    if len(bits) > len(lines):
        raise ValueError("Not enough lines in cover text")
    out = ''
    for i, line in enumerate(lines):
        if i < len(bits):
            out += line.rstrip('\n')
            out += ('\t' if bits[i] == '1' else ' ')
            out += '\n' if line.endswith('\n') else ''
        else:
            out += line
    return out

def extract_whitespace(text):
    lines = text.splitlines()
    bits = ''
    for line in lines:
        if line.endswith('\t'):
            bits += '1'
        elif line.endswith(' '):
            bits += '0'
        if len(bits) % 8 == 0 and len(bits) > 0:
            c = chr(int(bits[-8:], 2))
            if c == '\0':
                return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits)-8, 8))
    return ''
