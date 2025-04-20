def max_subsequence(nums, m):
        to_remove = len(nums) - m
        stack = []
        for num in nums:
            print(num,to_remove)
            while to_remove > 0 and stack and stack[-1] < num:
                stack.pop()
                to_remove -= 1
            stack.append(num)
            print(stack)
        return stack[:m]

# max_subsequence([9,1,2,5,8,3],4)

nums1 = [3,4,6,5]
nums2 = [9,1,2,5,8,3]

print(5-len(nums2))