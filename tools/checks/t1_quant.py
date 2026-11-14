"""Answer checks for Test 1 Quant: T1-Q1, T1-Q2M, T1-Q2H. Each computes the key from the question's conditions."""
from fractions import Fraction as F
from functools import reduce
from itertools import combinations, product
from math import comb, gcd, isqrt, lcm, sqrt
from statistics import median

from verify_quant import pick, qc

GRID = [F(i, 100) for i in range(-500, 501)] + [F(-10**6), F(-1, 10**6), F(1, 10**6), F(10**6)]
POS = [F(i, 8) for i in range(1, 200)] + [F(1, 10**6), F(10**6)]


def ndiv(n):
    count, p = 1, 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        count *= e + 1
        p += 1
    return count * (2 if n > 1 else 1)


# t1-factory-output: produced, rejected (thousands), employees
FACT = {"Aldgate": (240, F(72, 10), 160), "Brindle": (180, F(72, 10), 100),
        "Carrow": (300, F(6), 250), "Dunmore": (120, F(6), 60)}
# t1-league-season: won, drawn, lost, goals scored, goals conceded
LEAGUE = {"Harriers": (12, 2, 6, 41, 25), "Kestrels": (11, 7, 2, 33, 15), "Ospreys": (10, 5, 5, 36, 28),
          "Falcons": (8, 6, 6, 27, 26), "Merlins": (6, 5, 9, 24, 30), "Buzzards": (4, 3, 13, 19, 44)}
# t1-farm-crops: hectares by year 2021-2025
YEARS = [2021, 2022, 2023, 2024, 2025]
WHEAT, BARLEY, OATS = [120, 140, 150, 140, 170], [80, 70, 90, 120, 100], [30, 50, 50, 60, 60]
TOTAL = [w + b + o for w, b, o in zip(WHEAT, BARLEY, OATS)]


def _q1_08():
    """Isosceles OBP with O(0,0), B(6,0), area 12, P above the axis: count points P."""
    y = F(2 * 12, 6)
    d2 = lambda p, q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    O, B = (F(0), F(0)), (F(6), F(0))
    conds = [lambda a: d2((a, y), O) - d2((a, y), B), lambda a: d2((a, y), O) - d2(O, B),
             lambda a: d2((a, y), B) - d2(O, B)]
    roots = set()
    for f in conds:  # each is a polynomial of degree <= 2 in a
        c0 = f(F(0)); c1 = (f(F(1)) - f(F(-1))) / 2; c2 = (f(F(1)) + f(F(-1))) / 2 - c0
        if c2 == 0:
            roots.add(round(float(-c0 / c1), 9))
        else:
            disc = c1 * c1 - 4 * c2 * c0
            if disc >= 0:
                for s in (1, -1):
                    roots.add(round((float(-c1) + s * sqrt(disc)) / float(2 * c2), 9))
    return [2, 3, 4, 5, 6].index(len(roots))


def _q1_09():
    games = list(combinations(range(6), 2))
    pairs = list(combinations(games, 2))
    r = F(sum(1 for g, h in pairs if not set(g) & set(h)), len(pairs))
    return [r.numerator, r.denominator]


def _q1_12():
    rate = {k: r / p for k, (p, r, e) in FACT.items()}
    per = {k: F(p, e) for k, (p, r, e) in FACT.items()}
    tp, tr, te = (sum(v[i] for v in FACT.values()) for i in range(3))
    most_emp = max(FACT, key=lambda k: FACT[k][2])
    stmts = [
        lambda: per[most_emp] == min(per.values()),
        lambda: FACT["Aldgate"][1] + FACT["Brindle"][1] > tr / 2,
        lambda: per["Aldgate"] > F(tp, te),
        lambda: F(FACT["Carrow"][0], tp) > 2 * (FACT["Carrow"][1] / tr),
        lambda: median(rate.values()) == tr / tp,
    ]
    return pick(stmts, lambda s: s())


def _q2m_10():
    good = sum(1 for c in combinations(range(7), 3) if all(b - a > 1 for a, b in zip(c, c[1:])))
    return [F(1, 7), F(2, 7), F(2, 5), F(3, 7), F(4, 7)].index(F(good, comb(7, 3)))


def _q2m_11():
    a = next(a for a in [F(i, 4) for i in range(-80, 81)] if (3 * a + 1) / (3 + 2) == 2)
    g = lambda x: (a * x + 1) / (x + 2)
    r = g(g(F(3)))
    return [r.numerator, r.denominator]


def _pts(name, win=3):
    w, d, l, gs, gc = LEAGUE[name]
    return win * w + d


def _q2m_13():
    top = max(LEAGUE, key=_pts)
    most_wins = max(LEAGUE, key=lambda k: LEAGUE[k][0])
    return [0, 1, 2, 3, 4].index(_pts(top) - _pts(most_wins))


