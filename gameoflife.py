import numpy as np
import matplotlib.pyplot as plt

class GameOfLife:
    def __init__(self, grid):
        self.grid = grid
    
    def count(self, coord):
        # count the number of neighbors that are alive
        x, y = coord
        total = 0
        up = x==0
        down = x==self.grid.shape[0]-1
        left = y==0
        right = y==self.grid.shape[1]-1
        if not up and not down and not left and not right:
            total += self.grid[x-1][y]  # up
            total += self.grid[x][y-1]  # left
            total += self.grid[x][y+1]  # right
            total += self.grid[x+1][y]  # down
            total += self.grid[x-1][y-1]  # up-left
            total += self.grid[x-1][y+1]  # up-right
            total += self.grid[x+1][y-1]  # down-left
            total += self.grid[x+1][y+1]  # down-right
        elif up and left:
            total += self.grid[x][y+1]  # right
            total += self.grid[x+1][y]  # down
            total += self.grid[x+1][y+1]  # down-right
        elif up and right:
            total += self.grid[x][y-1]  # left
            total += self.grid[x+1][y]  # down
            total += self.grid[x+1][y-1]  # down-left
        elif down and left:
            total += self.grid[x-1][y]  # up
            total += self.grid[x][y+1]  # right
            total += self.grid[x-1][y+1]  # up-right
        elif down and right:
            total += self.grid[x-1][y]  # up
            total += self.grid[x][y-1]  # left
            total += self.grid[x-1][y-1]  # up-left
        elif up and not left and not right:
            total += self.grid[x][y-1]  # left
            total += self.grid[x][y+1]  # right
            total += self.grid[x+1][y]  # down
            total += self.grid[x+1][y-1]  # down-left
            total += self.grid[x+1][y+1]  # down-right
        elif down and not left and not right:
            total += self.grid[x][y-1]  # left
            total += self.grid[x][y+1]  # right
            total += self.grid[x-1][y]  # up
            total += self.grid[x-1][y-1]  # up-left
            total += self.grid[x-1][y+1]  # up-right
        elif left and not up and not down:
            total += self.grid[x-1][y]  # up
            total += self.grid[x+1][y]  # down
            total += self.grid[x][y+1]  # right
            total += self.grid[x-1][y+1]  # up-right
            total += self.grid[x+1][y+1]  # down-right
        elif right and not up and not down:
            total += self.grid[x-1][y]  # up
            total += self.grid[x+1][y]  # down
            total += self.grid[x][y-1]  # left
            total += self.grid[x-1][y-1]  # up-left
            total += self.grid[x+1][y-1]  # down-left
        return total
    
    def update(self):
        new_grid = self.grid.copy()
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                neighbors = self.count([i, j])
                if self.grid[i][j] == 1:
                    # if original alive
                    if neighbors < 2 or neighbors > 3:
                        # underpopulation or overpopulation
                        new_grid[i][j] = 0
                    else:
                        # lives on to the next generation
                        new_grid[i][j] = 1
                else:
                    # if original dead
                    if neighbors == 3:
                        # reproduction
                        new_grid[i][j] = 1
                    else:
                        new_grid[i][j] = 0
        self.grid = new_grid

    def display(self):
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid[i][j] == 1:
                    print('#', end=' ')
                else:
                    print('.', end=' ')
            print("")
    

grid = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
test = GameOfLife(grid)
test.display()
print("Next Generattion:")
test.update()
test.display()
