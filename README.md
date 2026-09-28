**Calcify** is a colourful desktop calculator built with Python and `tkinter`. 

## Features

- Display with a small history line (previous expression) and a large result
- Supports `+`, `−`, `×`, `÷`, `%`, `+/-`, decimals, backspace and clear
- Keyboard support
- Safe evaluation: expressions are parsed with Python's `ast` module, not `eval()`
- Friendly error message when dividing by zero
- No external libraries needed

## Requirements

- Python 3.8 or newer
- `tkinter` (included with Python on Windows and macOS)


## Controls

| Action | Mouse | Keyboard |
|---|---|---|
| Digits and decimal point | Click `0-9` and `.` | `0-9` and `.` |
| Add, subtract, multiply, divide | `+`, `−`, `×`, `÷` | `+`, `-`, `*`, `/` |
| Calculate | `=` | `Enter` |
| Delete last character | `⌫` | `Backspace` |
| Clear everything | `C` | `Esc` |
| Percentage (50 becomes 0.5) | `%` | `%` |
| Change sign | `+/-` | (mouse only) |

## Example

Typing `18 × 3 + 8` and pressing `=` shows `62`, with `18 × 3 + 8` in the history line above it.

## Customising

All colours and sizes are constants near the top of `calcify.py` (`BODY`, `FACE`, `FACE_SHADOW`, `TEXT`, `W`, `H`, and so on). Change them to give the calculator a new look.

## Notes

- This app opens a desktop window, so it will not work in Google Colab or other browser-only notebooks.
- Calculations use floating-point numbers, and results are rounded to 10 decimal places to avoid noise like `0.30000000000000004`.

