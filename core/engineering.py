def ohms_law(voltage=None, current=None, resistance=None):
    try:
        if voltage is None:
            voltage = current * resistance
            return f"Voltage is {voltage} V"

        if current is None:
            current = voltage / resistance
            return f"Current is {current} A"

        if resistance is None:
            resistance = voltage / current
            return f"Resistance is {resistance} ohm"

        return "Please provide only two values."

    except ZeroDivisionError:
        return "Calculation error: division by zero."


def electrical_power(voltage, current):
    power = voltage * current
    return f"Electrical power is {power} W"


def frequency_from_period(period):
    try:
        frequency = 1 / period
        return f"Frequency is {frequency} Hz"
    except ZeroDivisionError:
        return "Period cannot be zero."


def series_resistance(values):
    result = sum(values)
    return f"Total series resistance is {result} ohm"


def parallel_resistance(values):
    try:
        reciprocal_sum = sum(1 / value for value in values)

        if reciprocal_sum == 0:
            return "Invalid resistance values."

        result = 1 / reciprocal_sum
        return f"Total parallel resistance is {round(result, 4)} ohm"

    except ZeroDivisionError:
        return "Resistance cannot be zero."