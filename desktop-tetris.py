'''
1. made for windows
2. before running, check desktop->view->show desktop icons
3. uncheck desktop->view->align icons on the grid
'''

import win32gui, time, random, keyboard, tkinter as tk

# -------------------- GRID SETTINGS --------------------
GRID_WIDTH, GRID_HEIGHT = 8, 12
ICON_WIDTH, ICON_HEIGHT = 90, 90
EMPTY = -1
HIDDEN_POS = (-1000, -1000)

# -------------------- SPEED SETTINGS --------------------
INITIAL_FPS = 1        
SPEEDUP_RATE = 0.9     # multiplier
LINES_PER_LEVEL = 1    # lines to clear to increase speed

current_fps = INITIAL_FPS
lines_cleared_total = 0

# -------------------- SCORING --------------------
score = 0
line_score = {1:100, 2:300, 3:500, 4:800}  # Tetris scoring

# -------------------- ICON POOL --------------------
ICON_POOL = []       # stack of icons not currently on the grid

# -------------------- WIN32 --------------------
LVM_SETITEMPOSITION = 0x1000 + 15

# -------------------- TETRIS SHAPES --------------------
SHAPES = {
    1: [  # I
        [(0,-1),(0,0),(0,1),(0,2)],   # vertical
        [(-1,0),(0,0),(1,0),(2,0)]    # horizontal
    ],
    
    2: [  # J
        [(-1,-1),(-1,0),(0,0),(1,0)],   # 0°
        [(0,-1),(0,0),(0,1),(-1,1)],    # 90°
        [(-1,0),(0,0),(1,0),(1,1)],     # 180°
        [(0,-1),(0,0),(0,1),(1,-1)]     # 270°
    ],
    
    3: [  # L
        [(-1,0),(0,0),(1,0),(1,-1)],    # 0°
        [(0,-1),(0,0),(0,1),(1,1)],     # 90°
        [(-1,0),(0,0),(1,0),(-1,1)],    # 180°
        [(0,-1),(0,0),(0,1),(-1,-1)]    # 270°
    ],
    
    4: [  # O
        [(0,0),(1,0),(0,1),(1,1)]       # Only one rotation
    ],
    
    5: [  # S
        [(0,0),(1,0),(-1,1),(0,1)],     # 0°
        [(0,-1),(0,0),(1,0),(1,1)]      # 90°
    ],
    
    6: [  # T
        [(-1,0),(0,0),(1,0),(0,1)],     # 0°
        [(0,-1),(0,0),(0,1),(1,0)],     # 90°
        [(-1,0),(0,0),(1,0),(0,-1)],    # 180°
        [(0,-1),(0,0),(0,1),(-1,0)]     # 270°
    ],
    
    7: [  # Z
        [(-1,0),(0,0),(0,1),(1,1)],     # 0°
        [(1,-1),(1,0),(0,0),(0,1)]      # 90°
    ]
}

SHAPE_KEYS = list(SHAPES.keys())

# -------------------- GAME STATE --------------------
GRID = [[EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT)]

# -------------------- WIN32 HELPERS --------------------
# kinda magic
def get_desktop_listview_hwnd():
    progman = win32gui.FindWindow("Progman", None)
    shelldll = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)
    hwnd = win32gui.FindWindowEx(shelldll, 0, "SysListView32", None)
    if hwnd: return hwnd
    desktop_parent = win32gui.GetDesktopWindow()
    workerw = 0
    while True:
        workerw = win32gui.FindWindowEx(desktop_parent, workerw, "WorkerW", None)
        if workerw == 0: break
        shelldll = win32gui.FindWindowEx(workerw, 0, "SHELLDLL_DefView", None)
        if shelldll != 0:
            hwnd = win32gui.FindWindowEx(shelldll, 0, "SysListView32", None)
            return hwnd
    return None

def move_icon(hwnd, idx, x, y):
    lParam = (y << 16) | (x & 0xFFFF)
    win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, idx, lParam)

def hide_icon(hwnd, idx):
    move_icon(hwnd, idx, HIDDEN_POS[0], HIDDEN_POS[1])

def move_icon_grid(hwnd, idx, gx, gy):
    move_icon(hwnd, idx, gx*ICON_WIDTH, gy*ICON_HEIGHT)

