import pygame
import heapq
from random import choice
from math import sqrt

RES = WIDTH, HEIGHT = 1202, 902
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.parent = None
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')

    def draw_current_cell(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('saddlebrown'), (x + 2, y + 2, TILE - 2, TILE - 2))

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color('black'), (x, y, TILE, TILE))

        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y), (x + TILE, y), 3)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y), (x + TILE, y + TILE), 3)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y + TILE), (x, y + TILE), 3)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y + TILE), (x, y), 3)

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

    def get_neighbors(self):
        neighbors = []
        if not self.walls['top'] and self.y > 0:
            neighbors.append(self.check_cell(self.x, self.y - 1))
        if not self.walls['right'] and self.x < cols - 1:
            neighbors.append(self.check_cell(self.x + 1, self.y))
        if not self.walls['bottom'] and self.y < rows - 1:
            neighbors.append(self.check_cell(self.x, self.y + 1))
        if not self.walls['left'] and self.x > 0:
            neighbors.append(self.check_cell(self.x - 1, self.y))
        return [n for n in neighbors if n]

def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def reconstruct_path(current, start, color):
    path = []
    while current != start:
        path.append(current)
        current = current.parent
    path.append(start)
    path.reverse()
    
    for cell in path:
        x, y = cell.x * TILE, cell.y * TILE
        pygame.draw.rect(sc, color, (x + 2, y + 2, TILE - 2, TILE - 2))
    
    return path

def dijkstra(start, end):
    open_set = []
    heapq.heappush(open_set, (0, start))
    start.g = 0
    
    while open_set:
        current_cost, current = heapq.heappop(open_set)
        
        if current == end:
            return reconstruct_path(current, start, pygame.Color('green'))
        
        for neighbor in current.get_neighbors():
            tentative_g = current.g + 1
            
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                heapq.heappush(open_set, (neighbor.g, neighbor))
    
    return []

def a_star(start, end):
    open_set = []
    heapq.heappush(open_set, (0, start))
    start.g = 0
    start.h = heuristic(start, end)
    start.f = start.g + start.h
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        
        if current == end:
            return reconstruct_path(current, start, pygame.Color('blue'))
        
        for neighbor in current.get_neighbors():
            tentative_g = current.g + 1
            
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, end)
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_set, (neighbor.f, neighbor))
    
    return []

grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []
colors, color = [], 40

maze_generated = False
target_cell = None
dijkstra_path = []
a_star_path = []

running = True
while running:
    sc.fill(pygame.Color('darkslategray'))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and maze_generated:
            x, y = pygame.mouse.get_pos()
            col, row = x // TILE, y // TILE
            if 0 <= col < cols and 0 <= row < rows:
                target_cell = grid_cells[col + row * cols]
                for cell in grid_cells:
                    cell.g = float('inf')
                    cell.h = 0
                    cell.f = float('inf')
                    cell.parent = None
                dijkstra_path = dijkstra(grid_cells[0], target_cell)
                a_star_path = a_star(grid_cells[0], target_cell)
    
    if not maze_generated:
        [cell.draw() for cell in grid_cells]
        current_cell.visited = True
        current_cell.draw_current_cell()
        [pygame.draw.rect(sc, colors[i], (cell.x * TILE + 2, cell.y * TILE + 2,
                                         TILE - 4, TILE - 4)) for i, cell in enumerate(stack)]

        next_cell = current_cell.check_neighbors()
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            colors.append((min(color, 255), 10, 100))
            color += 1
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()
        else:
            maze_generated = True
    else:
        [cell.draw() for cell in grid_cells]
        
        if dijkstra_path:
            for cell in dijkstra_path:
                x, y = cell.x * TILE, cell.y * TILE
                pygame.draw.rect(sc, pygame.Color('green'), (x + 2, y + 2, TILE - 2, TILE - 2))
        
        if a_star_path:
            for cell in a_star_path:
                x, y = cell.x * TILE, cell.y * TILE
                pygame.draw.rect(sc, pygame.Color('blue'), (x + 2, y + 2, TILE - 2, TILE - 2))
        
        if target_cell:
            x, y = target_cell.x * TILE, target_cell.y * TILE
            pygame.draw.rect(sc, pygame.Color('red'), (x + 2, y + 2, TILE - 2, TILE - 2))
        
        x, y = (cols-1) * TILE, (rows-1) * TILE
        pygame.draw.rect(sc, pygame.Color('yellow'), (x + 2, y + 2, TILE - 2, TILE - 2))
        
        info_text = [
            "Лабиринт сгенерирован!",
            "Кликните в любую клетку, чтобы найти путь из левого нижнего угла",
            "Зеленый: алгоритм Дейкстры",
            "Синий: алгоритм A*",
            "Красный: целевая клетка",
            "Желтый: начальная клетка (левый нижний угол)"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, pygame.Color('white'))
            sc.blit(text_surface, (10, 10 + i * 25))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
