"""Answer checks for practice-bank Quant batch B (P-Q-101..137): each computes the key from the problem's conditions."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations_with_replacement as cwr
from math import isqrt, sqrt
import random

from verify_quant import qc, pick

GRID = sorted({F(i, 8) for i in range(-400, 401)} | {F(1, 1000), F(-1, 1000), F(10**6), F(-10**6)})


def _var(xs):
    n = len(xs)
    m = F(sum(xs), n)
    return sum((F(x) - m) ** 2 for x in xs) / n


def _closest(options, value):
    return min(range(len(options)), key=lambda i: abs(options[i] - value))


# ---------- Geometry ----------
def _g101():  # triangle 7, 10, x with x an integer
    return qc((17 + x, 33) for x in range(1, 40) if 7 + 10 > x and 7 + x > 10 and 10 + x > 7)


def _g102():
    vols = [F(c * c * h) for c, h in ((20, 12), (12, 20))]  # volume * 4pi
    ratio = max(vols) / min(vols)
    return [F(6, 5), F(4, 3), F(3, 2), F(5, 3), F(25, 9)].index(ratio)


def _g103():  # right triangle hypotenuse 10: a + b over many a
    return qc((a + sqrt(100 - a * a), 14) for a in [i / 100 for i in range(1, 1000)])


def _g104():  # circles r=4, R=9 externally tangent; area of quadrilateral centres, P, Q
    L = next(l for l in range(1, 100) if l * l + (9 - 4) ** 2 == (4 + 9) ** 2)  # tangent line = x-axis
    pts = [(0, 0), (L, 0), (L, 9), (0, 4)]  # P, Q, centre of big circle, centre of small circle
    return abs(sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))) / 2


def _g105():  # ring between circumcircle and incircle of regular decagon, side 8; in units of pi
    from math import pi, sin, tan
    s, n = 8, 10
    R = s / (2 * sin(pi / n))
    r = s / (2 * tan(pi / n))
    return [8, 12, 16, 24, 32].index(round(R * R - r * r))


def _g106():  # PQ=8, PR=15, area 48: both placements of the foot of the altitude from Q
    h = F(2 * 48, 15)
    d2 = 64 - h * h
    d = F(isqrt(d2.numerator), isqrt(d2.denominator))
    assert d * d == d2
    cases = []
    for foot in (d, -d):  # foot position along line PR measured from P
        qr2 = h * h + (15 - foot) ** 2
        cases.append((qr2, F(17 * 17)))
    return qc(cases)


def _g107():
    out = []
    for x in (17, 20, 23, 25, 27, 30):
        sides = sorted((7, 24, x))
        if sides[0] + sides[1] <= sides[2]:
            continue
        if sides[2] ** 2 > sides[0] ** 2 + sides[1] ** 2:
            out.append(x)
    return pick([17, 20, 23, 25, 27, 30], lambda v: v in out)


def _g108():  # rectangle A(0,0) B(9,0) C(9,12) D(0,12); feet of perpendiculars from A and C on BD
    B, D = (9, 0), (0, 12)
    dx, dy = D[0] - B[0], D[1] - B[1]
    L2 = dx * dx + dy * dy

    def t(P):
        return F((P[0] - B[0]) * dx + (P[1] - B[1]) * dy, L2)
    L = isqrt(L2)
    pq = abs(t((0, 0)) - t((9, 12))) * L
    return [F(18, 5), F(21, 5), F(24, 5), F(27, 5), F(6)].index(pq)


def _g109():  # square P(0,0) Q(2,0) R(2,2) S(0,2); M mid PQ, N mid QR; X = SM ∩ PN; area PXM / area square
    P, M, S, N = (F(0), F(0)), (F(1), F(0)), (F(0), F(2)), (F(2), F(1))
    # intersection of line S-M and line P-N
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = S, M, P, N
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    X = (px, py)
    area = abs((M[0] - P[0]) * (X[1] - P[1]) - (X[0] - P[0]) * (M[1] - P[1])) / 2
    r = area / 4
    return [r.numerator, r.denominator]


# ---------- Coordinate geometry & functions ----------
def _c110():  # y = x^2 - 6x + k with two distinct positive roots; compare k with 0
    cases = []
    for k in GRID:
        disc = 36 - 4 * k
        if disc <= 0:
            continue
        s = sqrt(disc)
        if (6 - s) / 2 > 0 and (6 + s) / 2 > 0:
            cases.append((k, 0))
    return qc(cases)


def _c111():
    m_k = F(0 - (-4), 6 - 0)
    m_m = -1 / m_k
    x = F(4) / m_m * -1  # y = m_m*x - 4 = 0 -> x = 4/m_m
    x = F(4) / m_m
    return [F(-8, 3), F(-3, 2), F(3, 2), F(8, 3), F(6)].index(x)


def _c112():  # line through (4,3), positive intercepts a,b: 4/a + 3/b = 1
    cases = []
    for a in [F(i, 8) for i in range(33, 2000)] + [F(8)]:
        if a <= 4:
            continue
        b = 3 * a / (a - 4)
        cases.append((a * b / 2, F(24)))
    return qc(cases)


def _c113():  # f(x) = 4x - x^2: count real x with f(f(x)) = 0
    ys = [y for y in range(-50, 51) if 4 * y - y * y == 0]
    count = 0
    for y in ys:  # x^2 - 4x + y = 0
        disc = 16 - 4 * y
        count += 2 if disc > 0 else 1 if disc == 0 else 0
    return [1, 2, 3, 4, 5].index(count)


def _c114():  # circle centre (3,-3) through (6,1); area of quadrilateral of axis crossings
    import math
    r2 = (6 - 3) ** 2 + (1 + 3) ** 2
    pts = [(x, 0) for x in range(-100, 101) if (x - 3) ** 2 + 9 == r2]
    pts += [(0, y) for y in range(-100, 101) if 9 + (y + 3) ** 2 == r2]
    assert len(pts) == 4
    pts.sort(key=lambda p: math.atan2(p[1] + 3, p[0] - 3))
    return abs(sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))) / 2


def _c115():  # h(x+4) = h(x), h(x+6) = h(x); h(1) = 3, h(2) = 7: which statements are forced
    known = {F(1): 3, F(2): 7}
    shifts = [4 * i + 6 * j for i in range(-12, 13) for j in range(-12, 13)]

    def val(x):
        x = F(x)
        for s in shifts:
            if x + s in known:
                return known[x + s]
        return ("free", x)

    def same(x, y):
        return any(F(x) - F(y) == s for s in shifts)
    stmts = [
        lambda: val(7) == 3, lambda: val(4) == 7, lambda: val(-3) == 3,
        lambda: val(F(1, 2)) == 3, lambda: val(6) == 3, lambda: same(F(5, 2), F(1, 2)),
    ]
    return pick(range(6), lambda i: stmts[i]())


def _c116():  # P on y = 2x + 3; distance to origin vs 7/5 (compare squares)
    return qc((x * x + (2 * x + 3) ** 2, F(49, 25)) for x in GRID)


def _c117():  # region between y=|x-3|-2 and y=2; fraction in the first quadrant
    n = 400
    tot = fq = F(0)
    ys = [F(-2) + F(4 * i, n) for i in range(n + 1)]  # includes y = 0 and y = 1 as grid points

    def width(y, lo=None):
        a, b = 3 - (y + 2), 3 + (y + 2)
        if lo is not None:
            a = max(a, lo)
        return b - a
    for y0, y1 in zip(ys, ys[1:]):
        tot += (width(y0) + width(y1)) / 2 * (y1 - y0)
        if y0 >= 0:
            fq += (width(y0, 0) + width(y1, 0)) / 2 * (y1 - y0)
    r = fq / tot
    return [r.numerator, r.denominator]


# ---------- Statistics ----------
def _s118():  # 7 distinct positive ints, mean 10, median 8: minimise the largest
    best = None
    for a in range(1, 8):
        for b in range(a + 1, 8):
            for c in range(b + 1, 8):
                for e in range(9, 70):
                    for f in range(e + 1, 70):
                        g = 70 - (a + b + c + 8 + e + f)
                        if g > f:
                            best = g if best is None else min(best, g)
    return qc([(best, 16)])


def _s119():
    n = 5 * 18 - 4 * 16
    m = 5 * 18 - 4 * 19
    new = F(5 * 18 + n - m, 4)
    return [F(204, 10), F(232, 10), F(240, 10), F(255, 10), F(260, 10)].index(new)


def _s120():  # list X: 10 numbers, mean 50, SD 4; add 46 and 54. Both SD conventions.
    cases = []
    for ddof in (0, 1):
        ss = F(16) * (10 - ddof)  # sum of squared deviations of X
        new_ss = ss + (46 - 50) ** 2 + (54 - 50) ** 2
        cases.append((new_ss / (12 - ddof), F(16)))
    return qc(cases)


def _s121():  # 7 positive ints a<=b<=c<=d=6<=e<=f<=g, sum 49, unique mode 8; max range
    best = None
    for a in range(1, 7):
        for b in range(a, 7):
            for c in range(b, 7):
                for e in range(6, 49):
                    for f in range(e, 49):
                        g = 49 - (a + b + c + 6 + e + f)
                        if g < f:
                            break
                        cnt = Counter([a, b, c, 6, e, f, g]).most_common()
                        if cnt[0][0] == 8 and (len(cnt) == 1 or cnt[1][1] < cnt[0][1]):
                            r = g - a
                            best = r if best is None else max(best, r)
    return best


def _s122():  # 9 numbers, mean 40, median 38 (+ add 40): which statements always hold
    rng = random.Random(3)
    samples = [[30, 34, 36, 37, 38, 38, 45, 51, 51], [26, 30, 33, 36, 38, 41, 44, 56, 56]]
    for _ in range(4000):
        xs = sorted(rng.randint(10, 80) for _ in range(9))
        if sum(xs) == 360 and xs[4] == 38 and len(set(xs)) > 1:
            samples.append(xs)

    def med(xs):
        xs = sorted(xs)
        n = len(xs)
        return F(xs[n // 2]) if n % 2 else F(xs[n // 2 - 1] + xs[n // 2], 2)
    tests = [
        lambda o, n: F(sum(n), len(n)) == 40,
        lambda o, n: med(n) == 38,
        lambda o, n: _var(n) < _var(o),
        lambda o, n: max(n) - min(n) == max(o) - min(o),
        lambda o, n: med(n) > 38,
    ]
    return [i for i, t in enumerate(tests) if all(t(xs, xs + [40]) for xs in samples)]


def _s123():  # combined mean 74 forces the ratio; compare nx with 1.5 ny
    return qc((F(nx), F(3, 2) * ny) for nx in range(1, 200) for ny in range(1, 200)
              if F(70 * nx + 80 * ny, nx + ny) == 74)


def _s124():
    lists = [(0, 0, 5, 10, 10), (0, 0, 0, 10, 10), (0, 0, 1, 10, 10), (0, 0, 0, 0, 10), (1, 1, 1, 9, 9)]
    v = [_var(l) for l in lists]
    assert v.count(max(v)) == 1
    return v.index(max(v))


def _s125():  # girls g, boys b; mean 70 now; 4 girls at 85 join and the mean becomes 72: boys
    sol = [b for g in range(1, 200) for b in range(1, 200)
           if 75 * g + 62 * b == 70 * (g + b) and 75 * g + 62 * b + 4 * 85 == 72 * (g + b + 4)]
    assert len(sol) == 1
    return sol[0]


def _s126():
    means = set()
    for l in cwr(range(1, 30), 6):
        if l[-1] - l[0] != 6 or l[2] + l[3] != 10:
            continue
        c = Counter(l).most_common()
        if c[0][0] != 4 or (len(c) > 1 and c[1][1] == c[0][1]):
            continue
        means.add(F(sum(l), 6))
    return qc((m, 5) for m in means)


def _s127():  # 30 students mean 74; 20 passed mean 80; one non-passer (44) retakes and passes
    fail_total = 30 * 74 - 20 * 80
    return F(fail_total - 44, 10 - 1)


def _s128():
    def med(v):
        m = len(v)
        return F(v[m // 2]) if m % 2 else F(v[m // 2 - 1] + v[m // 2], 2)

    def iqr(xs):
        xs = sorted(xs)
        n = len(xs)
        h = n // 2
        return med(xs[n - h:]) - med(xs[:h])  # odd n: median excluded; even n: halves of n/2
    xs = [2, 5, 7, 8, 11, 13, 14, 19, 22, 30, 41]
    return [0, 1, 2, 3, 4].index(iqr(xs) - iqr(xs + [12]))


# ---------- Data interpretation ----------
CALDER = {"Tents": (25, 25), "Boots": (30, 20), "Packs": (20, -20), "Stoves": (15, 50), "Other": (10, 0)}
TOTAL25 = 640


def _sales():
    s25 = {k: F(share * TOTAL25, 100) for k, (share, _) in CALDER.items()}
    s24 = {k: s25[k] / (1 + F(chg, 100)) for k, (_, chg) in CALDER.items()}
    return s25, s24


def _d129():
    s25, s24 = _sales()
    growth = (sum(s25.values()) - sum(s24.values())) / sum(s24.values()) * 100
    return [8, 11, 15, 16, 20].index(round(growth))


def _d130():
    s25, s24 = _sales()
    return qc([(s25["Tents"] - s24["Tents"], s25["Boots"] - s24["Boots"])])


def _d131():
    s25, s24 = _sales()
    t25, t24 = sum(s25.values()), sum(s24.values())
    return pick(list(CALDER), lambda k: s24[k] / t24 > s25[k] / t25)


NORTH = [40, 30, 50, 40, 60, 70]
SOUTH = [30, 40, 40, 50, 50, 60]
MUSEUM = [75, 100, 100, 150, 125, 100, 125]
PARK = [150, 175, 150, 225, 250, 225, 300]


def _d132():  # percent increase Jan -> Jun: South (A) vs North (B)
    return qc([(F(SOUTH[5] - SOUTH[0], SOUTH[0]), F(NORTH[5] - NORTH[0], NORTH[0]))])


def _d133():  # South Apr-Jun increase needed for combined Apr-Jun = 1.5 x combined Jan-Mar
    q1 = sum(NORTH[:3]) + sum(SOUTH[:3])
    need = F(3, 2) * q1 - sum(NORTH[3:])
    return round((need - sum(SOUTH[3:])) / sum(SOUTH[3:]) * 100)


def _d134():  # months (Feb..Jun) in which North's share exceeds the previous month's
    share = [F(n, n + s) for n, s in zip(NORTH, SOUTH)]
    return pick(range(1, 6), lambda m: share[m] > share[m - 1])


def _d135():
    i = 2  # 2021 -> 2022
    return qc([(F(MUSEUM[i + 1] - MUSEUM[i], MUSEUM[i]), F(PARK[i + 1] - PARK[i], PARK[i]))])


def _d136():
    n = sum(1 for m, p in zip(MUSEUM, PARK) if p > 2 * m)
    return [0, 1, 2, 3, 4].index(n)


def _d137():  # 2027: museum x0.8 x1.2, park x1.1 x0.9, from 2025 values
    m = F(MUSEUM[-1]) * F(80, 100) * F(120, 100)
    p = F(PARK[-1]) * F(110, 100) * F(90, 100)
    return round(m / p * 100)


CHECKS = {"P-Q-%d" % (101 + i): fn for i, fn in enumerate([
    _g101, _g102, _g103, _g104, _g105, _g106, _g107, _g108, _g109,
    _c110, _c111, _c112, _c113, _c114, _c115, _c116, _c117,
    _s118, _s119, _s120, _s121, _s122, _s123, _s124, _s125, _s126, _s127, _s128,
    _d129, _d130, _d131, _d132, _d133, _d134, _d135, _d136, _d137])}
