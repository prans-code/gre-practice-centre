"""Computed answer checks for the shared easy Quant section (Q2E)."""
from fractions import Fraction as F
from itertools import permutations
from verify_quant import qc, pick

# e-sports-shop table: month -> (footballs sold, price per football, pairs of trainers sold, price per pair)
SHOP = {"January": (40, 15, 20, 60), "February": (60, 15, 25, 60), "March": (50, 18, 30, 45), "April": (70, 16, 24, 55)}
GRID = [F(i, 8) for i in range(-800, 801)] + [F(1, 1000), F(-1, 1000), F(10**6), F(-10**6)]


def _both_red():
    bag = ["r"] * 4 + ["b"] * 5 + ["g"] * 3
    pairs = list(permutations(range(len(bag)), 2))
    return F(sum(1 for i, j in pairs if bag[i] == bag[j] == "r"), len(pairs))


def _left_fraction():
    left = 1 - F(1, 4)
    left -= left * F(1, 3)
    return [left.numerator, left.denominator]


CHECKS = {
    "E-Q-01": lambda: qc([(F(80) * F(125, 100) * F(75, 100), F(80))]),
    "E-Q-02": lambda: qc((y, 4) for y in GRID if y * y == 4 * y),
    "E-Q-03": lambda: qc((s, 3) for s in [F(i, 100) for i in range(1, 2001)] + [F(3) + F(1, 10**6)] if 8 - 5 < s < 8 + 5),
    "E-Q-04": lambda: qc([((600 // 50) * (400 // 50), 96)] if 600 % 50 == 0 and 400 % 50 == 0 else []),
    "E-Q-05": lambda: qc((p * q, 25) for p in range(1, 10) for q in range(1, 10) if p + q == 10 and p != q),
    "E-Q-06": lambda: [F(92, 10), F(96, 10), F(10), F(104, 10), F(12)].index(F(48) / (F(24, 12) + F(24, 8))),
    "E-Q-07": lambda: [50, 55, 60, 65, 70].index(next(a for a in range(151) if 4 * (150 - a) + 7 * a == 795)),
    "E-Q-08": lambda: (18 + 2) * (12 + 2) - 18 * 12,
    "E-Q-09": lambda: pick([3, 4, 6, 8, 9, 12], lambda t: 36 % t == 0 and 3 < 36 // t < 12),
    "E-Q-10": lambda: [F(1, 11), F(1, 9), F(4, 33), F(1, 6), F(1, 3)].index(_both_red()),
    "E-Q-11": _left_fraction,
    "E-Q-12": lambda: [F(125, 100), F(15, 10), F(175, 100), F(2), F(225, 100)].index((F(36, 2) ** 2) / (F(24, 2) ** 2)),
    "E-Q-13": lambda: (lambda pct: min(range(5), key=lambda i: abs([36, 47, 57, 64, 75][i] - pct)))(
        100 * F(sum(SHOP["April"][0::2]) - sum(SHOP["January"][0::2]), sum(SHOP["January"][0::2]))),
    "E-Q-14": lambda: (lambda f, pf, t, pt: F(f * pf + t * pt, f + t))(*SHOP["January"]),
    "E-Q-15": lambda: pick(list(SHOP), lambda m: SHOP[m][2] * SHOP[m][3] > F(3, 2) * SHOP[m][0] * SHOP[m][1]),
}
