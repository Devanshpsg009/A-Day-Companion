import pygame
from backend.logic import GameState
from sys import exit

class ChessGame:
    def __init__(self, width, height, title, fps):
        self.game_engine = GameState()
        pygame.init()
        self.width = width
        self.height = height
        self.square_size = width // 8
        self.fps = fps
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        self.light_color = (240, 217, 181)
        self.dark_color = (139, 69, 19)
        
        self.pieces = self.load_pieces()
        self.textf = pygame.font.Font(None,30)
        self.p_list_alp = ["a","b","c","d","e","f","g","h"]
        self.p_list_num = ["1","2","3","4","5","6","7","8"]

    def load_pieces(self):
        piece_paths = {
            "P_w" : "assets/Chess_plt60.png", "P_b" : "assets/Chess_pdt60.png",
            "B_w" : "assets/Chess_blt60.png", "B_b" : "assets/Chess_bdt60.png",
            "N_w" : "assets/Chess_nlt60.png", "N_b" : "assets/Chess_ndt60.png",
            "R_w" : "assets/Chess_rlt60.png", "R_b" : "assets/Chess_rdt60.png",
            "Q_w" : "assets/Chess_qlt60.png", "Q_b" : "assets/Chess_qdt60.png",
            "K_w" : "assets/Chess_klt60.png", "K_b" : "assets/Chess_kdt60.png"
        }
        
        loaded_pieces = {}
        for name, path in piece_paths.items():
            image = pygame.image.load(path).convert_alpha()
            loaded_pieces[name] = pygame.transform.smoothscale(image, (90, 90))

        return loaded_pieces

    def draw_board(self):
        self.choice = self.game_engine.player_color
        for row in range(8):
            for col in range(8):
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                rect = (col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)
        if self.choice == "white":
            for i in range(8):
                notation = self.textf.render(self.p_list_alp[i], True, (0, 0, 0))
                self.screen.blit(notation, (i * self.square_size + 45, self.height - 18))
                notation = self.textf.render(self.p_list_num[7 - i], True, (0, 0, 0))
                self.screen.blit(notation, (5, i * self.square_size + 45))
        else:
            for i in range(8):
                notation = self.textf.render(self.p_list_alp[7-i], True, (0, 0, 0))
                self.screen.blit(notation, (i * self.square_size + 45, self.height - 18))
                notation = self.textf.render(self.p_list_num[i], True, (0, 0, 0))
                self.screen.blit(notation, (5, i * self.square_size + 45))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.game_engine.board[row][col]
                if piece != "--":
                    color, p_type = piece[0], piece[1]
                    key = f"{p_type}_{color}"
                    if key in self.pieces:
                        if self.choice == "white":
                            self.screen.blit(self.pieces[key], (col * self.square_size + 2.5, row * self.square_size + 2.5))
                        else:
                            self.screen.blit(self.pieces[key], ((7-col) * self.square_size + 2.5, (7-row) * self.square_size + 2.5))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.draw_board()
            self.draw_pieces()
            pygame.display.update()
            self.clock.tick(self.fps)