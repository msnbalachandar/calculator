import ast
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

Window.clearcolor = (0.08, 0.08, 0.1, 1)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(expr):
    """Evaluate a basic arithmetic expression without using eval()."""

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = walk(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        raise ValueError("Invalid expression")

    return walk(ast.parse(expr, mode="eval"))


class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        self.expression = ""

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.display = Label(
            text="0",
            font_size="48sp",
            halign="right",
            valign="bottom",
            size_hint=(1, 0.28),
        )
        self.display.bind(size=lambda w, s: setattr(w, "text_size", s))
        root.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=8, size_hint=(1, 0.72))
        buttons = [
            "C", "<", "%", "/",
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "0", ".", "=", "",
        ]
        labels = {"/": "÷", "*": "×", "-": "−", "<": "⌫"}

        for key in buttons:
            if key == "":
                grid.add_widget(Label())
                continue
            is_op = key in "/*-+="
            btn = Button(
                text=labels.get(key, key),
                font_size="28sp",
                background_normal="",
                background_color=(0.95, 0.55, 0.1, 1) if is_op
                else (0.25, 0.25, 0.3, 1) if key in "C<%"
                else (0.17, 0.17, 0.2, 1),
            )
            btn.bind(on_press=lambda inst, k=key: self.on_key(k))
            grid.add_widget(btn)

        root.add_widget(grid)
        return root

    def on_key(self, key):
        if key == "C":
            self.expression = ""
        elif key == "<":
            self.expression = self.expression[:-1]
        elif key == "=":
            self.calculate()
            return
        else:
            self.expression += key
        self.display.text = self.pretty(self.expression) or "0"

    def calculate(self):
        if not self.expression:
            return
        try:
            result = safe_eval(self.expression.replace("%", "/100"))
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 10)
            self.expression = str(result)
            self.display.text = self.expression
        except ZeroDivisionError:
            self.expression = ""
            self.display.text = "Cannot divide by 0"
        except Exception:
            self.expression = ""
            self.display.text = "Error"

    @staticmethod
    def pretty(text):
        return text.replace("/", "÷").replace("*", "×").replace("-", "−")


if __name__ == "__main__":
    CalculatorApp().run()
