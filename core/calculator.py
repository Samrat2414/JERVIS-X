import math


def calculate(expression):
    try:
        allowed_names = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "pi": math.pi,
            "e": math.e,
        }

        result = eval(
            expression,
            {"__builtins__": {}},
            allowed_names
        )

        return f"The answer is {result}"

    except Exception:
        return "Sorry, I could not calculate that."