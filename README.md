# Advanced Steganography GUI

A modular **Advanced Steganography Tool** with a modern GUI that supports **hiding and extracting secret messages** from multiple media types including **Images, Audio, Text, and Video** using different steganographic techniques.

Built with **Python** and **CustomTkinter**, and designed with a clean, organized architecture where each category is implemented in a separate module.

---

## 🚀 Features

### 🔹 Supported Categories & Methods

#### 🖼 Image

* LSB
* Parity
* Bit Plane

#### 🔊 Audio

* LSB
* Parity
* Phase Coding
* Echo Hiding

#### 📝 Text

* Zero Width Characters
* Parity
* Whitespace Encoding

#### 🎬 Video

* DeEgger Method (Hide / Extract)

---

## 🧩 Project Structure

```
stego_app/
│
├── steganograpy_app.py             # Main GUI application
├── categories
├───── image_stego.py       # Image steganography methods
├───── audio_stego.py       # Audio steganography methods
├───── text_stego.py        # Text steganography methods
├───── video_stego.py       # Video steganography methods
└── README.md
```

Each category is **fully separated** into its own file for better readability, maintenance, and scalability.

---

## 🖥 GUI Overview

* Modern dark-themed interface (CustomTkinter)
* Category & Method selection
* Dynamic input handling
* Supports both **Hide** and **Extract**
* Extracted messages are displayed directly to the user

---

## 🛠 Requirements

* Python 3.9+
* Required libraries:

  ```bash
  pip install customtkinter pillow numpy opencv-python
  ```

*(Additional libraries may be required depending on audio/video methods used)*

---

## ▶️ How to Run

```bash
python steganograpy_app.py
```

---

## 📌 Notes

* Extraction functions **return the extracted message**, which is displayed in the GUI.
* Errors and invalid inputs are handled gracefully.
* The project is structured for easy extension (adding new methods or categories).

---

## 🧠 Educational Purpose

This project is intended for:

* Learning steganography concepts
* Academic projects
* CTFs & security research
* Demonstrating modular GUI-based Python applications

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**.
Do not use it for illegal or unethical activities.

---

⭐ If you like this project, consider giving it a star on GitHub!
