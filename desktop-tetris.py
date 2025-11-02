import win32gui
import time
import random
import keyboard

# -------------------- GRID SETTINGS --------------------
GRID_WIDTH, GRID_HEIGHT = 8, 12      # Grid size
ICON_WIDTH, ICON_HEIGHT = 90, 90
FPS = 1.0
EMPTY = -1
HIDDEN_POS = (-1000, -1000)

# -------------------- ICON POOL --------------------
ICON_POOL = []       # Icons not currently on the grid
FALLING_ICONS = []   # Icons used by the current falling piece
SETTLED_ICONS = []   # Icons currently locked on the grid

# -------------------- WIN32 --------------------
LVM_SETITEMPOSITION = 0x1000 + 15

# -------------------- TETRIS SHAPES --------------------
SHAPES = {
    1: [[(0,-1),(0,0),(0,1),(0,2)], [(-1,0),(0,0),(1,0),(2,0)]],      # I
    2: [[(-1,-1),(-1,0),(0,0),(1,0)], [(-1,1),(0,1),(0,0),(0,-1)],
        [(1,1),(1,0),(0,0),(-1,0)], [(1,-1),(0,-1),(0,0),(0,1)]],      # J
    3: [[(-1,0),(0,0),(1,0),(1,-1)], [(0,-1),(0,0),(0,1),(1,1)],
        [(-1,1),(-1,0),(0,0),(1,0)], [(-1,-1),(0,-1),(0,0),(0,1)]],    # L
    4: [[(0,0),(1,0),(0,1),(1,1)]],                                     # O
    5: [[(0,0),(1,0),(-1,1),(0,1)], [(-1,0),(-1,1),(0,-1),(0,0)]],     # S
    6: [[(-1,0),(0,0),(1,0),(0,1)], [(0,-1),(0,0),(1,0),(0,1)],
        [(-1,0),(0,0),(1,0),(0,-1)], [(-1,0),(0,0),(0,-1),(0,1)]],     # T
    7: [[(-1,0),(0,0),(0,1),(1,1)], [(0,0),(-1,1),(0,-1),(-1,0)]]      # Z
}
SHAPE_KEYS = list(SHAPES.keys())

# -------------------- GAME STATE --------------------
GRID = [[EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT)]

# -------------------- WIN32 HELPERS --------------------
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
        print(f"Not enough desktop icons! Found {total}")
        return False

    # Pick the game icons from all available icons
    game_icons = random.sample(range(total), (GRID_WIDTH * GRID_HEIGHT) + 4)
    ICON_POOL = game_icons[:]  # Initial pool for pieces

    # Hide all unused icons
    for i in range(total):
        if i in game_icons:
            hide_icon(hwnd, i)  # They will be used dynamically
        else:
            hide_icon(hwnd, i)  # Unused icons are hidden completely

    print(f"Game icons: {len(game_icons)}, all others are hidden.")
    return True


# -------------------- PIECE HELPERS --------------------
def new_piece():
    global ICON_POOL
    if len(ICON_POOL) < 4:
        # Refill pool from cleared icons if needed
        random.shuffle(ICON_POOL)
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

def lock_piece(hwnd, p):
    for (x, y), icon in zip(piece_blocks(p), p["icons"]):
        if y >= 0:
            GRID[y][x] = icon
            move_icon_grid(hwnd, icon, x, y)

def clear_lines(hwnd):
    global ICON_POOL
    # 1. Find all full rows
    full_rows = [y for y in range(GRID_HEIGHT) if all(GRID[y][x] != EMPTY for x in range(GRID_WIDTH))]
    if not full_rows:
        return

    # 2. Collect icons to return to the pool
    for y in full_rows:
        for x in range(GRID_WIDTH):
            ICON_POOL.append(GRID[y][x])
            hide_icon(hwnd, GRID[y][x])

    # 3. Shift all non-cleared rows down
    new_grid = [ [EMPTY]*GRID_WIDTH for _ in range(GRID_HEIGHT) ]
    new_y = GRID_HEIGHT - 1

    # Start from the bottom row, copy non-full rows down
    for old_y in reversed(range(GRID_HEIGHT)):
        if old_y not in full_rows:
            new_grid[new_y] = GRID[old_y][:]
            new_y -= 1

    # 4. Update the global grid
    for y in range(GRID_HEIGHT):
        GRID[y] = new_grid[y][:]

    # 5. Redraw all settled icons
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if GRID[y][x] != EMPTY:
                move_icon_grid(hwnd, GRID[y][x], x, y)


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

# -------------------- MAIN LOOP --------------------
def run():
    hwnd = get_desktop_listview_hwnd()
    if not hwnd:
        print("Desktop icons not found!")
        return
    if not setup_icons(hwnd):
        return

    piece = new_piece()
    draw_piece(hwnd, piece)
    last = time.time()

    while True:
        # Keyboard input
        if keyboard.is_pressed("left"): move_horizontal(hwnd, piece, -1); time.sleep(0.08)
        if keyboard.is_pressed("right"): move_horizontal(hwnd, piece, 1); time.sleep(0.08)
        if keyboard.is_pressed("up"): rotate(hwnd, piece); time.sleep(0.12)
        if keyboard.is_pressed("down"):
            if not collision(piece, 0, 1):
                piece["y"] += 1
                draw_piece(hwnd, piece)
            time.sleep(0.06)

        # Gravity
        if time.time()-last >= FPS:
            if not collision(piece, 0, 1):
                piece["y"] += 1
                draw_piece(hwnd, piece)
            else:
                lock_piece(hwnd, piece)
                clear_lines(hwnd)
                piece = new_piece()
                if collision(piece):
                    print("GAME OVER")
                    return
                draw_piece(hwnd, piece)
            last = time.time()

        time.sleep(0.01)

# -------------------- RUN --------------------
if __name__=="__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nStopped. Refresh desktop to restore icons.")
