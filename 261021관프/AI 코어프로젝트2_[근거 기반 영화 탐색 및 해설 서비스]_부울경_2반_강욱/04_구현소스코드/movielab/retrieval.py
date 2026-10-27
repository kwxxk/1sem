"""F2014: 의미 관련성과 이미 고른 근거와의 차이를 함께 고려한다."""
import math


def cosine(a, b):
    denominator = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / denominator if denominator else 0.0


def mmr_indices(query, vectors, count, weight=0.5):
    if not vectors or count <= 0:
        return []
    relevance = [cosine(query, vector) for vector in vectors]
    selected = [max(range(len(vectors)), key=lambda i: relevance[i])]
    remaining = set(range(len(vectors))) - set(selected)
    while remaining and len(selected) < count:
        winner = max(sorted(remaining), key=lambda i:
            weight * relevance[i] - (1-weight) * max(cosine(vectors[i], vectors[j]) for j in selected))
        selected.append(winner)
        remaining.remove(winner)
    return selected