def _q2m_15():
    order = lambda win: sorted(LEAGUE, key=lambda k: -_pts(k, win))
    draw_share = {k: F(v[1], _pts(k)) for k, v in LEAGUE.items()}
    h = LEAGUE["Harriers"]
    stmts = [
        lambda: order(3) == order(2) and len({_pts(k, 2) for k in LEAGUE}) == 6 and len({_pts(k) for k in LEAGUE}) == 6,
        lambda: all(draw_share["Falcons"] > s for k, s in draw_share.items() if k != "Falcons"),
        lambda: 3 * (h[0] + h[1]) > _pts("Kestrels"),
    ]
    return pick(stmts, lambda s: s())


def _q2h_01():
    xs = [x for x in range(1, 300) if ndiv(x) == 6]
    ys = [y for y in range(1, 300) if ndiv(y) == 4]
    return qc((ndiv(x * y), 24) for x in xs for y in ys)


def _q2h_03():
    def area2(a, b, c):  # Heron, squared
        s = F(a + b + c, 2)
        return s * (s - a) * (s - b) * (s - c)
    return qc([(area2(10, 10, 12), area2(10, 10, 16))])


def _q2h_08():
    n = next(n for n in range(3, 200) if (n - 2) * 180 == 2340)
    return sum(1 for i, j in combinations(range(n), 2) if (j - i) % n not in (1, n - 1))


def _q2h_09():
    def ok(k):
        disc = k * k - 36  # x² − kx + 9
        if disc <= 0:
            return False
        r = sqrt(disc)
        return (float(k) - r) / 2 > 0 and (float(k) + r) / 2 > 0
    return pick([F(-10), F(-7), F(-6), F(0), F(6), F(13, 2), F(9)], ok)


def _q2h_10():
    # path over two adjacent faces from (0,0,0) to (6,6,6), crossing the shared edge at height t
    best = min(sqrt(36 + t * t) + sqrt(36 + (6 - t) ** 2) for t in [i / 1000 for i in range(6001)])
    opts = [6 * sqrt(3), 6 * sqrt(5), 6 + 6 * sqrt(2), 6 * sqrt(6), 18]
    i = min(range(5), key=lambda j: abs(opts[j] - best))
    assert abs(opts[i] - best) < 1e-6
    return i


def _q2h_11():
    games = list(combinations(range(5), 2))
    hits = 0
    for o in product((0, 1), repeat=len(games)):
        wins = [0] * 5
        for g, w in zip(games, o):
            wins[g[w]] += 1
        hits += max(wins) == 4
    r = F(hits, 2 ** len(games))
    return [r.numerator, r.denominator]


def _q2h_15():
    dw = [WHEAT[i] - WHEAT[i - 1] for i in range(1, 5)]
    db = [BARLEY[i] - BARLEY[i - 1] for i in range(1, 5)]
    stmts = [
        lambda: F(OATS[4], TOTAL[4]) > F(OATS[0], TOTAL[0]),
        lambda: all(F(TOTAL[i], TOTAL[i - 1]) > F(105, 100) for i in range(1, 5)),
        lambda: [i for i in range(4) if dw[i] < 0] == [db.index(max(db))] and db.count(max(db)) == 1,
        lambda: median(OATS) > F(sum(OATS), len(OATS)),
    ]
    return pick(stmts, lambda s: s())


