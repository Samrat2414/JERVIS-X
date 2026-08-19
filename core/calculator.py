import math
import re


def calculate(expression):
    try:
        expression = expression.lower().strip()

        # Percentage
        match = re.fullmatch(r"(\d+(?:\.\d+)?)%\s+of\s+(\d+(?:\.\d+)?)", expression)
        if match:
            percent = float(match.group(1))
            number = float(match.group(2))
            result = (percent / 100) * number
            return f"The answer is {result}"

        # Power
        match = re.fullmatch(
            r"(\d+(?:\.\d+)?)\s+power\s+(\d+(?:\.\d+)?)",
            expression
        )
        if match:
            base = float(match.group(1))
            exponent = float(match.group(2))
            result = base ** exponent
            return f"The answer is {result}"

        # Trigonometry in degrees
        match = re.fullmatch(
            r"(sin|cos|tan)\s+(-?\d+(?:\.\d+)?)",
            expression
        )
        if match:
            function = match.group(1)
            angle = float(match.group(2))
            radians = math.radians(angle)

            if function == "sin":
                result = math.sin(radians)
            elif function == "cos":
                result = math.cos(radians)
            else:
                result = math.tan(radians)

            return f"The answer is {round(result, 6)}"

        # log10
        match = re.fullmatch(r"log10\s+(\d+(?:\.\d+)?)", expression)
        if match:
            number = float(match.group(1))

            if number <= 0:
                return "Logarithm requires a positive number."

            return f"The answer is {math.log10(number)}"

        # Normal scientific calculator
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