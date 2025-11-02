import mouse, time, os, numpy as np, random, shutil, pyautogui, keyboard
#ADD SOMETHING TO CALCULATE THE HEIGHTS AND WIDTHS OF ICONS
SOURCE = [1,2,3,4,5,6,7]
grid = np.zeros((13,10))
DELAY = 1.4
XPIXELS = 114
YPIXELS = 123
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
random.shuffle(SOURCE)
outer_source = SOURCE
PIECES = [np.array([1,1,1,1]), np.array([[1,0,0],[1,1,1],[0,0,0]]),
          np.array([[1,1,1], [1,0,0]]), np.array([[1,1],[1,1]]), np.array([[0,1,1], [1,1,0]]),
          np.array([[1,1,0], [0,1,1]]), np.array([[1,1,1], [0,1,0]])]

def to_pixels(x, y):
    return x*XPIXELS+50, y*YPIXELS+30

def clear_all():
    drag((24,16), (0,0))
    time.sleep(0.1)
    pyautogui.press("del")

def create_colour_line(colour, shape):
    for i in range(1, 5):
        shutil.copyfile(f"Colours\\{colour}.png", os.path.join(desktop, f"{shape}{i}.png"))

def drag(start, end):
    s_gridx, s_gridy = start
    e_gridx, e_gridy = end
    (sx, sy) = to_pixels(s_gridx, s_gridy)
    (ex, ey) = to_pixels(e_gridx, e_gridy)
    mouse.drag(sx, sy, ex, ey, absolute=True, duration=0.05)

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
    # add a check -> if any piece is ALREADY 1 then the game is over
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
        time.sleep(3*DELAY)
        drag((2, 13), (0, 0))
        drag((0, 0), (6 + 11 * j, 0))
    for i in range(1, 11):
        shutil.copyfile("Colours\\Wall.png", os.path.join(desktop, f"Wall{28+i}.png"))
    time.sleep(2*DELAY)
    for i in range(0, 10):
        drag((0, i), (i+7,13))
    for i in range(4):
        generate_choose_piece(start_source[i])
        time.sleep(0.15)
        if start_source[i] == 5:
            drag((1, 0), (21, 3*(i+1)))
        else:
            drag((0, 0), (20, 3*(i+1)))
    piece, grid, next_pieces = display_calculate_next(start_source)
    return piece, grid, next_pieces

def select_piece(piece, corner, orientation):
    (px, py) = corner
    pixelx, pixely = to_pixels(px, py)
    shape = PIECES[piece - 1]
    for i in range(orientation):
        shape = np.rot90(shape)
    keyboard.press("ctrl")
    if len(shape) == 4:
        for i in range(len(shape)):
            if shape[i] == 1:
                pixelx, pixely = to_pixels(px + i + 7, py)
                mouse.move(pixelx, pixely, absolute=True, duration=0)
                time.sleep(0.1)
                mouse.click()
                time.sleep(0.1)
    else:
        rows, columns = shape.shape
        for j in range(rows):
            for i in range(columns):
                if shape[j][i] == 1:
                    pixelx, pixely = to_pixels(px + i + 7, py + j)
                    mouse.move(pixelx, pixely, absolute=True, duration=0)
                    time.sleep(0.1)
                    mouse.click()
                    time.sleep(0.1)
    keyboard.release("ctrl")

def translate_piece(piece, corner, translation, orientation, grid):
    (x,y) = translation
    (px, py) = corner
    shape = PIECES[piece - 1]
    for i in range(orientation):
        shape = np.rot90(shape)
    print(np.where(shape == 1)[0][0])
    grabx, graby = np.where(shape == 1)[0][0], np.where(shape == 1)[0][1]
    drag((grabx + 7+px, graby+py), (grabx + x + 7+px, graby + y+py))
    return grid, (px + x, py + y)

def display_calculate_next(source, grid=grid):
    if len(source) <= 4:
        random.shuffle(SOURCE)
        source += SOURCE
    drag((23,5), (19, 3))
    time.sleep(0.15)
    if source[0] == 5:
        drag((21,3), (10,0))
    else:
        drag((20,3), (10,0))
    drag((23, 13), (19, 6))
    if source[1] == 5:
        drag((21,6), (21,3))
    else:
        drag((20,6), (20,3))
    grid = grid_set(grid, source[0])
    curr_piece = source[0]
    del source[0]
    generate_choose_piece(source[3])
    time.sleep(0.15)
    if source[3] == 5:
        drag((1,0), (21, 12))
    else:
        drag((0,0), (20, 12))
    return curr_piece, grid, source

def run_game(piece, grid, next_pieces):
    corner = (3, 0)
    orientation = 0
    select_piece(piece, corner, orientation)
    dropflag = False
    while True:
        (x, y) = corner
        t_end = time.time() + 2
        while time.time() < t_end:
            (x, y) = corner
            if keyboard.is_pressed("s"):
                dropflag = True
                break
            if keyboard.is_pressed("a"):
                grid, corner = translate_piece(piece, (x, y), (-1, 0), orientation, grid)
            if keyboard.is_pressed("d"):
                grid, corner = translate_piece(piece, (x, y), (1, 0), orientation, grid)
        grid, corner = translate_piece(piece, (x, y), (0, 1), orientation, grid)
        """if dropflag:
            break
        elif insert a check to see if a down translation is possible:
            grid, corner = translate_piece(piece, (x, y), (0, 1), orientation, grid)
            if hit floor:
                #insert a line check
                break
        else:
            break"""
    # pass control to next with source


#clear_all()

piece, grid, next_pieces = initialise(outer_source)
run_game(piece, grid, next_pieces)

# the only commands to run the game
#mouse.move(2*75+37, 1091, absolute=True, duration=0)
"""for x in range(0, 24):
    for y in range(0, 14):
        mouse.move(x*114+50, y*123+30, absolute=True, duration=0)
        time.sleep(1)"""
"""for i in range(1, 8):
    print(i)
    print(grid_set(np.zeros((14,10)), i))"""
