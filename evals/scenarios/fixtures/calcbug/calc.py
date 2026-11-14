def average(xs):
    return sum(xs) / len(xs)


def percent(part, whole):
    return part / whole * 100


def clamp(x, lo, hi):
    return max(lo, min(hi, x))
