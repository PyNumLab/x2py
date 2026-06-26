def rank_weighted_sum(
    values: Const(Float64[...])
) -> Float64: ...

def bump_assumed_rank(
    values: Float64[...]
) -> None: ...

def rank_pair_score(
    left: Const(Float64[...]),
    right: Const(Float64[...])
) -> Int32: ...
