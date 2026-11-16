"""Answer checks for Test 3 Quant (Q1, Q2M, Q2H): each entry recomputes the key from the problem's conditions."""
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import factorial, gcd, isqrt

from verify_quant import qc, pick


def _var(xs):
    m = F(sum(xs), len(xs))
    return sum((F(x) - m) ** 2 for x in xs) / len(xs)


def _ndiv(n):
    c, d = 0, 1
    while d * d <= n:
        if n % d == 0:
            c += 1 if d * d == n else 2
        d += 1
    return c


def _cents(x):  # nearest cent, halves up (x > 0)
    return F(int(x * 100 + F(1, 2)), 100)


def _frac(f):
    return [f.numerator, f.denominator]


def _nearest(options, value):
    return min(range(len(options)), key=lambda i: abs(options[i] - value))


# ---- Q1-03: P on a circle of radius 6 about Q with angle PQR obtuse; t > 1 gives u = cos < 0 via rational points
def _q1_03():
    cases = []
    for t in [F(k, 10) for k in range(11, 400)] + [1 + F(1, 10**4), F(10**4)]:
        u, v = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
        cases.append(((6 * u - 8) ** 2 + (6 * v) ** 2, 100))  # PR² vs 10²
    return qc(cases)


def _q1_04():
    best = max(a for a in range(-60, 13) for b in range(a, 13) for d in range(12, 80) if 50 - a - b - 12 - d >= d)
    return qc([(best, 7)])


EXAM = {"Ashford": (200, 76, 64), "Brookvale": (180, 80, 66), "Carrow": (300, 62, 59), "Denholm": (160, 75, 70)}
PASS = {k: F(n * p, 100) for k, (n, p, _) in EXAM.items()}
FAIL = {k: EXAM[k][0] - PASS[k] for k in EXAM}
TOTAL = {k: n * m for k, (n, _, m) in EXAM.items()}

MAT = {"Steel beams": (120, 450, 75), "Concrete": (800, 110, 60), "Timber": (250, 320, 80), "Bricks": (90, 600, 50)}
DELIV = {k: F(u * pct, 100) * p for k, (u, p, pct) in MAT.items()}
UNDELIV = {k: F(u * (100 - pct), 100) * p for k, (u, p, pct) in MAT.items()}


def _m07():
    P, Q = (F(24, 3), F(0)), (F(0), F(24, 4))
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    s = -(P[0] * dx + P[1] * dy) / (dx * dx + dy * dy)
    fx, fy = P[0] + s * dx, P[1] + s * dy
    d2 = fx * fx + fy * fy
    return [o * o for o in [F(4), F("4.8"), F(5), F(6), F(8)]].index(d2)


def _m08():
    k = next(k for k in [F(i, 4) for i in range(-400, 401)] if k != 3 and (2 * k + 6) / (k - 3) == 4)
    return (4 * k + 6) / (2 * k - 3)


def _m11():
    L = lambda x: min(6, x + 2) - max(0, x - 2)  # length of the favourable vertical chord; kinks at x = 2, 4
    area = sum(F(L(i) + L(i + 1), 2) for i in range(6))
    return _frac(area / 36)


def _h03():
    # sides a, b with a² + b² = 100; compare area² = a²b² with 50², over s = a² in (0, 100)
    return qc((s * (100 - s), 2500) for s in [F(i, 8) for i in range(1, 800)] + [F(1, 10**6), 100 - F(1, 10**6)])


def _h05():
    lists = [[50] * 6, [0, 0, 0, 100, 100, 100], [48, 49, 50, 50, 51, 52], [20, 30, 50, 50, 70, 80], [46, 46, 46, 54, 54, 54]]
    assert all(sum(L) == 300 for L in lists)
    return qc((_var(L + [46, 54]), _var(L)) for L in lists)


def _h06():
    r = F(11, 10)
    bal = lambda P: (10000 * r - P) * r - P  # linear in P
    P = bal(0) / (bal(0) - bal(1))
    return [F("5500"), F("5700"), F("5761.90"), F("6050"), F("6100")].index(_cents(P))


