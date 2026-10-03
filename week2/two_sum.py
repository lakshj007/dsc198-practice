def two_sum(nums, target):
    """Return the positions of the two numbers that add to target.

    There is one bug in this function. Session 2 finds it by reading a
    pytest failure rather than by staring at the code.
    """
    seen = {}
    for i, v in enumerate(nums):
        if v in seen:
            continue
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
    return []
