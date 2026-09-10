import random
import string

ALPHABET = string.ascii_letters + string.digits


def generate_code(length=7):
    return "".join(random.choices(ALPHABET, k=length))
