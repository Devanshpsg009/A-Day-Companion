class GameState:
    def __init__(self):
        self.turn = "white"
        self.player_color = "black"
        self.move_history = []
        self.board = self.chess_board()
        
    def chess_board(self):
        pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP", "--"]
        b_rook = pieces[0]
        b_knight = pieces[1]
        b_bishop = pieces[2]
        b_queen = pieces[3]
        b_king = pieces[4]
        b_pawn = pieces[5]
        w_rook = pieces[6]
        w_knight = pieces[7]
        w_bishop = pieces[8]
        w_queen = pieces[9]
        w_king = pieces[10]
        w_pawn = pieces[11]
        empty = pieces[12]
        
        self.board = [
            [b_rook, b_knight, b_bishop, b_queen, b_king, b_bishop, b_knight, b_rook],
            [b_pawn] * 8,
            [empty] * 8,
            [empty] * 8,
            [empty] * 8,
            [empty] * 8,
            [w_pawn] * 8,
            [w_rook, w_knight, w_bishop, w_queen, w_king, w_bishop, w_knight, w_rook]
        ]
        return self.board
    def move_piece(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        self.board[end_pos[0]][end_pos[1]] = piece
        self.board[start_pos[0]][start_pos[1]] = "--"
        self.move_history.append((piece, start_pos, end_pos))
        self.turn = "black" if self.turn == "white" else "white"