def _h07():
    B, C = (F(6), F(0)), (F(0), F(8))  # A at the origin
    cx, cy = C[0] - B[0], C[1] - B[1]
    s = ((0 - B[0]) * cx + (0 - B[1]) * cy) / (cx * cx + cy * cy)
    bd2 = s * s * (cx * cx + cy * cy)
    return [o * o for o in [F("3.6"), F(4), F("4.8"), F(5), F("6.4")]].index(bd2)


def _h12():
    best = max(e - a for a in range(1, 12) for b in range(a + 1, 12) for d in range(13, 60)
               for e in [50 - a - b - 12 - d] if e > d)
    return [17, 19, 20, 21, 22].index(best)


FX, FY = [40, 45, 50, 45, 55, 60], [30, 35, 40, 40, 50, 50]  # 2019..2024


def _h14():
    x, y, year = F(FX[-1]), F(FY[-1]), 2024
    while y <= x:
        year, x, y = year + 1, x + 3, y * F(11, 10)
    return year


def _median(xs):
    s = sorted(xs)
    return F(s[len(s) // 2 - 1] + s[len(s) // 2], 2)


CHECKS = {
    # ---------------- Q1
    "T3-Q1-01": lambda: qc((n % 12, 0) for n in range(1, 5001) if n * n % 72 == 0),
    "T3-Q1-02": lambda: qc((1 / x, x - 1) for x in [F(-i, 1000) for i in range(1, 1000)] + [F(-1, 10**6), F(-1) + F(1, 10**6)]),
    "T3-Q1-03": _q1_03,
    "T3-Q1-04": _q1_04,
    "T3-Q1-05": lambda: [F("24.32"), F("100"), F("275.68"), F("300"), F("324.32")].index(
        _cents(5000 * F(6, 100) * 3 - 5000 * (F(104, 100) ** 3 - 1))),
    "T3-Q1-06": lambda: sum(1 for c in combinations(range(1, 13), 8) if sum(q <= 5 for q in c) >= 4),
    "T3-Q1-07": lambda: pick([4, 6, 8, 9, 12, 18], lambda o: o in {_ndiv(6 * k) for k in range(1, 3000) if _ndiv(k) == 3}),
    "T3-Q1-08": lambda: [3, 4, 5, 6, 8].index(sum(1 for b in range(1, 2000) if isqrt(144 + b * b) ** 2 == 144 + b * b)),
    "T3-Q1-09": lambda: _frac(F(sum(1 for s in combinations(range(12), 4) if (0 in s) != (1 in s)), len(list(combinations(range(12), 4))))),
    "T3-Q1-10": lambda: [72, 73, 74, 75, 76].index(int(sum(PASS.values()) * 100 / sum(n for n, _, _ in EXAM.values()) + F(1, 2))),
    "T3-Q1-11": lambda: [F("59.5"), 60, F("60.5"), 61, F("61.5")].index(F(TOTAL["Ashford"] + TOTAL["Carrow"], EXAM["Ashford"][0] + EXAM["Carrow"][0])),
    "T3-Q1-12": lambda: pick([
        lambda: FAIL["Carrow"] > FAIL["Ashford"] + FAIL["Brookvale"] + FAIL["Denholm"],
        lambda: PASS["Brookvale"] > PASS["Denholm"],
        lambda: TOTAL["Denholm"] > TOTAL["Brookvale"],
        lambda: PASS["Ashford"] > PASS["Brookvale"]], lambda f: f()),
    # ---------------- Q2M
    "T3-Q2M-01": lambda: qc((a + b, 42) for a in range(1, 500) for b in range(1, 500) if gcd(a, b) == 6 and a * b // 6 == 72),
    "T3-Q2M-02": lambda: qc(((x - 2) * (x - 4), -1) for x in [2 + F(i, 1000) for i in range(0, 1001)] + [2 + F(1, 10**6), 3 - F(1, 10**6)]
                            if x * x - 5 * x + 6 < 0),
    "T3-Q2M-03": lambda: qc((F(4) * pi / F(1, 2), 25) for pi in (F(314159, 100000), F(314160, 100000))),
    "T3-Q2M-04": lambda: qc([(F(sum(1 for s in product((0, 1), repeat=6) if sum(s) == 3), 64),
                              F(sum(1 for s in product((0, 1), repeat=6) if sum(s) in (2, 4)), 64))]),
    "T3-Q2M-05": lambda: qc([(_var([4, 8, 12, 16]), _var([4, 8, 10, 12, 16]))]),
    "T3-Q2M-06": lambda: [6, 7, 8, 9, 10].index(4 + (1 - F(6 * 4, 60)) / F(9, 60)),
    "T3-Q2M-07": _m07,
    "T3-Q2M-08": _m08,
    "T3-Q2M-09": lambda: pick([-2, 0, 10, 26, 32, 50], lambda o: o in {sum(range(n, n + 4)) for n in range(-200, 200)}),
    "T3-Q2M-10": lambda: [F("73.2"), F("73.6"), F(74), F("74.4"), F(75)].index(F(25 * 72 + 5 * 8 - 10, 25)),
    "T3-Q2M-11": _m11,
    "T3-Q2M-12": lambda: [F("2.7"), F(3), F("3.6"), F("4.2"), F("4.5")].index(
        next(c for c in [F(i, 10) for i in range(0, 1000)] if (18 * F(25, 100) + c) / (18 + c) == F(40, 100))),
    "T3-Q2M-13": lambda: _nearest([20, 25, 30, 35, 40], DELIV["Timber"] * 100 / sum(DELIV.values())),
    "T3-Q2M-14": lambda: DELIV["Concrete"] + UNDELIV["Concrete"] * F(115, 100),
    "T3-Q2M-15": lambda: pick(["Steel beams", "Concrete", "Timber", "Bricks"], lambda m: UNDELIV[m] > 25000),
    # ---------------- Q2H
    "T3-Q2H-01": lambda: qc([(max(k for k in range(40) if factorial(20) % 12 ** k == 0), 9)]),
    "T3-Q2H-02": lambda: qc((x, 1) for x in [F(i, 7) for i in range(-700, 701)] + [1 - F(1, 10**6), F(10**6), F(-10**6), F(1)]
                            if abs(x - 3) > abs(x + 1)),
    "T3-Q2H-03": _h03,
    "T3-Q2H-04": lambda: qc([(sum(1 for n in range(1000, 10000) if all(a < b for a, b in zip(str(n), str(n)[1:]))),
                              sum(1 for n in range(1000, 10000) if all(a > b for a, b in zip(str(n), str(n)[1:]))))]),
    "T3-Q2H-05": _h05,
    "T3-Q2H-06": _h06,
    "T3-Q2H-07": _h07,
    "T3-Q2H-08": lambda: sum(1 for p in permutations(range(6)) if p.index(0) < p.index(1) and p[0] != 2),  # 0 Maths, 1 Physics, 2 Chemistry
    "T3-Q2H-09": lambda: pick([F(-3), F(0), F(2), F(5, 2), F(3), F(4)], lambda x: x != 2 and x / (x - 2) >= 3),
    "T3-Q2H-10": lambda: [28, 30, 32, 34, 40].index(sum(1 for n in range(1, 200) if (n % 6 == 0 or n % 15 == 0) and n % 10)),
    "T3-Q2H-11": lambda: _frac(2 * (F(1, 4) + F(1, 6) - F(1, 8)) + 1 * (F(1, 4) - F(1, 8))),
    "T3-Q2H-12": _h12,
    "T3-Q2H-13": lambda: _nearest([55, 57, 58, 60, 67], F(FX[-1] + FY[-1] - FX[0] - FY[0], FX[0] + FY[0]) * 100),
    "T3-Q2H-14": _h14,
    "T3-Q2H-15": lambda: pick([
        lambda: _median(FY) > 40,
        lambda: F(sum(FX), 6) > 48,
        lambda: F(FY[4] - FY[3], FY[3]) > F(FX[4] - FX[3], FX[3]),
        lambda: all(FY[i] < FY[i - 1] for i in range(1, 6) if FX[i] < FX[i - 1])], lambda f: f()),
}
