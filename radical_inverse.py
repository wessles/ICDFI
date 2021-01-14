"""
This is an implementation of the radical inverse function, described in 'Advanced Global Illumination 2e', section 3.6.7.
Notes:
- I've written one special version which uses standard bit-manipulation to calculate base-2 radical inverses.
- The code is in Python because it is simple to translate to other languages like C++
- A subset of this function, the 1D base-2 variant, is known as the "van der Corput sequence", which may help in research.

For more details, here's a great resource:
    http://www.pbr-book.org/3ed-2018/Sampling_and_Reconstruction/The_Halton_Sampler.html

Author: Wesley LaFerriere
Date: 1/9/2021
"""

import math

# RADICAL INVERSE OF BASE 2:

def radical_inverse_2(N):
    if N == 0:
        return 0
    bin_digits = math.floor(math.log2(N)) + 1
    res = 0.0
    for i in range(0, bin_digits):
        x = (N >> i) & 0b1 # x = ith binary digit of N
        res += x / (2 << i)
    return res

# RADICAL INVERSE OF ARBITRARY BASE B:

def radical_inverse(N, b):
    if N == 0:
        return 0
    digits = math.floor(math.log(N,b)) + 1
    res = 0.0
    for i in range(0, digits):
        x = math.floor(N/(b**i)) % b # x = ith digit of N
        res += x / (b**(i+1))
    return res