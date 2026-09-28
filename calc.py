import ast
import operator
import tkinter as tk

# ---------- Safe expression evaluator ----------
OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Invalid expression")


def calculate(expr):
    return _eval(ast.parse(expr, mode="eval"))


def fmt(value):
    """Turn a number into a clean string (no trailing .0, no float noise)."""
    if isinstance(value, float):
        value = round(value, 10)
        if value == int(value):
            value = int(value)
    return str(value)


# ---------- Theme (matches the reference image) ----------
BG, DOT = "#e3f5fb", "#c4e6f3"
BODY, BODY_SHADOW = "#ff8fb8", "#c85b88"
OUTLINE = "#4d2a36"
DISPLAY_BG = "#e9fbff"
FACE, FACE_HOVER, FACE_SHADOW = "#cdeeff", "#e4f7ff", "#2f5a75"
TEXT = "#5a2a1f"
FONT = "Helvetica"

W, H = 300, 490
OFF = 4  # depth of the 3D button shadow


def rrect(cv, x1, y1, x2, y2, r, **kw):
    """Draw a rounded rectangle on a canvas."""
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


class Key:
    """A chunky 3D button that sinks when pressed."""

    def __init__(self, cv, x, y, w, h, label, command):
        self.cv, self.command, self.down = cv, command, False
        self.shadow = rrect(cv, x + OFF, y + OFF, x + w + OFF, y + h + OFF, 10,
                            fill=FACE_SHADOW, outline=OUTLINE, width=2)
        self.face = rrect(cv, x, y, x + w, y + h, 10,
                          fill=FACE, outline=OUTLINE, width=2)
        self.text = cv.create_text(x + w / 2, y + h / 2, text=label,
                                   font=(FONT, 17, "bold"), fill=TEXT)
        for item in (self.face, self.text):
            cv.tag_bind(item, "<ButtonPress-1>", self.on_press)
            cv.tag_bind(item, "<ButtonRelease-1>", self.on_release)
            cv.tag_bind(item, "<Enter>", self.on_enter)
            cv.tag_bind(item, "<Leave>", self.on_leave)

    def _move(self, d):
        self.cv.move(self.face, d, d)
        self.cv.move(self.text, d, d)

    def on_enter(self, _):
        self.cv.config(cursor="hand2")
        self.cv.itemconfig(self.face, fill=FACE_HOVER)

    def on_leave(self, _):
        self.cv.config(cursor="")
        self.cv.itemconfig(self.face, fill=FACE)
        if self.down:
            self._move(-OFF)
            self.down = False

    def on_press(self, _):
        if not self.down:
            self._move(OFF)
            self.down = True

    def on_release(self, _):
        if self.down:
            self._move(-OFF)
            self.down = False
            self.command()


class Calculator:
    LAYOUT = [
        ["C", "+/-", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "+"],
        ["⌫", "0", ".", "="],
    ]

    def __init__(self, root):
        self.root = root
        root.title("Calculator")
        root.resizable(False, False)
        self.expr, self.just_evaluated = "", False

        cv = self.cv = tk.Canvas(root, width=W, height=H, bg=BG,
                                 highlightthickness=0)
        cv.pack()

        # Dotted background
        for x in range(3, W, 8):
            for y in range(3, H, 8):
                cv.create_rectangle(x, y, x + 2, y + 2, fill=DOT, outline="")

        # Pink calculator body
        rrect(cv, 24, 20, W - 14, H - 14, 16, fill=BODY_SHADOW, outline=OUTLINE, width=3)
        rrect(cv, 18, 14, W - 20, H - 20, 16, fill=BODY, outline=OUTLINE, width=3)

        # Display
        rrect(cv, 34, 30, W - 36, 116, 10, fill=DISPLAY_BG, outline=OUTLINE, width=3)
        self.history = cv.create_text(W - 46, 52, text="", anchor="e",
                                      font=(FONT, 11, "bold"), fill="#8a6a70")
        self.result = cv.create_text(W - 46, 88, text="0", anchor="e",
                                     font=(FONT, 30, "bold"), fill=TEXT)

        # Keys
        bw, bh, gx, gy = 51, 56, 8, 12
        x0, y0 = 34, 134
        for r, row in enumerate(self.LAYOUT):
            for c, label in enumerate(row):
                Key(cv, x0 + c * (bw + gx), y0 + r * (bh + gy), bw, bh, label,
                    lambda t=label: self.press(t))

        # Keyboard support
        root.bind("<Key>", self.on_key)
        root.bind("<Return>", lambda e: self.press("="))
        root.bind("<BackSpace>", lambda e: self.press("⌫"))
        root.bind("<Escape>", lambda e: self.press("C"))

    # ---------- Display ----------
    @staticmethod
    def pretty(s):
        return s.replace("*", "×").replace("/", "÷").replace("-", "−")

    def refresh(self):
        shown = self.pretty(self.expr) or "0"
        size = 30 if len(shown) <= 9 else 22 if len(shown) <= 13 else 15
        self.cv.itemconfig(self.result, text=shown, font=(FONT, size, "bold"))

    # ---------- Logic ----------
    def current_number(self):
        i = len(self.expr)
        while i > 0 and (self.expr[i - 1].isdigit() or self.expr[i - 1] == "."):
            i -= 1
        return self.expr[i:]

    def press(self, t):
        ops = {"÷": "/", "×": "*", "+": "+", "−": "-"}
        if t == "C":
            self.expr, self.just_evaluated = "", False
            self.cv.itemconfig(self.history, text="")
        elif t == "⌫":
            self.expr = self.expr[:-1]
            self.just_evaluated = False
        elif t == "+/-":
            self.toggle_sign()
        elif t == "%":
            self.percent()
        elif t == "=":
            self.evaluate()
            return
        elif t in ops:
            self.just_evaluated = False
            if self.expr and self.expr[-1] in "+-*/":
                self.expr = self.expr[:-1]  # replace previous operator
            if self.expr or t == "−":
                self.expr += ops[t]
        else:  # digit or dot
            if self.just_evaluated:
                self.expr, self.just_evaluated = "", False
            if t == "." and "." in self.current_number():
                return
            self.expr += t
        self.refresh()

    def toggle_sign(self):
        num = self.current_number()
        if not num:
            return
        start = len(self.expr) - len(num)
        if start > 0 and self.expr[start - 1] == "-" and (
                start == 1 or self.expr[start - 2] in "+-*/"):
            self.expr = self.expr[:start - 1] + num
        else:
            self.expr = self.expr[:start] + "-" + num

    def percent(self):
        num = self.current_number()
        if num and num != ".":
            start = len(self.expr) - len(num)
            self.expr = self.expr[:start] + fmt(float(num) / 100)

    def evaluate(self):
        if not self.expr:
            return
        try:
            value = calculate(self.expr)
            self.cv.itemconfig(self.history, text=self.pretty(self.expr))
            self.expr = fmt(value)
            self.just_evaluated = True
            self.refresh()
        except ZeroDivisionError:
            self.show_error("Can't ÷ by 0")
        except Exception:
            self.show_error("Error")

    def show_error(self, msg):
        self.expr, self.just_evaluated = "", False
        self.cv.itemconfig(self.result, text=msg, font=(FONT, 18, "bold"))

    def on_key(self, e):
        if e.char and e.char in "0123456789.+%":
            self.press(e.char)
        elif e.char == "-":
            self.press("−")
        elif e.char == "*":
            self.press("×")
        elif e.char == "/":
            self.press("÷")


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()