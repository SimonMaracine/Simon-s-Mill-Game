from typing import Optional

import pygame

from src.game.piece import Piece
from src.game.node import Node
from src.constants import *
from src.log import get_logger

logger = get_logger(__name__)
logger.setLevel(10)

window_width = 800
window_height = 600


class Board:
    """Game board object."""

    def __init__(self):
        self.width = window_height - 160
        self.x = (window_width - self.width) // 2  # x and y are board's origin
        self.y = (window_height - self.width) // 2
        self.DIV = self.width // 6

        self.line_thickness = 8
        self.board_offset = 35

        self.nodes = (
            Node(self.x, self.y, (0, 1, 1, 0), 0),
            Node(self.x + self.DIV * 3, self.y, (0, 1, 1, 1), 1),
            Node(self.x + self.DIV * 6, self.y, (0, 1, 0, 1), 2),  # line
            Node(self.x + self.DIV, self.y + self.DIV, (0, 1, 1, 0), 3),
            Node(self.x + self.DIV * 3, self.y + self.DIV, (1, 1, 1, 1), 4),
            Node(self.x + self.DIV * 5, self.y + self.DIV, (0, 1, 0, 1), 5),  # line
            Node(self.x + self.DIV * 2, self.y + self.DIV * 2, (0, 1, 1, 0), 6),
            Node(self.x + self.DIV * 3, self.y + self.DIV * 2, (1, 0, 1, 1), 7),
            Node(self.x + self.DIV * 4, self.y + self.DIV * 2, (0, 1, 0, 1), 8),  # line
            Node(self.x, self.y + self.DIV * 3, (1, 1, 1, 0), 9),
            Node(self.x + self.DIV, self.y + self.DIV * 3, (1, 1, 1, 1), 10),
            Node(self.x + self.DIV * 2, self.y + self.DIV * 3, (1, 1, 0, 1), 11),  # line
            Node(self.x + self.DIV * 4, self.y + self.DIV * 3, (1, 1, 1, 0), 12),
            Node(self.x + self.DIV * 5, self.y + self.DIV * 3, (1, 1, 1, 1), 13),
            Node(self.x + self.DIV * 6, self.y + self.DIV * 3, (1, 1, 0, 1), 14),  # line
            Node(self.x + self.DIV * 2, self.y + self.DIV * 4, (1, 0, 1, 0), 15),
            Node(self.x + self.DIV * 3, self.y + self.DIV * 4, (0, 1, 1, 1), 16),
            Node(self.x + self.DIV * 4, self.y + self.DIV * 4, (1, 0, 0, 1), 17),  # line
            Node(self.x + self.DIV, self.y + self.DIV * 5, (1, 0, 1, 0), 18),
            Node(self.x + self.DIV * 3, self.y + self.DIV * 5, (1, 1, 1, 1), 19),
            Node(self.x + self.DIV * 5, self.y + self.DIV * 5, (1, 0, 0, 1), 20),  # line
            Node(self.x, self.y + self.DIV * 6, (1, 0, 1, 0), 21),
            Node(self.x + self.DIV * 3, self.y + self.DIV * 6, (1, 0, 1, 1), 22),
            Node(self.x + self.DIV * 6, self.y + self.DIV * 6, (1, 0, 0, 1), 23)  # line
        )
        for node in self.nodes:  # Correct the position of each node.
            node.x += 1
            node.y += 1

        self.phase = PHASE1
        self.turn = PLAYER1

        self.white_pieces = 9
        self.black_pieces = 9

        self.picked_up_piece: Optional[Piece] = None  # The piece that is currenly held
        self.node_taken_piece: Optional[Node] = None  # The node whose piece is currently picked up

        self.windmills = (
            (self.nodes[0], self.nodes[1], self.nodes[2]),
            (self.nodes[0], self.nodes[9], self.nodes[21]),
            (self.nodes[21], self.nodes[22], self.nodes[23]),
            (self.nodes[23], self.nodes[14], self.nodes[2]),
            (self.nodes[3], self.nodes[4], self.nodes[5]),
            (self.nodes[3], self.nodes[10], self.nodes[18]),
            (self.nodes[18], self.nodes[19], self.nodes[20]),
            (self.nodes[20], self.nodes[13], self.nodes[5]),
            (self.nodes[6], self.nodes[7], self.nodes[8]),
            (self.nodes[6], self.nodes[11], self.nodes[15]),
            (self.nodes[15], self.nodes[16], self.nodes[17]),
            (self.nodes[17], self.nodes[12], self.nodes[8]),
            (self.nodes[1], self.nodes[4], self.nodes[7]),
            (self.nodes[9], self.nodes[10], self.nodes[11]),
            (self.nodes[22], self.nodes[19], self.nodes[16]),
            (self.nodes[12], self.nodes[13], self.nodes[14])
        )

        self.must_remove_piece = False
        self.can_jump = {PLAYER1: False, PLAYER2: False}
        self.node_pressed = False  # if a node is clicked
        # self.turns_without_windmills = 0

        self.game_over = False
        self.winner = TIE  # Nobody is the winner
        # self._phase2_now()

        self.font_indicator = pygame.font.SysFont("", 34, True)
        self.font_pieces = pygame.font.SysFont("", 38, True)

    def render(self, surface: pygame.Surface):
        self._draw_board(surface)

        for node in self.nodes:
            node.render(surface)
            if node.piece:
                if node.piece != self.picked_up_piece:
                    node.piece.render(surface)
                if node.remove_thingy and self._get_turn_color() != node.piece.color:
                    node.render_remove_thingy(surface)

        if self.picked_up_piece is not None:
            self.picked_up_piece.render(surface)

        if self.phase == PHASE1:
            self._draw_player_pieces(surface, self.font_pieces)

        self._draw_player_indicator(surface, self.font_indicator)

    def update(self, mouse: tuple):
        mouse_x = mouse[0]
        mouse_y = mouse[1]
        for node in self.nodes:
            node.update(mouse_x, mouse_y, self.must_remove_piece)
            if node.piece is not None:
                node.piece.update(mouse_x, mouse_y)

    def on_window_resize(self, width: int, height: int):
        global window_width, window_height
        window_width = width
        window_height = height

        if height <= width:
            self.width = height - 160
        else:
            self.width = width - 160

        self.x = round((width - self.width) / 2)
        self.y = round((height - self.width) / 2)
        self.DIV = round(self.width / 6)

        self.nodes[0].set_position(self.x, self.y)
        self.nodes[1].set_position(self.x + self.DIV * 3, self.y)
        self.nodes[2].set_position(self.x + self.DIV * 6, self.y)
        self.nodes[3].set_position(self.x + self.DIV, self.y + self.DIV)
        self.nodes[4].set_position(self.x + self.DIV * 3, self.y + self.DIV)
        self.nodes[5].set_position(self.x + self.DIV * 5, self.y + self.DIV)
        self.nodes[6].set_position(self.x + self.DIV * 2, self.y + self.DIV * 2)
        self.nodes[7].set_position(self.x + self.DIV * 3, self.y + self.DIV * 2)
        self.nodes[8].set_position(self.x + self.DIV * 4, self.y + self.DIV * 2)
        self.nodes[9].set_position(self.x, self.y + self.DIV * 3)
        self.nodes[10].set_position(self.x + self.DIV, self.y + self.DIV * 3)
        self.nodes[11].set_position(self.x + self.DIV * 2, self.y + self.DIV * 3)
        self.nodes[12].set_position(self.x + self.DIV * 4, self.y + self.DIV * 3)
        self.nodes[13].set_position(self.x + self.DIV * 5, self.y + self.DIV * 3)
        self.nodes[14].set_position(self.x + self.DIV * 6, self.y + self.DIV * 3)
        self.nodes[15].set_position(self.x + self.DIV * 2, self.y + self.DIV * 4)
        self.nodes[16].set_position(self.x + self.DIV * 3, self.y + self.DIV * 4)
        self.nodes[17].set_position(self.x + self.DIV * 4, self.y + self.DIV * 4)
        self.nodes[18].set_position(self.x + self.DIV, self.y + self.DIV * 5)
        self.nodes[19].set_position(self.x + self.DIV * 3, self.y + self.DIV * 5)
        self.nodes[20].set_position(self.x + self.DIV * 5, self.y + self.DIV * 5)
        self.nodes[21].set_position(self.x, self.y + self.DIV * 6)
        self.nodes[22].set_position(self.x + self.DIV * 3, self.y + self.DIV * 6)
        self.nodes[23].set_position(self.x + self.DIV * 6, self.y + self.DIV * 6)

        # Assuming that 600 is the default window height
        Node.dot_radius = round((window_height * Node.DEFAULT_DOT_RADIUS) / 600)
        Node.radius = round((window_height * Node.DEFAULT_RADIUS) / 600)
        Piece.radius = round((window_height * Piece.DEFAULT_RADIUS) / 600)
        self.line_thickness = round((window_height * 8) / 600)
        self.board_offset = round((window_height * 35) / 600)

    def put_new_piece(self) -> bool:
        """Puts a new piece on to the board.

        Returns:
            bool: True if the turn was changed, False otherwise. For pymill_network.

        """
        changed_turn = False
        for node in self.nodes:
            if node.highlight and not node.piece:
                if self.turn == PLAYER1:
                    new_piece = Piece(node.x, node.y, WHITE)
                    node.add_piece(new_piece)
                    self.white_pieces -= 1
                    if not self._check_windmills(WHITE, node):
                        self._switch_turn()
                        changed_turn = True
                    else:
                        self.must_remove_piece = True
                        logger.debug("Remove a piece!")
                else:
                    new_piece = Piece(node.x, node.y, BLACK)
                    node.add_piece(new_piece)
                    self.black_pieces -= 1
                    if not self._check_windmills(BLACK, node):
                        self._switch_turn()
                        changed_turn = True
                    else:
                        self.must_remove_piece = True
                        logger.debug("Remove a piece!")
                break
        if (self.white_pieces + self.black_pieces) == 0:
            self.phase = PHASE2
            logger.info("PHASE 2")
        return changed_turn

    def pick_up_piece(self):
        for node in self.nodes:
            if node.highlight and node.piece and self.picked_up_piece is None:
                if node.piece.pick_up(self.turn):
                    self._change_node_color(node, (0, 255, 0), (255, 0, 0))
                    self.node_taken_piece = node
                    self.picked_up_piece = node.piece
                break

    def remove_opponent_piece(self) -> bool:
        """Removes a piece from opponent.

        Returns:
            bool: True if the player can actually remove the piece, False otherwise.

        """
        can_remove = False

        for node in self.nodes:
            if self.turn == PLAYER1:
                if node.highlight and node.piece and node.piece.color == BLACK:
                    if not self._check_windmills(BLACK, node) or \
                            self._number_pieces_in_windmills(BLACK) == self._count_pieces(BLACK):
                        node.take_piece()
                        self.must_remove_piece = False
                        if self._check_player_pieces(BLACK):
                            self.game_over = True
                        self._switch_turn()
                        can_remove = True
                    else:
                        logger.info("You cannot take piece from windmill!")
            else:
                if node.highlight and node.piece and node.piece.color == WHITE:
                    if not self._check_windmills(WHITE, node) or \
                            self._number_pieces_in_windmills(WHITE) == self._count_pieces(WHITE):
                        node.take_piece()
                        self.must_remove_piece = False
                        if self._check_player_pieces(WHITE):
                            self.game_over = True
                        self._switch_turn()
                        can_remove = True
                    else:
                        logger.info("You cannot take piece from windmill!")
        self.node_pressed = False
        return can_remove

    def put_down_piece(self) -> bool:
        """Puts down a picked up piece.

        Returns:
            bool: True if the turn was changed, False otherwise. For morris_net.

        """
        changed_turn = False
        if self.picked_up_piece is not None:
            for node in self._where_can_go(self.node_taken_piece):
                if node.highlight and not node.piece:
                    node.add_piece(self.picked_up_piece)
                    logger.debug("Piece: {}".format(node.piece))
                    self._change_node_color(self.node_taken_piece, (0, 0, 0), (0, 0, 0))
                    self.node_taken_piece.piece.release(node)
                    self.node_taken_piece.take_piece()
                    self.node_taken_piece = None
                    self.picked_up_piece = None
                    if not self._check_windmills(WHITE if self.turn == PLAYER1 else BLACK, node):
                        self._switch_turn()
                        changed_turn = True
                    else:
                        self.must_remove_piece = True
                        logger.info("Remove a piece!")

        # Release piece if player released the left button.
        if self.picked_up_piece is not None:
            self._change_node_color(self.node_taken_piece, (0, 0, 0), (0, 0, 0))
            self.picked_up_piece.release(self.node_taken_piece)
            self.picked_up_piece = None

        if self._check_player_pieces(WHITE if self.turn == PLAYER1 else BLACK):  # inverse WHITE and BLACK because turn
            if not self.must_remove_piece:                                      # was already switched
                self.game_over = True
                changed_turn = False  # todo check this
                logger.debug("game_over = True")
        return changed_turn

    def put_new_piece_alone(self, node_id: int, piece_color: tuple):
        """Puts a new piece on that node. For computer and networking versions of the game.

        Args:
            node_id: The node on which to put the new piece.
            piece_color: What type of piece to put.

        """
        assert 0 <= node_id <= 23
        assert self.phase == PHASE1

        for node in self.nodes:
            if node.id == node_id:
                assert node.piece is None
                node.add_piece(Piece(node.x, node.y, piece_color))
                if piece_color == WHITE:
                    self.white_pieces -= 1
                else:
                    self.black_pieces -= 1
                if not self._check_windmills(piece_color, node):
                    self._switch_turn()
                else:
                    self.must_remove_piece = True
                    logger.debug("Remove a piece!")
                break

    def change_piece_location(self, source_node_id: int, destination_node_id: int):
        assert 0 <= source_node_id <= 23 and 0 <= destination_node_id <= 23
        assert self.phase == PHASE2

        piece = None
        for node in self.nodes:
            if node.id == source_node_id:
                assert node.piece is not None
                piece = node.piece
                node.take_piece()

        for node in self.nodes:
            if node.id == destination_node_id:
                assert node.piece is None
                node.add_piece(piece)

                if not self._check_windmills(piece.color, node):
                    self._switch_turn()
                else:
                    self.must_remove_piece = True
                    logger.debug("Remove a piece!")

    def mouse_over_node(self) -> bool:
        for node in self.nodes:
            if node.highlight:
                return True
        return False

    def _draw_board(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (252, 219, 86), (self.x - self.board_offset, self.y - self.board_offset,
                                                   self.width + self.board_offset * 2, self.width + self.board_offset * 2))

        # Drawing three rectangles...
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.width), self.line_thickness)
        pygame.draw.rect(surface, (0, 0, 0), (self.x + self.DIV, self.y + self.DIV,
                                              self.width - self.DIV * 2, self.width - self.DIV * 2), self.line_thickness)
        pygame.draw.rect(surface, (0, 0, 0), (self.x + self.DIV * 2, self.y + self.DIV * 2,
                                              self.width - self.DIV * 4, self.width - self.DIV * 4), self.line_thickness)
        # ...and four middle lines.
        pygame.draw.line(surface, (0, 0, 0), (self.x + self.DIV * 3, self.y),
                         (self.x + self.DIV * 3, self.y + self.DIV * 2), self.line_thickness)
        pygame.draw.line(surface, (0, 0, 0), (self.x, self.y + self.DIV * 3),
                         (self.x + self.DIV * 2, self.y + self.DIV * 3), self.line_thickness)
        pygame.draw.line(surface, (0, 0, 0), (self.x + self.DIV * 3, self.y + self.DIV * 6),
                         (self.x + self.DIV * 3, self.y + self.DIV * 4), self.line_thickness)
        pygame.draw.line(surface, (0, 0, 0), (self.x + self.DIV * 6, self.y + self.DIV * 3),
                         (self.x + self.DIV * 4, self.y + self.DIV * 3), self.line_thickness)

    def _draw_player_pieces(self, surface: pygame.Surface, font: pygame.font.Font):
        player1_text = font.render("x {}".format(self.white_pieces), True, (0, 0, 0))
        player2_text = font.render("x {}".format(self.black_pieces), True, (0, 0, 0))
        surface.blit(player1_text, (20, window_height // 2 - 30))
        surface.blit(player2_text, (window_width - 20 - player2_text.get_width(), window_height // 2 - 30))

    def _draw_player_indicator(self, surface: pygame.Surface, font: pygame.font.Font):
        text = font.render("WHITE'S TURN" if self.turn == PLAYER1 else "BLACK'S TURN", True, (0, 0, 0))
        surface.blit(text, (self.x, window_height - 35))

    def _switch_turn(self):
        if self.turn == PLAYER1:
            self.turn = PLAYER2
        else:
            self.turn = PLAYER1

    @staticmethod
    def _check_nodes(w_mill: tuple, color: tuple) -> bool:
        """Checks if all nodes within a group of nodes have pieces of the same color.

        Args:
            w_mill (tuple): The group of nodes to check (a possible windmill).
            color (tuple): The color that the pieces all need to be.

        Returns:
            bool: True if the nodes within the windmill actually form a windmill, False otherwise.

        """
        nodes = []
        for n in w_mill:
            if n.piece and n.piece.color == color:
                nodes.append(True)
            else:
                nodes.append(False)
        if all(nodes):
            return True
        else:
            return False

    def _check_windmills(self, color: tuple, node: Node) -> bool:
        """Checks if there is a windmill formed and if node is any of the windmill's nodes.

        Args:
            color (tuple): The color of the pieces to check.
            node (Node): The node to check if is any of windmill's nodes.

        Returns:
            bool: True if there is a windmill and if node is in there, False otherwise.

        """
        for i, windmill in enumerate(self.windmills):
            if self._check_nodes(windmill, color) and any(map(lambda n: n is node, windmill)):
                logger.debug("{} windmill: {}".format("Black" if color == BLACK else "White", i))
                # self.turns_without_windmills = 0
                return True
        return False

    def _count_pieces(self, color: tuple) -> int:
        """Counts the number of pieces a player has.

        Args:
            color (tuple): The color of the pieces it counts.

        Returns:
            int: The number of pieces a player has.

        """
        pieces = 0
        for node in self.nodes:
            if node.piece and node.piece.color == color:
                pieces += 1
        logger.debug(f"{'PLAYER1' if color == WHITE else 'PLAYER2'} pieces remaining: {pieces}")
        return pieces

    def _check_player_pieces(self, color: tuple) -> bool:
        """Checks the number of pieces of a player and returns if the game is over.

        If the player has 3 pieces remaining, his/her pieces can go anywhere and if 2 pieces remaining, he/she loses.

        Args:
            color (tuple): The color of the pieces to check.

        Returns:
            bool: True if the game is over, False otherwise.

        """
        player = PLAYER1 if color == WHITE else PLAYER2
        pieces_left = self._count_pieces(color)

        if self.phase == PHASE2:
            if pieces_left == 3:
                self.can_jump[player] = True
            else:
                self.can_jump[player] = False

            if pieces_left == 2:
                win = "White won!" if player == PLAYER2 else "Black won!"
                print(win)
                self.winner = WHITE if player == PLAYER2 else BLACK
                return True

        pieces_to_check = (self.black_pieces < 2) if player is PLAYER2 else (self.white_pieces < 2)
        if pieces_to_check:
            if self._is_opponent_blocked(player):
                win = "White won!" if player is PLAYER2 else "Black won!"
                print(win)
                self.winner = WHITE if player == PLAYER2 else BLACK
                return True

        return False

    def _where_can_go(self, node: Node) -> tuple:
        """Decides where a piece can go based on the dictionary self.can_jump.

        Args:
            node (Node): The node from where the piece wants to go.

        Returns:
            tuple: The nodes where the piece can go.

        """
        assert node is not None, "Node shouldn't be None..."

        if self.turn == PLAYER1 and not self.can_jump[PLAYER1] or self.turn == PLAYER2 and not self.can_jump[PLAYER2]:
            return node.search_neighbors(self.nodes, self.DIV)
        else:
            new_nodes = list(self.nodes)
            new_nodes.remove(node)
            return tuple(new_nodes)

    def _number_pieces_in_windmills(self, color: tuple) -> int:
        """Counts the number of pieces that are inside of every windmill.

        Args:
            color (tuple): The color of the pieces to count.

        Returns:
            int: The number of pieces that are inside windmills.

        """
        pieces_inside_windmills = set()
        for windmill in self.windmills:
            if self._check_nodes(windmill, color):
                for node in windmill:
                    pieces_inside_windmills.add(node)
        return len(pieces_inside_windmills)

    def _change_node_color(self, node: Node, color1: tuple, color2: tuple):
        """Changes color of other nodes based on where the piece can go.

        Args:
            node (Node): The node where the piece currently sits.
            color1 (tuple): The color to change the nodes where the piece can go.
            color2 (tuple): The color to change the nodes where the piece cannot go.

        """
        for n in self._where_can_go(node):
            n.change_color(color1)

        nodes_copy = list(self.nodes)
        for i in self.nodes:
            for j in self._where_can_go(node):
                if i is j:
                    nodes_copy.remove(i)
        nodes_copy.remove(node)

        for n in nodes_copy:
            n.change_color(color2)

    def _is_opponent_blocked(self, player: int) -> bool:
        """Checks if a player has any legal moves to do.

        Args:
            player (int): The player whose pieces to check.

        Returns:
            bool: True if the player is blocked, False otherwise.

        """
        if player == PLAYER1:
            color = WHITE
        else:
            color = BLACK

        logger.debug(f"Player {player} is checked")
        player_nodes = [node for node in self.nodes if node.piece and node.piece.color == color]
        num_of_player_nodes = len(player_nodes)

        for node in player_nodes:
            where_can_go = self._where_can_go(node)
            num_of_nodes_can_go = len(where_can_go)
            # print(where_can_go)
            for n in where_can_go:
                if n.piece:
                    num_of_nodes_can_go -= 1

            if not num_of_nodes_can_go:
                num_of_player_nodes -= 1

        logger.debug(f"num_of_player_nodes = {num_of_player_nodes}")

        if not num_of_player_nodes and self._count_pieces(color) > 3 \
                and (self.white_pieces == 0 if color == WHITE else self.black_pieces == 0):
            logger.info("Player {} is blocked!".format(player))
            return True
        else:
            return False

    def _get_turn_color(self):
        if self.turn == PLAYER1:
            return WHITE
        else:
            return BLACK

    # def _phase2_now(self):
    #     """Automatically puts all pieces. Only for testing purposes."""
    #     w = True
    #     for node in self.nodes:
    #         if not node.piece and (self.white_pieces + self.black_pieces) > 0:
    #             if w:
    #                 new_piece = Piece(node.x, node.y, WHITE)
    #                 node.add_piece(new_piece)
    #                 self._switch_turn()
    #                 self.white_pieces -= 1
    #                 w = not w
    #             else:
    #                 new_piece = Piece(node.x, node.y, BLACK)
    #                 node.add_piece(new_piece)
    #                 self._switch_turn()
    #                 self.black_pieces -= 1
    #                 w = not w
