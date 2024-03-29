"""
Title: QR Code lite
Author: David Zhang
Date: 8/18/2019
Code version: 1.0

Adapted from: Project Nayuki (MIT License)
https://www.nayuki.io/page/qr-code-generator-library
"""

import re

""" Limits for QR Code versions, larger number means more capacity """
MIN_VERSION = 1
MAX_VERSION = 40

"""For use in getPenaltyScore(), when evaluating which mask is best."""
_PENALTIES = [3, 10, 40]

""" Number of required error correction codewords given Version and ECL """
ECC_CODEWORDS_PER_BLOCK = (
    (None, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28,
     30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
     30, 30, 30, 30),  # Low

    (None, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28,
     26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28,
     28, 28, 28, 28),  # Medium

    (None, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28,
     28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
     30, 30, 30, 30),  # Quartile

    (None, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28,
     28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
     30, 30, 30, 30)  # High
)

""" Number of required error correction blocks given Version and ECL """
NUM_ERROR_CORRECTION_BLOCKS = (
    (None, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9,
     10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),  # Low

    (None, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17,
     17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47,
     49),  # Medium

    (None, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20,
     23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65,
     68),  # Quartile

    (None, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25,
     25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77,
     81)  # High
)

""" 0 - 7 different masks - pick the one with lowest penalty score """
_MASK_PATTERNS = (
    (lambda x, y: (x + y) % 2),
    (lambda x, y: y % 2),
    (lambda x, y: x % 3),
    (lambda x, y: (x + y) % 3),
    (lambda x, y: (x // 3 + y // 2) % 2),
    (lambda x, y: x * y % 2 + x * y % 3),
    (lambda x, y: (x * y % 2 + x * y % 3) % 2),
    (lambda x, y: ((x + y) % 2 + x * y % 3) % 2),
)

"""Numeric mode: iff each character is in the range 0 to 9."""
NUMERIC_REGEX = re.compile(r"[0-9]*\Z")

"""Alphanumeric mode: 0 to 9, A to Z (uppercase only), space, dollar,
percent, asterisk, plus, hyphen, period, slash, colon."""
ALPHANUMERIC_REGEX = re.compile(r"[A-Z0-9 $%*+./:-]*\Z")

"""Dictionary of "0"->0, "A"->10, "$"->37, etc."""
ALPHANUMERIC_ENCODING_TABLE = {ch: i for (i, ch) in enumerate(
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")}
