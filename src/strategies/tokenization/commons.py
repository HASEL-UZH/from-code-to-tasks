import re

pattern = r"\d+"
regex = re.compile(pattern)


def remove_numbers(text):
    cleaned_text = regex.sub("", text)
    return cleaned_text


def is_number(s):
    try:
        float(s)  # for float
    except ValueError:
        return False
    return True
