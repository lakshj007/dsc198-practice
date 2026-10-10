# Session 1 solution. Runs once, prints, and exits.
#
# STAGE TWO: uncomment the three marked lines at the bottom. They use pandas,
# which is not part of Python, so the image will have to install it.

def two_sum(nums, target):
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
    return []


cases = [
    ([2, 7, 11, 15], 9),
    ([3, 2, 4], 6),
    ([3, 3], 6),
    ([1, 5, 9, 14], 23),
]

for nums, target in cases:
    print(nums, target, two_sum(nums, target), type(nums))


# STAGE TWO. Uncomment the three lines below.
import pandas as pd
rows = [{"nums": str(n), "target": t, "positions": str(two_sum(n, t))} for n, t in cases]
print(pd.DataFrame(rows).to_string(index=False))