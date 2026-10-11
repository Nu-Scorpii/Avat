"""Percentage strength moves legal numeric faces toward their best/worst value."""

from .dice import values_of


def luck_result(plan, natural, mode, percent):
    if not plan.numeric:
        return natural
    values = []
    for (sign, die), value in zip(plan.dice, values_of(natural)):
        up = (mode == 'good') == (sign > 0)
        low, high = (1, die.sides) if die.sides is not None else (min(die.faces), max(die.faces))
        extreme = high if up else low
        # Integer arithmetic avoids rounding errors on large or negative dice.
        scaled = value * 100 + (extreme - value) * percent
        if die.sides is not None:
            move = (abs(extreme - value) * percent + 50) // 100
            adjusted = value + move if up else value - move
        else:
            adjusted = min(set(die.faces), key=lambda face: (abs(face * 100 - scaled), -face if up else face))
        values.append(adjusted)
    return plan.result(values)
