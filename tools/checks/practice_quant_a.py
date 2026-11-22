"""Answer checks for practice questions P-Q-001..043 (arithmetic, algebra, percents/ratios/rates, counting/probability)."""
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb, factorial, gcd, isqrt, perm

from verify_quant import qc, pick


def _d(n):
    c, k = 0, 1
    while k * k <= n:
        if n % k == 0:
            c += 1 if k * k == n else 2
        k += 1
    return c


def _lcm(a, b):
    return a * b // gcd(a, b)


GRID = sorted({F(i, 8) for i in range(-800, 801)} | {F(1, 1000), F(-1, 1000), F(10**6), F(-10**6)})
POS = [x for x in GRID if x > 0]


def _c3():
    ns = [n for n in range(1, 3000) if _d(n) == 3]
    return qc((_d(n ** 3), 9) for n in ns)


def _c11(options):
    vals = {(pow(13, 4 * n + 2, 10) * pow(17, 4 * n + 3, 10)) % 10 for n in range(1, 30)}
    assert len(vals) == 1
    return options.index(str(vals.pop()))


def _trailing(n):
    s = str(factorial(n))
    return len(s) - len(s.rstrip("0"))


def _c8():
    opts = [lambda n: n ** 3 + 5 * n, lambda n: 2 * n ** 3 + 4 * n, lambda n: n * (n + 1) * (2 * n + 1),
            lambda n: (n + 1) * (n + 2), lambda n: (n + 2) * (n + 3), lambda n: n ** 3 + 11 * n]
    return pick(opts, lambda f: all(f(n) % 6 == 0 for n in range(-60, 61)))


def _c12():
    return sum(1 for x in range(1, 400) for y in range(1, 400) if F(1, x) + F(1, y) == F(1, 12))


def _c20():
    return min((8 - 2 * y) ** 2 + 4 * y * y for y in [F(i, 8) for i in range(-800, 801)] if 8 - 2 * y <= 2)


def _c21():
    sol = [x for x in (F(i, 4) for i in range(-800, 801)) if abs(x - 1) > abs(x + 3)]
    opts = [lambda x: x < 0, lambda x: x < -3, lambda x: x * x > 1, lambda x: x * x - 2 * x > 3,
            lambda x: x > -5, lambda x: abs(x + 2) > 1]
    return pick(opts, lambda f: all(f(x) for x in sol))


def _c22():
    s = F(5)
    p = s / F(5, 3)  # 1/x + 1/y = s/p
    v = (s ** 3 - 3 * p * s) / p  # (x^3 + y^3)/(xy)
    r = float(s * s - 4 * p) ** 0.5  # numeric check with the actual roots
    x, y = (float(s) + r) / 2, (float(s) - r) / 2
    assert abs(x * x / y + y * y / x - float(v)) < 1e-9 and abs(1 / x + 1 / y - 5 / 3) < 1e-9
    return [v.numerator, v.denominator]


def _c16(options):
    xs = [k / 64 for k in range(-640, 641) if abs(4 ** (k / 64) + 2 ** (k / 64 + 1) - 8) < 1e-9]
    return options.index(str(round(sum(xs))))


def _c18():
    xs = [k / 8 for k in range(-80, 4000) if k / 8 + 10 >= 0 and abs((k / 8 - 2) * (k / 8 + 10) ** 0.5 - (k / 8 + 10)) < 1e-9]
    return round(sum(xs))


def _c19():
    xs = [k / 8 for k in range(8, 4000) if abs((5 * k / 8 + 4) ** 0.5 - (k / 8 - 1) ** 0.5 - 3) < 1e-9]
    return sum(xs)


def _c26(options):
    ra, rb, rc = F(1, 6), F(1, 9), F(-1, 18)
    level, t, step = F(0), F(0), F(1, 60)
    while level < 1:
        level += (ra + rc if t < 2 else ra + rb + rc) * step
        t += step
    s = str(float(t))
    return options.index(s[:-2] if s.endswith(".0") else s)


def _c27(options):
    z = F(1)
    y = F(5, 4) * z
    x = F(3, 5) * y
    pct = (z - x) / x * 100
    vals = [20, 25, F(100, 3), 75, F(400, 3)]
    return vals.index(pct)


