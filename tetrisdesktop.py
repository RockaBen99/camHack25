import mouse, time, os, numpy as np, random, shutil, pyautogui, keyboard
SOURCE = [1,2,3,4,5,6,7]
grid = np.zeros((14,10))
DELAY = 1.4
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
random.shuffle(SOURCE)
outer_source = SOURCE
def clear_all():
    drag((24,16), (0,0))
    time.sleep(0.1)
    pyautogui.press("del")

def create_colour_line(colour, shape):
    for i in range(1, 5):
        shutil.copyfile(f"Colours\\{colour}.png", os.path.join(desktop, f"{shape}{i}.png"))

def drag(start, end):
    (sx, sy) = start
    (ex, ey) = end
    mouse.drag(sx*75+37, sy*82+45, ex*75+37, ey*82+45, absolute=True, duration=0.05)

def generate_choose_piece(shape):
    if shape == 1:
        create_colour_line("Blue", "I")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (2, 0))
        drag((0, 3), (3, 0))
    elif shape == 2:
        create_colour_line("Green", "J")
        time.sleep(DELAY)
        drag((0, 2), (1, 1))
        drag((0, 3), (2, 1))
    elif shape == 3:
        create_colour_line("Red", "L")
        time.sleep(DELAY)
        drag((0, 2), (1, 0))
        drag((0, 3), (2, 0))
    elif shape == 4:
        create_colour_line("Purple", "O")
        time.sleep(DELAY)
        drag((0, 2), (1, 0))
        drag((0, 3), (1, 1))
    elif shape == 5:
        create_colour_line("Yellow", "S")
        time.sleep(DELAY)
        drag((0, 0), (2, 0))
        drag((0, 2), (1, 0))
        drag((0, 3), (1, 1))
    elif shape == 6:
        create_colour_line("Orange", "Z")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (1, 1))
        drag((0, 3), (2, 1))
    elif shape == 7:
        create_colour_line("Cyan", "T")
        time.sleep(DELAY)
        drag((0, 1), (1, 0))
        drag((0, 2), (2, 0))
        drag((0, 3), (1, 1))
    time.sleep(0.15)
    drag((4, 1), (0, 0))

def grid_set(grid, piece):
    if piece == 1:
        grid[0][3:7] = 1
    elif piece == 2:
        grid[0][3] = 1
        grid[1][3:6] = 1
    elif piece == 3:
        grid[1][3] = 1
        grid[0][3:6] = 1
    elif piece == 4:
        grid[0][3:5] = 1
        grid[1][3:5] = 1
    elif piece == 5:
        grid[0][4:6] = 1
        grid[1][3:5] = 1
    elif piece == 6:
        grid[0][3:5] = 1
        grid[1][4:6] = 1
    elif piece == 7:
        grid[0][3:6] = 1
        grid[1][4] = 1
    return grid

def initialise(start_source):
    for j in range(2):
        for i in range(1,15):
            shutil.copyfile("Colours\\Wall.png", os.path.join(desktop, f"Wall{14*j+i}.png"))
        time.sleep(2*DELAY)
        drag((2, 15), (0, 0))
        drag((0, 0), (6 + 11 * j, 0))
    for i in range(1, 11):
        shutil.copyfile("Colours\\Wall.png", os.path.join(desktop, f"Wall{28+i}.png"))
    time.sleep(2*DELAY)
    for i in range(0, 10):
        drag((0, i), (i+7,14))
    for i in range(4):
        generate_choose_piece(start_source[i])
        time.sleep(0.15)
        if start_source[i] == 5:
            drag((1, 0), (21, 3*(i+1)))
        else:
            drag((0, 0), (20, 3*(i+1)))
    display_calculate_next(start_source)

def display_calculate_next(source, grid=grid):
    if len(source) <= 4:
        random.shuffle(SOURCE)
        source += SOURCE
    drag((23,5), (20, 3))
    if source[0] == 5:
        drag((21,3), (10,0))
    else:
        drag((20,3), (10,0))
    drag((23, 14), (20, 6))
    if source[0] == 5:
        drag((21,6), (21,3))
    else:
        drag((20,6), (20,3))
    grid = grid_set(grid, source[0])
    print(source[0])
    print(grid)
    del source[0]
    generate_choose_piece(source[3])
    time.sleep(0.15)
    if source[3] == 5:
        drag((1,0), (21, 12))
    else:
        drag((0,0), (20, 12))
    return grid, source

def run_game():
    while True:
        if keyboard.is_pressed("s"):
            break
        if keyboard.is_pressed("a"):
            continue
    # insert a FULL LINE check
    # pass control to next with source


#clear_all()

initialise(outer_source)
"""for i in range(1, 8):
    print(i)
    print(grid_set(np.zeros((14,10)), i))"""