# -------------------- DESKTOP SETUP --------------------
def setup_icons(hwnd):
    global ICON_POOL
    LVM_GETITEMCOUNT = 0x1000 + 4
    total = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)
    
    # Check if enough icons exist
    if total < (GRID_WIDTH * GRID_HEIGHT) + 4:
        print(f"Not enough desktop icons! Found {total}, needed {(GRID_WIDTH * GRID_HEIGHT) + 4}")
        return False

    # Pick the game icons from all available icons
    game_icons = random.sample(range(total), (GRID_WIDTH * GRID_HEIGHT) + 4)
    ICON_POOL = game_icons[:]  # Initial pool for pieces

    # Hide all unused icons
    for i in range(total):
        hide_icon(hwnd, i)

    print(f"Game icons: {len(game_icons)}, all others are hidden.")
    return True

def show_game_over():
    root = tk.Tk()
    root.title("Tetris")
    root.geometry("400x100")
    root.resizable(False, False)

    label = tk.Label(root, text="GAME OVER. SCORE = " + str(score), font=("Arial", 14), fg="red")
    label.pack(expand=True)

    button = tk.Button(root, text="Exit", command=root.destroy)
    button.pack(pady=10)

    root.mainloop()

# -------------------- PIECE FUNCS --------------------
def new_piece():
    icons = [ICON_POOL.pop() for _ in range(4)]
    return {
        "type": random.choice(SHAPE_KEYS),
        "rotation": 0,
        "x": GRID_WIDTH//2-1,
        "y": 0,
        "icons": icons
    }

def piece_blocks(p):
    return [(p["x"]+dx, p["y"]+dy) for dx,dy in SHAPES[p["type"]][p["rotation"]]]

def collision(p, dx=0, dy=0):
    for x, y in piece_blocks(p):
        nx, ny = x+dx, y+dy
        if nx<0 or nx>=GRID_WIDTH or ny>=GRID_HEIGHT:
            return True
        if ny>=0 and GRID[ny][nx]!=EMPTY:
            return True
    return False

def draw_piece(hwnd, p):
    for icon, (x, y) in zip(p["icons"], piece_blocks(p)):
        if y>=0:
            move_icon_grid(hwnd, icon, x, y)
        else:
            hide_icon(hwnd, icon)

def draw_next_piece(hwnd, piece):
    preview_x = GRID_WIDTH + 1  # one column right of grid
    preview_y = 2 # two rows from top row

    for icon, (dx, dy) in zip(piece["icons"], SHAPES[piece["type"]][piece["rotation"]]):
        move_icon_grid(hwnd, icon, preview_x + dx, preview_y + dy)

def lock_piece(hwnd, p):
    for (x, y), icon in zip(piece_blocks(p), p["icons"]):
        if y >= 0:
            GRID[y][x] = icon
            move_icon_grid(hwnd, icon, x, y)

