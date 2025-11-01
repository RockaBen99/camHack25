import mouse, time, os, numpy as np, random, shutil
SOURCE = [1,2,3,4,5,6,7]
grid = np.zeros((14,10))
DELAY = 1.3
random.shuffle(SOURCE)
outer_source = SOURCE
def create_colour_line(colour, shape):
    for i in range(1, 5):
        shutil.copyfile(f"Colours\\{colour}.png", f"C:\\Users\\adyan\\Desktop\\{shape}{i}.png")

def drag(start, end):
    (sx, sy) = start
    (ex, ey) = end
    mouse.drag(sx*75+37, sy*75+37, ex*75+37, ey*75+37, absolute=True, duration=0.05)

def display_calculate_next(source):
    if len(source) == 4:
        random.shuffle(SOURCE)
        source += SOURCE
    if source[3] == 1:
        create_colour_line("Blue", "I")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (2, 0))
        drag((0, 3), (3, 0))
    elif source[3] == 2:
        create_colour_line("Green", "J")
        time.sleep(DELAY)
        drag((0, 2), (1, 1))
        drag((0, 3), (2, 1))
    elif source[3] == 3:
        create_colour_line("Red", "L")
        time.sleep(DELAY)
        drag((0, 0), (2, 0))
        drag((0, 2), (1, 1))
        drag((0, 3), (2, 1))
    elif source[3] == 4:
        create_colour_line("Purple", "O")
        time.sleep(DELAY)
        drag((0, 2), (1, 0))
        drag((0, 3), (1, 1))
    elif source[3] == 5:
        create_colour_line("Yellow", "S")
        time.sleep(DELAY)
        drag((0, 0), (2, 0))
        drag((0, 2), (1, 0))
        drag((0, 3), (1, 1))
    elif source[3] == 6:
        create_colour_line("Orange", "Z")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (1, 1))
        drag((0, 3), (2, 1))
    elif source[3] == 7:
        create_colour_line("Cyan", "T")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (2, 0))
        drag((0, 3), (1, 1))
    time.sleep(0.1)
    drag((4,1), (0, 0))
    time.sleep(0.1)
    drag((0,0), (20, 12))

    return source
    # this function should be called every time a new piece is about to be selected (after tapping down or collide with floor)

display_calculate_next([4,7,3,7,5])



