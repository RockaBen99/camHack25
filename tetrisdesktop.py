import mouse, time, os, numpy as np, random
SOURCE = [1,2,3,4,5,6,7]
grid = np.zeros((14,10))

def display_calculate_next():
    if len(SOURCE) < 4:

    random.shuffle(SOURCE)
    return SOURCE[0]
    # this function should be called every time a new piece is about to be selected (after tapping down or collide with floor)