def _c28():
    j, n = F(20), 0
    while j / 20 >= F(7, 10):
        j = j - 4 * j / 20 + 2
        n += 1
    return n


def _c29():
    done, day = F(0), 0
    while True:
        day += 1
        r = F(1, 20) if day % 2 else F(1, 12)
        if done + r >= 1:
            return float(day - 1 + (1 - done) / r)
        done += r


def _c30():
    y = F(1)
    x = y * F(6, 5)
    z = y / F(3, 4)
    stmts = [x == z * F(9, 10), x == z * F(95, 100), z == x * F(11, 10), x - y == x / 6, z - y == z / 4, y == x * F(4, 5)]
    return [i for i, s in enumerate(stmts) if s]


def _c31():
    red = F(3) * F(3, 4)
    total = red / F(2, 3)
    green_left = total - red
    f = 1 - green_left / 2
    return [f.numerator, f.denominator]


def _c32():
    adj = sum(1 for p in permutations(range(7)) if abs(p.index(0) - p.index(1)) == 1)
    return qc([(adj, 5040 - adj)])


def _c33():
    cards = ["R"] * 6 + ["B"] * 4
    p = F(sum(1 for i in range(10) for j in range(10) if i != j and cards[j] == "R"), 90)
    return qc([(p, F(3, 5))])


def _c34():
    a = sum(1 for x in range(1, 11) for y in range(1, 11) if 10 - x - y >= 1)
    b = sum(1 for x in range(0, 8) for y in range(0, 8) if 7 - x - y >= 0)
    return qc([(a, b)])


def _c35():
    pe, pf = F(3, 5), F(7, 10)
    cases = []
    for i in range(0, 101):
        t = F(i, 100)  # P(E and F)
        cells = [t, pe - t, pf - t, 1 - pe - pf + t]
        if all(c >= 0 for c in cells):
            cases.append((t, F(3, 10)))
    return qc(cases)


def _c36(options):
    n = sum(1 for k in range(1000, 10000)
            if all(a < b for a, b in zip(str(k), str(k)[1:])) or all(a > b for a, b in zip(str(k), str(k)[1:])))
    return options.index(str(n))


def _c37(options):
    n = sum(1 for p in set(permutations("BALLOON")) if "LL" not in "".join(p) and "OO" not in "".join(p))
    return options.index(str(n))


def _c38(options):
    people = [("M", i) for i in range(5)] + [("P", i) for i in range(4)]
    n = 0
    for c in combinations(people, 4):
        kinds = {k for k, _ in c}
        if len(kinds) == 2 and not (("M", 0) in c and ("M", 1) in c):
            n += 1
    return options.index(str(n))


def _c39():
    n = 0
    for p in permutations(range(6)):  # p[seat] = person; 0 Ann, 1 Ben, 2 Cal, 3 Dee
        seat = {person: i for i, person in enumerate(p)}
        near = lambda a, b: (seat[a] - seat[b]) % 6 in (1, 5)
        if not near(0, 1) and near(2, 3):
            n += 1
    return n // 6  # rotations are the same seating


def _c40():
    return sum(1 for n in range(1, 1000) if sum(map(int, str(n))) == 12)


def _c41():
    f = sum(1 for a, b, c in product(range(1, 7), repeat=3) if a <= b <= c)
    fr = F(f, 216)
    return [fr.numerator, fr.denominator]


def _c42():
    bag = ["R"] * 4 + ["B"] * 3 + ["G"] * 2
    f = sum(1 for c in combinations(range(9), 4) if len({bag[i] for i in c}) == 2)
    fr = F(f, comb(9, 4))
    return [fr.numerator, fr.denominator]


