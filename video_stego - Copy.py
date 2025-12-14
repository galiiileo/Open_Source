# video_stego.py
import os
from pathlib import Path


DEEGGER_LNK_PATH = r"C:\Program Files (x86)\ZASI\DeEgger Embedder\DeEgger Embedder.exe"

def create_message_file(message, output_dir="Output", output_name="embedded_message.txt"):
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, output_name)
    with open(out, "w", encoding="utf-8") as f:
        f.write(message)
    return out

def open_deegger(lnk_path=DEEGGER_LNK_PATH):
    """Try to open DeEgger (windows .lnk). Returns True if started or raises."""
    if os.path.exists(lnk_path):
        try:
            os.startfile(lnk_path)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to open DeEgger: {e}")
    else:
        raise FileNotFoundError("DeEgger shortcut not found at configured path.")

def hide_video_deegger(video_path, message, lnk_path=DEEGGER_LNK_PATH):
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video path not found")
    msg_file = create_message_file(message)
    # Open DeEgger for user to manually embed (DeEgger requires GUI usage)
    open_deegger(lnk_path)
    # Return instructions & msg_file path so GUI can show them
    info = {
        "host": video_path,
        "embed": msg_file,
        "note": "DeEgger opened. Select Host = host path, Embed = embed path then run Embed."
    }
    return info

def extract_video_deegger(extracted_txt_path):
    if not os.path.exists(extracted_txt_path):
        raise FileNotFoundError("Extracted .txt not found")
    with open(extracted_txt_path, "r", encoding="utf-8") as f:
        return f.read()
