"""Answer checks for Test 2 Quant (Q1, Q2M, Q2H): each computes the key from the problem's conditions."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations, product
import random

from verify_quant import qc, pick

# fine grid of exact values used by several qc searches
GRID = sorted({F(i, 8) for i in range(-800, 801)} | {F(1, 1000), F(-1, 1000), F(10**6), F(-10**6)})


def _nearest(options, value):
    return min(range(len(options)), key=lambda i: abs(options[i] - value))


def _q1_08():
    # 7 integers a<=b<=c<=12<=e<=f<=g (median 12), sum 70, 14 the only mode; maximise a (a >= 0 suffices)
    best = None
    for a in range(0, 13):
        for b in range(a, 13):
            for c in range(b, 13):
                rem = 70 - 12 - a - b - c
                for e in range(12, rem + 1):
                    for f in range(e, rem + 1):
                        g = rem - e - f
                        if g < f:
                            break
                        cnt = Counter([a, b, c, 12, e, f, g])
                        top = max(cnt.values())
                        if cnt[14] == top and list(cnt.values()).count(top) == 1:
                            best = a if best is None else max(best, a)
    return [2, 3, 4, 5, 6].index(best)


# hardware shop table: (price Jan-Mar, units Jan-Mar, price Apr-Jun, units Apr-Jun)
SHOP = {"Paint": (12, 250, 15, 220), "Brush": (4, 600, 4, 540), "Drill": (80, 45, 72, 60),
        "Ladder": (50, 30, 55, 36), "Screws": (6, 400, 5, 520)}


def _q1_10():
    name = max(SHOP, key=lambda k: F(SHOP[k][3], SHOP[k][1]))
    p1, u1, p2, u2 = SHOP[name]
    return _nearest([8, 10, 15, 18, 20], (F(p2 * u2, p1 * u1) - 1) * 100)


def _q1_11():
    rev = sum(p2 * u2 for _, _, p2, u2 in SHOP.values())
    units = sum(u2 for _, _, _, u2 in SHOP.values())
    return _nearest([F("10.44"), F("14.36"), F("24.40"), F("30.20"), F("36.00")], F(rev, units))


def _q1_12():
    names = ["Paint", "Brush", "Drill", "Ladder", "Screws"]
    return pick(names, lambda k: F(SHOP[k][2] * SHOP[k][3], SHOP[k][0] * SHOP[k][1]) > F(SHOP[k][3], SHOP[k][1]))


BUS = {"Adult": (480, 432), "Student": (160, 200), "Child": (120, 138), "Senior": (200, 226), "Disability pass": (40, 40)}


def _q2m_14():
    adult, student = F(432), F(200)
    ratio, step = F(432, 480), 200 - 160
    year = 2024
    while student <= adult:
        year += 1
        adult *= ratio
        student += step
    return year


def _q2m_15():
    t23 = sum(a for a, _ in BUS.values())
    t24 = sum(b for _, b in BUS.values())
    return pick(list(BUS), lambda k: F(BUS[k][1], t24) > F(BUS[k][0], t23))


def _var(xs):
    m = F(sum(xs), len(xs))
    return sum((x - m) ** 2 for x in xs) / len(xs)


def _q2h_04():
    rng = random.Random(7)
    cases = []
    for _ in range(200):
        rest = [F(rng.randint(-50, 50), rng.choice([1, 2, 3])) for _ in range(18)]
        if len(set(rest)) == 1:
            continue
        m = F(sum(rest), 18)
        full = rest + [m, m]
        cases.append((_var(full), _var(rest)))  # same order as the standard deviations
    cases.append((_var([0] * 9 + [10] * 9 + [5, 5]), _var([0] * 9 + [10] * 9)))
    return qc(cases)


def _q2h_06():
    g = lambda x: abs(x - 3) - abs(x + 1)
    xs = [F(i, 8) for i in range(-400, 401)]
    return [5, 6, 7, 8, 9].index(sum(1 for k in range(-10, 11) if sum(1 for x in xs if g(x) == k) == 1))


NORTH = [25, 30, 35, 45, 55, 60]
SOUTH = [40, 35, 45, 50, 60, 70]

CHECKS = {
    # ---------------- Q1
    "T2-Q1-01": lambda: qc([(next(n for n in range(1, 10**4) if n * n % 72 == 0), 12)]),
    "T2-Q1-02": lambda: qc((((10 + d) / 2) * ((10 - d) / 2), 21)
                           for d in [4 + F(1, 1000), F(41, 10)] + [F(i, 4) for i in range(17, 400)] + [F(10**6)]),
    "T2-Q1-03": lambda: (lambda area: (20 ** 2 - 4 * area > 0) and qc([(area, F(175, 2))]))(F(20 ** 2 - 15 ** 2, 2)),
    "T2-Q1-04": lambda: (lambda pairs: qc([(F(sum(1 for p in pairs if p[0][0] == p[1][0]), len(pairs)),
                                            F(sum(1 for p in pairs if p[0][0] != p[1][0]), len(pairs)))]))(
        list(combinations([("r", i) for i in range(5)] + [("b", i) for i in range(3)], 2))),
    "T2-Q1-05": lambda: [150, 180, 216, 240, 270].index(
        next(c for c in range(1, 2000) if F(c) * F(160, 100) * F(75, 100) - c == 36)),
    # 60t + 90(t - 1/2) = 330, distance from P = 60t
    "T2-Q1-06": lambda: next(60 * t for t in [F(i, 60) for i in range(30, 6 * 60)] if 60 * t + 90 * (t - F(1, 2)) == 330),
    "T2-Q1-07": lambda: pick([2, 4, 9, 11, 16, 18], lambda v: v in {n * n % 21 for n in range(3, 5000, 7)}),
    "T2-Q1-08": _q1_08,
    "T2-Q1-09": lambda: (lambda hits: [hits, 60])(sum(1 for n in range(1, 61) if (n % 4 == 0) != (n % 6 == 0))),
    "T2-Q1-10": _q1_10,
    "T2-Q1-11": _q1_11,
    "T2-Q1-12": _q1_12,
    # ---------------- Q2M
    "T2-Q2M-01": lambda: (lambda mx, my: qc([(mx * mx + my * my, F(14, 10) ** 2)]))(F(-3 + 5, 2), F(4 - 2, 2)),
    "T2-Q2M-02": lambda: qc(((x * x + 1) / x, 2) for x in [F(1, 1000), F(999, 1000)] + [F(i, 100) for i in range(1, 100)]),
    "T2-Q2M-03": lambda: (lambda xs: qc([(_var([-2 * x + 30 for x in xs]), 4 * _var(xs))]))([3, 5, 7, 9, 11]),
    "T2-Q2M-04": lambda: qc([(sum(1 for d in range(1, 37) if 36 % d == 0), sum(1 for d in range(1, 41) if 40 % d == 0))]),
    "T2-Q2M-05": lambda: qc((a * (12 - 2 * a) / 3, 6) for a in [F(1, 1000), F(5999, 1000), F(3)] + [F(i, 20) for i in range(1, 120)]),
    "T2-Q2M-06": lambda: [F(-1), F(-1, 2), F(1, 2), F(1), F(2)].index(
        next(t for t in [F(i, 20) for i in range(-400, 401)] if t * t - 4 * t == (t + 3) ** 2 - 4 * (t + 3))),
    "T2-Q2M-07": lambda: [30, F(75, 2), 45, 50, 60].index(
        next(x for x in [F(i, 2) for i in range(0, 601)] if (300 - x) * F(1, 5) + x == F(30, 100) * 300)),
    "T2-Q2M-08": lambda: (lambda left: F(24) / left)(F(36, 32) - F(12, 24)),
    "T2-Q2M-09": lambda: pick([15, 24, 29, 30, 31], lambda v: 0 < F(v) / 5 < 6),  # area = 10 * h / 2, obtuse -> 0 < h < 6
    "T2-Q2M-10": lambda: [120, 240, 360, 480, 600].index(
        sum(1 for p in permutations(range(6)) if abs(p.index(0) - p.index(1)) != 1)),
    "T2-Q2M-11": lambda: (lambda picks: [sum(1 for s in picks if sum(1 for c in s if c < 3) == 1), len(picks)])(
        list(combinations(range(10), 3))),
    "T2-Q2M-12": lambda: [22, 24, 27, 30, 33].index(sum(1 for n in range(1, 200) if n % 6 == 0 and n % 9)),
    "T2-Q2M-13": lambda: _nearest([4, 8, 12, 14, 16], (F(sum(b for k, (a, b) in BUS.items() if k != "Adult"),
                                                       sum(a for k, (a, b) in BUS.items() if k != "Adult")) - 1) * 100),
    "T2-Q2M-14": _q2m_14,
    "T2-Q2M-15": _q2m_15,
    # ---------------- Q2H
    "T2-Q2H-01": lambda: qc([(sum(1 for x in range(1, 200) for y in range(1, 200) if x * x - y * y == 45), 3)]),
    "T2-Q2H-02": lambda: qc((a * a, a * b) for a in GRID for b in [F(i, 4) for i in range(-40, 41) if i] + [F(1, 1000), F(-1, 1000)]
                            if a and a / b > 1),
    "T2-Q2H-03": lambda: qc((4 - pi, pi - 2) for pi in [F(314159, 100000), F(31416, 10000)]),  # radius 1
    "T2-Q2H-04": _q2h_04,
    "T2-Q2H-05": lambda: (lambda codes: qc([(sum(1 for c in codes if len(set(c)) < 4), sum(1 for c in codes if len(set(c)) == 4))]))(
        list(product(range(10), repeat=4))),
    "T2-Q2H-06": _q2h_06,
    "T2-Q2H-07": lambda: [120, 130, 140, 150, 160].index(next(m for m in range(0, 301) if F(m, 60) / 6 + F(5, 9) == 1)),
    "T2-Q2H-08": lambda: sum(1 for x in range(0, 9) for y in range(0, 7) if 6 * x + 8 * y <= 48),
    "T2-Q2H-09": lambda: pick([3, 5, 6, 8, 9, 12], lambda v: v in {
        sum(1 for d in range(1, 4 * n + 1) if 4 * n % d == 0)
        for n in range(1, 2000) if sum(1 for d in range(1, n + 1) if n % d == 0) == 3}),
    "T2-Q2H-10": lambda: [33, 35, 36, 37, 38].index(max(
        e - a for a in range(1, 10) for b in range(a + 1, 10) for d in range(11, 60)
        for e in [60 - a - b - 10 - d] if e > d)),
    "T2-Q2H-11": lambda: (lambda all_: [sum(1 for s in all_ if len(set(s)) == 3), len(all_)])(list(product(range(3), repeat=5))),
    # options 7, 8, 9, √85, 11 compared by their squares
    "T2-Q2H-12": lambda: [49, 64, 81, 85, 121].index(next(h * h for h in range(1, 20) if 6 * 6 + 6 * 6 + h * h == 11 * 11)),
    "T2-Q2H-13": lambda: [1, 2, 3, 4, 5].index(sum(1 for n, s in zip(NORTH, SOUTH) if F(n, n + s) > F(45, 100))),
    "T2-Q2H-14": lambda: 7 * F(sum(SOUTH), 6) - sum(NORTH),
    "T2-Q2H-15": lambda: pick(range(1, 6), lambda i: F(NORTH[i], NORTH[i - 1]) > F(SOUTH[i], SOUTH[i - 1])),
}