def _c43():
    vals = [comb(8, 3), comb(7, 2) + comb(7, 3), perm(8, 2), len(set(permutations("AAABBBBB"))),
            sum(1 for c in combinations(range(1, 10), 3) if 9 in c), factorial(8) // (factorial(3) * factorial(4))]
    return pick(vals, lambda v: v == 56)


def _c9():
    s = {x + y for x in range(1, 400) for y in range(1, 400) if gcd(x, y) == 6 and _lcm(x, y) == 360}
    return qc((v, 96) for v in s)


def _c10():
    return qc((_d(x), 4) for x in range(2, 400) if _d(x * x) == 9)


def _c4():
    ns = [n for n in range(100, 1000) if n % 4 == 3 and n % 6 == 5 and n % 7 == 2]
    return ["11", "12", "13", "14", "15"].index(str(len(ns)))


def _c5():
    ds = [d for d in range(1, 7201) if 7200 % d == 0]
    return sum(1 for d in ds if isqrt(d) ** 2 == d or any(k ** 3 == d for k in range(1, 21)))


def _c7():
    ds = [d for d in range(1, 721) if 720 % d == 0]
    f = F(sum(1 for d in ds if d % 6 == 0 or d % 10 == 0), len(ds))
    return [f.numerator, f.denominator]


def _c13():
    return qc((x + 1 / x, F(2)) for x in GRID if x != 0 and x * x > x)


def _c23():
    return qc((F(100 - p, 100) * F(100 + q, 100), F(1)) for p in range(1, 100) for q in range(p + 1, 300))


def _c24():
    return qc((F(30 * x + 50 * y, x + y), F(40)) for x in range(1, 40) for y in range(1, 80) if 5 * y > 3 * x)


def _c25():
    return qc((D / (D * F(2, 5) / 40 + D * F(3, 5) / 60), F(50)) for D in [F(1), F(7), F(120), F(10**6)])


def _c2():
    primes = [p for p in range(2, 200) if all(p % k for k in range(2, p))]
    return qc((pow(p, 4, 16), 1) for p in primes)


CHECKS = {
    "P-Q-001": _c3,
    "P-Q-002": _c2,
    "P-Q-003": lambda: ["27", "33", "40", "46", "52"].index(str(sum(1 for n in range(1, 200) if (n % 6 == 0) != (n % 10 == 0)))),
    "P-Q-004": _c4,
    "P-Q-005": _c5,
    "P-Q-006": lambda: sum(n for n in range(1, 300) if _trailing(n) == 6),
    "P-Q-007": _c7,
    "P-Q-008": _c8,
    "P-Q-009": _c9,
    "P-Q-010": _c10,
    "P-Q-011": lambda: _c11(["1", "3", "5", "7", "9"]),
    "P-Q-012": _c12,
    "P-Q-013": _c13,
    "P-Q-014": lambda: qc((1 / (x * x) - 1 / x, x) for x in (F(i, 100) for i in range(1, 100))),
    "P-Q-015": lambda: qc((abs(x), F(5, 2)) for x in (F(i, 2) for i in range(-200, 201)) if abs(x - 2) == 3 * abs(x + 2)),
    "P-Q-016": lambda: _c16(["-2", "0", "1", "2", "3"]),
    "P-Q-017": lambda: ["3", "4", "5", "6", "7"].index(str(sum(1 for x in range(-100, 100) if abs(2 * x - 3) < 11 and x * x > 4))),
    "P-Q-018": _c18,
    "P-Q-019": _c19,
    "P-Q-020": _c20,
    "P-Q-021": _c21,
    "P-Q-022": _c22,
    "P-Q-023": _c23,
    "P-Q-024": _c24,
    "P-Q-025": _c25,
    "P-Q-026": lambda: _c26(["4.5", "5", "5.5", "6", "6.5"]),
    "P-Q-027": lambda: _c27(None),
    "P-Q-028": _c28,
    "P-Q-029": _c29,
    "P-Q-030": _c30,
    "P-Q-031": _c31,
    "P-Q-032": _c32,
    "P-Q-033": _c33,
    "P-Q-034": _c34,
    "P-Q-035": _c35,
    "P-Q-036": lambda: _c36(["126", "210", "252", "336", "420"]),
    "P-Q-037": lambda: _c37(["540", "660", "780", "900", "1260"]),
    "P-Q-038": lambda: _c38(["96", "99", "102", "105", "120"]),
    "P-Q-039": _c39,
    "P-Q-040": _c40,
    "P-Q-041": _c41,
    "P-Q-042": _c42,
    "P-Q-043": _c43,
}
