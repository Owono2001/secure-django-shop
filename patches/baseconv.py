"""
Minimal implementation of baseconv functionality for django-cryptography.
This example provides a simple base36 encoder.
"""

def base36_encode(number):
    """
    Convert an integer to a base36 string.
    """
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    if number == 0:
        return alphabet[0]
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36