def clear_lines(hwnd):
    global ICON_POOL, lines_cleared_total
    full_rows = [y for y in range(GRID_HEIGHT) if all(GRID[y][x] != EMPTY for x in range(GRID_WIDTH))]
    if not full_rows:
        return 0

    # Return icons to pool
    for y in full_rows:
        for x in range(GRID_WIDTH):
            ICON_POOL.append(GRID[y][x])
            hide_icon(hwnd, GRID[y][x])

    # Shift rows down
    new_grid = [[EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
    new_y = GRID_HEIGHT - 1
    for old_y in reversed(range(GRID_HEIGHT)):
        if old_y not in full_rows:
            new_grid[new_y] = GRID[old_y][:]
            new_y -= 1
    for y in range(GRID_HEIGHT):
        GRID[y] = new_grid[y][:]
    
    # Redraw
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if GRID[y][x] != EMPTY:
                move_icon_grid(hwnd, GRID[y][x], x, y)

    # Update total lines cleared
    lines = len(full_rows)
    lines_cleared_total += lines

    # Scoring for cleared rows
    if lines > 0:
        global score
        score += line_score.get(lines, 0)

    return lines


# -------------------- INPUT --------------------
def move_horizontal(hwnd, piece, dx):
    if not collision(piece, dx, 0):
        piece["x"] += dx
        draw_piece(hwnd, piece)

def rotate(hwnd, piece):
    test = piece.copy()
    test["rotation"] = (piece["rotation"] + 1) % len(SHAPES[piece["type"]])
    if not collision(test):
        piece["rotation"] = test["rotation"]
        draw_piece(hwnd, piece)

# ----------------- END SCREEN DISPLAY --------------------
DIGITS = {
    "0": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "1": [(1,0),(1,1),(1,2),(1,3),(1,4)],
    "2": [(0,0),(1,0),(2,0),(2,1),(0,2),(1,2),(2,2),(0,3),(0,4),(1,4),(2,4)],
    "3": [(0,0),(1,0),(2,0),(2,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
    "4": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(2,3),(2,4)],
    "5": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
    "6": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "7": [(0,0),(1,0),(2,0),(2,1),(1,2),(1,3),(1,4)],
    "8": [(0,0),(1,0),(2,0),(0,1),(2,1),(1,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "9": [(0,0),(1,0),(2,0),(0,1),(2,1),(1,2),(2,3),(0,4),(1,4),(2,4)]
}

def hide_all_icons(hwnd):
    LVM_GETITEMCOUNT = 0x1000 + 4
    total = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)
    for i in range(total):
        hide_icon(hwnd, i)


def display_score_icons(hwnd, score):
    s = str(score)

    total_digits = len(s)
    icons_needed = total_digits * 15  # ~15 icons per digit

    score_icons = ICON_POOL[:icons_needed]
    ICON_POOL[:] = ICON_POOL[icons_needed:]

    icon_index = 0
    base_x = 2   # where on desktop grid digits start
    base_y = 2

    for digit in s:
        for (dx, dy) in DIGITS[digit]:
            move_icon_grid(hwnd, score_icons[icon_index], base_x + dx, base_y + dy)
            icon_index += 1
        base_x += 4  # space between digits

# -------------------- MAIN LOOP --------------------
def run():
    global current_fps, lines_cleared_total, score

    hwnd = get_desktop_listview_hwnd()
    if not hwnd:
        print("Desktop icons not found!")
        return
    if not setup_icons(hwnd):
        return

    current_piece = new_piece()
    next_piece = new_piece()
    draw_piece(hwnd, current_piece)
    draw_next_piece(hwnd, next_piece)

    last = time.time()

    while True:
        # Keyboard input
        if keyboard.is_pressed("left"): 
            move_horizontal(hwnd, current_piece, -1)
            time.sleep(0.08)
        if keyboard.is_pressed("right"): 
            move_horizontal(hwnd, current_piece, 1)
            time.sleep(0.08)
        if keyboard.is_pressed("up"): 
            rotate(hwnd, current_piece)
            time.sleep(0.12)
        if keyboard.is_pressed("down"):
            if not collision(current_piece, 0, 1):
                current_piece["y"] += 1
                draw_piece(hwnd, current_piece)
            time.sleep(0.06)

        # Gravity
        if time.time() - last >= current_fps:
            if not collision(current_piece, 0, 1):
                current_piece["y"] += 1
                draw_piece(hwnd, current_piece)
                
                # Soft drop scoring
                score += 1
            else:
                # Piece locks
                lock_piece(hwnd, current_piece)
                lines_cleared = clear_lines(hwnd)

                # Increase speed based on lines cleared
                if lines_cleared_total // LINES_PER_LEVEL > (lines_cleared_total - lines_cleared) // LINES_PER_LEVEL:
                    current_fps = max(0.1, current_fps * SPEEDUP_RATE)  # don't go below 0.1s per step

                # Move next_piece to current_piece
                current_piece = next_piece
                draw_piece(hwnd, current_piece)

                # Spawn a new next_piece
                next_piece = new_piece()
                draw_next_piece(hwnd, next_piece)

                # Check game over immediately
                if collision(current_piece):
                    # Hide everything first
                    hide_all_icons(hwnd)
                    time.sleep(0.3)

                    # Display score as icons
                    display_score_icons(hwnd, score)

                    # Optional score window — keep or remove
                    # show_game_over()
                    # DO NOT SHOW IT NOW - SINCE WE HAVE ICON SCORE.
                    print(score)
                    return

                
            last = time.time()

        time.sleep(0.01)

# -------------------- RUN --------------------
if __name__=="__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nStopped. Refresh desktop to restore icons.")