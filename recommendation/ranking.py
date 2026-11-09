def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: candidate["score"],
        reverse=True
    )