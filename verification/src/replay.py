"""Exact finite checks for the minimum-rank compression and worked kernel."""

from fractions import Fraction as F
from itertools import combinations, product


def compose(left, right):
    return tuple(left[x] for x in right)


def closure(generators):
    maps = set(generators)
    waiting = list(generators)
    while waiting:
        word = waiting.pop()
        for g in generators:
            longer = compose(g, word)
            if longer not in maps:
                maps.add(longer)
                waiting.append(longer)
    return maps


def rank(mapping):
    return len(set(mapping))


def columns(kernel, idempotent):
    reps = sorted(set(idempotent))
    return [sum(kernel[i][x] for i in reps for x in range(len(kernel)) if idempotent[x] == j)
            for j in reps]


def marginal(generators, weights):
    n = len(generators[0])
    return [[sum(w for g, w in zip(generators, weights) if g[i] == j) for j in range(n)]
            for i in range(n)]


def support_census():
    maps = list(product(range(3), repeat=3))
    tested = 0
    idempotent_checks = 0
    for size in (1, 2, 3):
        for generators in combinations(maps, size):
            semigroup = closure(generators)
            k = min(map(rank, semigroup))
            if k == 1:
                continue
            idempotents = [e for e in semigroup if rank(e) == k and compose(e, e) == e]
            assert idempotents
            kernel = marginal(generators, [F(1, size)] * size)
            for e in idempotents:
                reps = sorted(set(e))
                assert all(e[i] == i for i in reps)
                for g in generators:
                    assert sorted(e[g[i]] for i in reps) == reps
                assert columns(kernel, e) == [1] * k
                idempotent_checks += 1
            tested += 1
    assert tested == 233
    print(tested, "nonsynchronizing supports; all", idempotent_checks, "minimum-rank idempotent checks agree.")


def worked_example():
    e, f, g = (0, 1, 0), (1, 0, 0), (0, 0, 0)
    assert min(map(rank, closure((e, f)))) == 2
    assert e[0] == e[2] and f[1] == f[2] and e[1] != e[2] and f[0] != f[2]
    idempotents = [p for p in product(range(3), repeat=3) if rank(p) >= 2 and compose(p, p) == p]
    assert len(idempotents) == 7
    for numerator in range(17):
        epsilon = F(numerator, 16)
        kernel = marginal((e, f, g), ((1-epsilon)/2, (1-epsilon)/2, epsilon))
        assert columns(kernel, e) == [1+epsilon, 1-epsilon]
        delta = min(max(abs(x-1) for x in columns(kernel, p)) for p in idempotents)
        assert delta == epsilon
        active = (e, f) if epsilon == 0 else (g,) if epsilon == 1 else (e, f, g)
        assert min(map(rank, closure(active))) == (2 if epsilon == 0 else 1)
    print("17 mixtures and all seven affine tests verify the example exactly.")


if __name__ == "__main__":
    support_census()
    worked_example()
