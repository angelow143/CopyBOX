# CopyBox - Always On Top Search Bar

A lightweight Python application that provides a search bar that always stays on top of other windows, perfect for quick text copying and emoji input.

## Features

- **Always on Top**: The window stays above all other applications including Chrome, VS Code, etc.
- **Search Bar**: Clean, modern interface with placeholder text
- **Pushpin Icon**: Visual indicator with a grey pushpin emoji
- **Clear Button**: Grey 'X' button to clear the search text
- **Copy Button**: Green copy button that copies text to clipboard
- **Draggable**: Click and drag the window to reposition it anywhere on screen
- **Visual Feedback**: Button changes to 'copied!' with blue color when text is copied

## Installation

1. Make sure you have Python installed (3.6 or higher)
2. Install the required dependency:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. The CopyBox window will appear and stay on top of all other windows

3. **Features**:
   - Type or paste text in the search bar
   - Click the 'X' button to clear the text
   - Click the green 'copy' button to copy text to clipboard
   - Click and drag anywhere on the window to move it
   - The window will always remain on top of other applications

## Requirements

- Python 3.6+
- tkinter (usually comes with Python)
- pyperclip

## File Structure

```
CopyBOX/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How it Works

- The application uses tkinter's `-topmost` attribute to keep the window always on top
- `overrideredirect(True)` removes window decorations for a cleaner look
- The window is draggable by clicking and dragging anywhere on the interface
- pyperclip handles clipboard operations for the copy functionality




git add .
git commit -m "add mouse"
git push origin main
