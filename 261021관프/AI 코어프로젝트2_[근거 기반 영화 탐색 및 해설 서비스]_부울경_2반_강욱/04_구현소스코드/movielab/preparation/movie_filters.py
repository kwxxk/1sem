from ..config import UserError
from .movies import normalize

FILTER_FIELDS = {"min_year", "max_year", "min_runtime", "max_runtime", "min_rating",
                 "max_rating", "language", "genres", "directors", "cast", "countries",
                 "semantic", "unsupported"}
NUMBER_FIELDS = {"min_year", "max_year", "min_runtime", "max_runtime", "min_rating", "max_rating"}
LIST_FIELDS = {"genres", "directors", "cast", "countries"}


def validate_filters(filters):
    if set(filters) != FILTER_FIELDS:
        raise UserError("탐색 조건을 해석하지 못했습니다. 조건을 더 구체적으로 입력하세요.")
    for key in NUMBER_FIELDS:
        value = filters[key]
        if value is not None and (type(value) not in (int, float) or not -1e6 < value < 1e6):
            raise UserError("숫자 조건을 해석하지 못했습니다.")
    for key in LIST_FIELDS:
        if not isinstance(filters[key], list) or not all(isinstance(v, str) and v.strip() for v in filters[key]):
            raise UserError("목록 조건을 해석하지 못했습니다.")
    if any(not isinstance(filters[k], str) for k in ("language", "semantic", "unsupported")):
        raise UserError("탐색 조건의 형식이 올바르지 않습니다.")
    for lower, upper in (("min_year", "max_year"), ("min_runtime", "max_runtime"), ("min_rating", "max_rating")):
        if filters[lower] is not None and filters[upper] is not None and filters[lower] > filters[upper]:
            raise UserError("최솟값이 최댓값보다 큽니다. 조건을 확인하세요.")
    return filters


def matches(movie, filters):
    for field, lo, hi in (("year", "min_year", "max_year"), ("runtime", "min_runtime", "max_runtime"),
                          ("vote_average", "min_rating", "max_rating")):
        value = movie.get(field)
        constrained = filters[lo] is not None or filters[hi] is not None
        if constrained and (value is None or value <= 0):
            return False
        if filters[lo] is not None and value < filters[lo]:
            return False
        if filters[hi] is not None and value > filters[hi]:
            return False
    if filters["language"] and movie.get("original_language") != filters["language"]:
        return False
    for key, field in (("genres", "genres"), ("directors", "director"), ("cast", "cast"),
                       ("countries", "production_countries")):
        actual = {normalize(x) for x in movie.get(field, [])}
        if not all(normalize(v) in actual for v in filters[key]):
            return False
    return True
