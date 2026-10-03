class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        
        values = {}
        for i in range(len(nums)):
            if target-nums[i] in values:
                return [i, values[target-nums[i]]]
            values[nums[i]] = i 