CHECKS = {
    # ---- Q1
    "T1-Q1-01": lambda: qc([(reduce(gcd, [k for k in range(1, 5001) if k * k % 72 == 0]), 12)]),
    "T1-Q1-02": lambda: qc((x, x * x) for x in GRID if x ** 3 < x),
    # Q at the origin, R = (8, 0), P = (a, b) with a² + b² = 36; angle PQR > 90° means a < 0; PR² = 100 − 16a
    "T1-Q1-03": lambda: qc(((F(-i, 100) - 8) ** 2 + (36 - F(-i, 100) ** 2), 100) for i in range(1, 600)),
    "T1-Q1-04": lambda: qc([(F(sum(1 for i, j in combinations("TTTTTDDD", 2) if i == j), comb(8, 2)), F(1, 2))]),
    "T1-Q1-05": lambda: [20, 30, 45, 60, 75].index(next(
        x for x in range(1, 500) if F(15, 100) * 40 + F(40, 100) * x == F(30, 100) * (40 + x))),
    "T1-Q1-06": lambda: sum(1 for d in range(1, 7201) if 7200 % d == 0 and isqrt(d) ** 2 == d),
    "T1-Q1-07": lambda: pick([-9, -8, -6, -5, 0, 7], lambda v: v in {x * x - 6 * x for x in range(-10, 20) if abs(x - 4) < 3}),
    "T1-Q1-08": _q1_08,
    "T1-Q1-09": _q1_09,
    "T1-Q1-10": lambda: [F(29, 10), F(31, 10), F(33, 10), F(35, 10), F(37, 10)].index(round(
        sum(v[1] for v in FACT.values()) / sum(v[0] for v in FACT.values()) * 100, 1)),
    "T1-Q1-11": lambda: [40, 60, F(200, 3), 80, 100].index(
        (FACT["Dunmore"][1] / (FACT["Aldgate"][1] / FACT["Aldgate"][0]) - FACT["Dunmore"][0]) / FACT["Dunmore"][0] * 100),
    "T1-Q1-12": _q1_12,
    # ---- Q2M
    "T1-Q2M-01": lambda: qc((n % 4, n % 3) for n in range(1, 400) if n % 6 == 4),
    "T1-Q2M-02": lambda: qc([(7 * next(k for k in range(1, 10000) if F(7 * k, 3 * k + 400) == F(7, 4)), 2500)]),
    "T1-Q2M-03": lambda: qc(((3 * t + 3) / (5 * t + 5), F(3, 5)) for t in POS),
    "T1-Q2M-04": lambda: qc((p * r * r - (2 * r) ** 2 / 2, (2 * r) ** 2 - p * r * r)
                            for p in (F(314, 100), F(315, 100)) for r in POS[:-2] + [F(10**6)]),
    "T1-Q2M-05": lambda: qc([(2 * len(list(combinations(range(8), 2))), len(list(combinations(range(8), 3))))]),
    # p + q = 1/12 and 6p + 21q = 1
    "T1-Q2M-06": lambda: [12, 15, 16, 18, 20].index(next(
        h for h in range(1, 200) if (lambda p: 6 * p + 21 * (F(1, 12) - p) == 1)(F(1, h)))),
    "T1-Q2M-07": lambda: [0, 1, 3, 7, 9].index(pow(7, 45) * pow(3, 22) % 10),
    "T1-Q2M-08": lambda: (1 - F(110, 100) / F(125, 100)) * 100,
    # the height to the side of length 9 is at most 5 (the other side), and any height in (0, 5] is possible
    "T1-Q2M-09": lambda: pick([F(4), F(12), F(20), F(45, 2), F(24), F(45)], lambda v: 0 < 2 * v / 9 <= 5),
    "T1-Q2M-10": _q2m_10,
    "T1-Q2M-11": _q2m_11,
    "T1-Q2M-12": lambda: [7, 14, 17, 19, 21].index(sum(
        x for x in range(-100, 200) if F(28 + x, 5) == sorted([2, 5, 9, 12, x])[2])),
    "T1-Q2M-13": _q2m_13,
    "T1-Q2M-14": lambda: median(F(v[3] - v[4]) for v in LEAGUE.values()),
    "T1-Q2M-15": _q2m_15,
    # ---- Q2H
    "T1-Q2H-01": _q2h_01,
    "T1-Q2H-02": lambda: (lambda vals: qc([(min(vals), len(vals))]))([a for a in range(1, 2000) if lcm(a, 18) == 90]),
    "T1-Q2H-03": _q2h_03,
    "T1-Q2H-04": lambda: qc([(F(sum(1 for o in product(range(6), repeat=4) if 0 in o), 6 ** 4), F(1, 2))]),
    "T1-Q2H-05": lambda: qc((x, 2 * y) for x in POS[::3] for y in POS[::3]
                            if F(3, 10) * x + F(6, 10) * y > F(4, 10) * (x + y)),
    "T1-Q2H-06": lambda: [51, 59, 67, 73, 83].index(sum(1 for k in range(1, 301) if (k % 6 == 0) != (k % 9 == 0))),
    "T1-Q2H-07": lambda: [8, 9, 10, 11, 12].index(sum(1 for x in range(-100, 100) if abs(x - 3) + abs(x + 2) < 9)),
    "T1-Q2H-08": _q2h_08,
    "T1-Q2H-09": _q2h_09,
    "T1-Q2H-10": _q2h_10,
    "T1-Q2H-11": _q2h_11,
    # n1, n2, n3 = farms lacking exactly 1, 2, 3 crops; the "lacks" total 10 + 12 + 14 = 36 (the minimum,
    # n1 = 36, is feasible: 10 + 12 + 14 farms each lacking one different crop)
    "T1-Q2H-12": lambda: [0, 4, 7, 10, 14].index(min(
        50 - n1 - n2 - n3 for n1 in range(51) for n2 in range(26) for n3 in range(17)
        if n1 + n2 + n3 <= 50 and n1 + 2 * n2 + 3 * n3 == (50 - 40) + (50 - 38) + (50 - 36))),
    "T1-Q2H-13": lambda: min(range(5), key=lambda i: F(WHEAT[i], TOTAL[i])),
    "T1-Q2H-14": lambda: round(F(8 * WHEAT[4] + 6 * BARLEY[4] + F(9, 2) * OATS[4], TOTAL[4]), 1),
    "T1-Q2H-15": _q2h_15,
}
