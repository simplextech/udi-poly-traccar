
def cardinal_direction(course):
    # Returns the Cardinal Direction Name
    if 0 <= course <= 11.24:
        return 1
    elif 11.25 <= course <= 33.74:
        return 2
    elif 33.75 <= course <= 56.24:
        return 3
    elif 56.25 <= course <= 78.74:
        return 4
    elif 78.75 <= course <= 101.24:
        return 5
    elif 101.25 <= course <= 123.74:
        return 6
    elif 123.75 <= course <= 146.24:
        return 7
    elif 146.25 <= course <= 168.74:
        return 8
    elif 168.75 <= course <= 191.24:
        return 9
    elif 191.25 <= course <= 213.74:
        return 10
    elif 213.75 <= course <= 236.24:
        return 11
    elif 236.25 <= course <= 258.74:
        return 12
    elif 258.75 <= course <= 281.24:
        return 13
    elif 281.25 <= course <= 303.74:
        return 14
    elif 303.75 <= course <= 326.24:
        return 15
    elif 326.25 <= course <= 348.74:
        return 16
    elif 348.75 <= course <= 360:
        return 1
    else:
        return 0
