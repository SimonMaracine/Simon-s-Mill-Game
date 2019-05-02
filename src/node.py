from math import sqrt
import pygame


class Node:
    def __init__(self, x, y, search: tuple):
        self.x = x
        self.y = y
        self.search = search
        self.radius = 29
        self.highlight = False
        self.highlight_color = (16, 200, 15)
        self.color = (0, 0, 0)
        self.piece = None

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), 11)
        if self.highlight:
            pygame.draw.ellipse(surface, self.highlight_color,
                                (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2), 3)

    def update(self, mouse_x, mouse_y):
        distance = sqrt(((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2))
        if distance <= self.radius:
            self.highlight = True
        else:
            self.highlight = False

    def add_piece(self, piece):
        self.piece = piece

    def take_piece(self):
        self.piece = None

    def change_color(self, color: tuple):
        self.color = color

    def search_neighbors(self, nodes: tuple, div: int) -> tuple:
        search_north, search_south, search_east, search_west = self.search
        neighbor_nodes = []
        x = self.x
        y = self.y

        for i in range(1, 4):
            for node in nodes:
                if search_east:
                    if (x + div * i, y) == (node.x, node.y):
                        print("Found node on the E. Distance = {} DIVs".format(i))
                        neighbor_nodes.append(node)
                        search_east = 0
                if search_south:
                    if (x, y + div * i) == (node.x, node.y):
                        print("Found node on the S. Distance = {} DIVs".format(i))
                        neighbor_nodes.append(node)
                        search_south = 0

        x = self.x
        y = self.y

        for i in range(1, 4):
            for node in nodes:
                if search_west:
                    if (x - div * i, y) == (node.x, node.y):
                        print("Found node on the W. Distance = {} DIVs".format(i))
                        neighbor_nodes.append(node)
                        search_west = 0
                if search_north:
                    if (x, y - div * i) == (node.x, node.y):
                        print("Found node on the N. Distance = {} DIVs".format(i))
                        neighbor_nodes.append(node)
                        search_north = 0

        return tuple(neighbor_nodes)
