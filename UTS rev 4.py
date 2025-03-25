import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Label, Button
import copy
import random

class ShogiPiece:
    def __init__(self, name, kanji, romaji, is_player=True):
        self.name = name
        self.kanji = kanji
        self.romaji = romaji
        self.is_player = is_player
        self.promoted = False
        self.captured = False
        self.can_be_promoted = True  # By default pieces can be promoted

    def get_moves(self, board, x, y):
        return []

    def can_promote(self, from_y, to_y):
        if not self.can_be_promoted or self.promoted:
            return False
        
        # Promotion zone: top 3 rows for player, bottom 3 rows for AI
        if self.is_player and (from_y <= 2 or to_y <= 2):
            return True
        elif not self.is_player and (from_y >= 6 or to_y >= 6):
            return True
        return False
    
    def must_promote(self, to_y):
        # Pawn and Lance must be promoted if they reach the furthest row
        if self.name in ["Pion", "Lancer"]:
            if self.is_player and to_y == 0:
                return True
            elif not self.is_player and to_y == 8:
                return True
        # Knight must be promoted if it reaches the two furthest rows
        elif self.name == "Knight":
            if self.is_player and to_y <= 1:
                return True
            elif not self.is_player and to_y >= 7:
                return True
        return False

    def promote(self):
        self.promoted = True

    def get_display_name(self):
        if self.promoted:
            return f"+{self.kanji}"
        return self.kanji

    def get_display_romaji(self):
        if self.promoted:
            if self.name == "Pion":
                return "to"
            elif self.name == "Lancer":
                return "nkyo"
            elif self.name == "Knight":
                return "nkei"
            elif self.name == "Silver":
                return "ngin"
            elif self.name == "Bishop":
                return "uma"
            elif self.name == "Rook":
                return "ryu"
            else:
                return f"+{self.romaji}"
        return self.romaji

    def is_valid_move(self, board, from_x, from_y, to_x, to_y):
        # Check if move is in the list of possible moves
        moves = self.get_moves(board, from_x, from_y)
        if (to_x, to_y) not in moves:
            return False
        
        # Check if there is a piece of the same side at the destination
        if board[to_y][to_x] is not None and board[to_y][to_x].is_player == self.is_player:
            return False
        
        # Simulate the move to check if the king will be in check
        temp_board = copy.deepcopy(board)
        captured_piece = temp_board[to_y][to_x]
        temp_board[to_y][to_x] = temp_board[from_y][from_x]
        temp_board[from_y][from_x] = None
        
        # Find king position
        king_pos = None
        for y in range(9):
            for x in range(9):
                if temp_board[y][x] is not None and temp_board[y][x].name == "King" and temp_board[y][x].is_player == self.is_player:
                    king_pos = (x, y)
                    break
            if king_pos:
                break
        
        # Check if the king is in check after the move
        if king_pos:
            for y in range(9):
                for x in range(9):
                    if temp_board[y][x] is not None and temp_board[y][x].is_player != self.is_player:
                        enemy_moves = temp_board[y][x].get_moves(temp_board, x, y)
                        if king_pos in enemy_moves:
                            return False
        
        return True

    def copy(self):
        new_piece = type(self)(is_player=self.is_player)
        new_piece.promoted = self.promoted
        new_piece.captured = self.captured
        new_piece.can_be_promoted = self.can_be_promoted
        return new_piece

class King(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("King", "王", "ou", is_player)
        if is_player:
            self.kanji = "玉"
            self.romaji = "gyoku"
        self.can_be_promoted = False  # King cannot be promoted

    def get_moves(self, board, x, y):
        moves = []
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
        
        return moves

class Rook(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Rook", "飛", "hi", is_player)

    def get_moves(self, board, x, y):
        moves = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy
        
        # Additional moves for Dragon (Promoted Rook)
        if self.promoted:
            diagonals = [(-1, -1), (1, -1), (1, 1), (-1, 1)]  # Diagonals
            for dx, dy in diagonals:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9:
                    if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                        moves.append((nx, ny))
        
        return moves

class Bishop(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Bishop", "角", "kaku", is_player)

    def get_moves(self, board, x, y):
        moves = []
        directions = [(-1, -1), (1, -1), (1, 1), (-1, 1)]  # Diagonals
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy
        
        # Additional moves for Horse (Promoted Bishop)
        if self.promoted:
            orthogonals = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
            for dx, dy in orthogonals:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9:
                    if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                        moves.append((nx, ny))
        
        return moves

class Gold(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Gold", "金", "kin", is_player)
        self.can_be_promoted = False  # Gold cannot be promoted

    def get_moves(self, board, x, y):
        moves = []
        if self.is_player:
            directions = [
                (-1, -1), (0, -1), (1, -1),
                (-1, 0), (1, 0),
                (0, 1)
            ]
        else:
            directions = [
                (-1, 1), (0, 1), (1, 1),
                (-1, 0), (1, 0),
                (0, -1)
            ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
        
        return moves

class Silver(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Silver", "銀", "gin", is_player)

    def get_moves(self, board, x, y):
        moves = []
        if not self.promoted:
            if self.is_player:
                directions = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 1), (1, 1)
                ]
            else:
                directions = [
                    (-1, 1), (0, 1), (1, 1),
                    (-1, -1), (1, -1)
                ]
        else:
            # Promoted Silver moves like Gold
            if self.is_player:
                directions = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0), (1, 0),
                    (0, 1)
                ]
            else:
                directions = [
                    (-1, 1), (0, 1), (1, 1),
                    (-1, 0), (1, 0),
                    (0, -1)
                ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
        
        return moves

class Knight(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Knight", "桂", "kei", is_player)

    def get_moves(self, board, x, y):
        moves = []
        if not self.promoted:
            if self.is_player:
                directions = [(-1, -2), (1, -2)]  # L-shape forward
            else:
                directions = [(-1, 2), (1, 2)]  # L-shape forward
        else:
            # Promoted Knight moves like Gold
            if self.is_player:
                directions = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0), (1, 0),
                    (0, 1)
                ]
            else:
                directions = [
                    (-1, 1), (0, 1), (1, 1),
                    (-1, 0), (1, 0),
                    (0, -1)
                ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
        
        return moves

class Lancer(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Lancer", "香", "kyo", is_player)

    def get_moves(self, board, x, y):
        moves = []
        if not self.promoted:
            if self.is_player:
                dy = -1  # Straight forward
            else:
                dy = 1  # Straight forward
            
            nx, ny = x, y + dy
            while 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
                    break
                else:
                    break
                ny += dy
        else:
            # Promoted Lancer moves like Gold
            if self.is_player:
                directions = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0), (1, 0),
                    (0, 1)
                ]
            else:
                directions = [
                    (-1, 1), (0, 1), (1, 1),
                    (-1, 0), (1, 0),
                    (0, -1)
                ]
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9:
                    if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                        moves.append((nx, ny))
        
        return moves

class Pion(ShogiPiece):
    def __init__(self, is_player=True):
        super().__init__("Pion", "歩", "fu", is_player)

    def get_moves(self, board, x, y):
        moves = []
        if not self.promoted:
            if self.is_player:
                dy = -1  # Forward
            else:
                dy = 1  # Forward
            
            nx, ny = x, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                    moves.append((nx, ny))
        else:
            # Promoted Pawn (Tokin) moves like Gold
            if self.is_player:
                directions = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0), (1, 0),
                    (0, 1)
                ]
            else:
                directions = [
                    (-1, 1), (0, 1), (1, 1),
                    (-1, 0), (1, 0),
                    (0, -1)
                ]
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9:
                    if board[ny][nx] is None or board[ny][nx].is_player != self.is_player:
                        moves.append((nx, ny))
        
        return moves

class ShogiGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Shogi - Japanese Chess Game")
        self.root.geometry("800x650")
        self.root.configure(bg="#F5DEB3")
        
        self.board = self.initialize_board()
        self.player_captures = []
        self.ai_captures = []
        self.selected_piece = None
        self.selected_pos = None
        self.player_turn = True  # True for player, False for AI
        
        self.player_score = 0
        self.ai_score = 0
        self.time_limit = 10  # time per second
        self.move_timer = None
        
        self.create_gui()
        self.update_board_display()
        self.start_turn_timer()
        
    def start_turn_timer(self):
        if self.move_timer:
            self.root.after_cancel(self.move_timer)
        self.time_remaining = self.time_limit
        self.update_timer()
        self.move_timer = self.root.after(1000, self.decrement_timer)

    def update_timer(self):
        self.timer_label.config(text=f"Waktu: {self.time_remaining}s")

    def decrement_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer()
            self.move_timer = self.root.after(1000, self.decrement_timer)
        else:
            # Time's up - change turn
            if self.player_turn:
                self.status_label.config(text="Time's up! Turn changes to AI.")
                self.player_turn = False
                self.update_board_display()
                self.root.after(500, self.ai_move)
            else:
                self.status_label.config(text="Time's up! Turn changes to Player.")
                self.player_turn = True
                self.update_board_display()
            
            # Reset timer for the next turn
            self.start_turn_timer()
    
    def initialize_board(self):
        # Create empty 9x9 board
        board = [[None for _ in range(9)] for _ in range(9)]
        
        # Initial positions for player pieces (rows 6-8)
        board[8][0] = Lancer(True)
        board[8][1] = Knight(True)
        board[8][2] = Silver(True)
        board[8][3] = Gold(True)
        board[8][4] = King(True)
        board[8][5] = Gold(True)
        board[8][6] = Silver(True)
        board[8][7] = Knight(True)
        board[8][8] = Lancer(True)
  
        board[7][1] = Bishop(True)
        board[7][7] = Rook(True)
        
        for i in range(9):
            board[6][i] = Pion(True)
        
        # Initial positions for AI pieces (rows 0-2)
        board[0][0] = Lancer(False)
        board[0][1] = Knight(False)
        board[0][2] = Silver(False)
        board[0][3] = Gold(False)
        board[0][4] = King(False)
        board[0][5] = Gold(False)
        board[0][6] = Silver(False)
        board[0][7] = Knight(False)
        board[0][8] = Lancer(False)
        
        board[1][1] = Rook(False)
        board[1][7] = Bishop(False)
        
        for i in range(9):
            board[2][i] = Pion(False)
            
        return board
    
    def create_gui(self):
        self.main_frame = Frame(self.root, bg="#F5DEB3")
        self.main_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Configure columns to make the center column wider for the board
        self.main_frame.grid_columnconfigure(0, weight=1)  # Left side
        self.main_frame.grid_columnconfigure(1, weight=3)  # Center (board) - more weight
        self.main_frame.grid_columnconfigure(2, weight=1)  # Right side
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Frame untuk menampung semua informasi dalam satu baris
        self.info_frame = Frame(self.main_frame, bg="#F5DEB3")
        self.info_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Turn information
        self.turn_label = Label(self.info_frame, text="Giliran: Pemain", font=("Arial", 14), bg="#F5DEB3")
        self.turn_label.pack(side=tk.LEFT, padx=20)

        # Score info
        self.score_label = Label(self.info_frame, text="Pemain: 0 | AI: 0", font=("Arial", 14), bg="#F5DEB3")
        self.score_label.pack(side=tk.LEFT, padx=20)

        # Timer info
        self.timer_label = Label(self.info_frame, text="Waktu: 10dtk", font=("Arial", 14), bg="#F5DEB3")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # Frame for player captured pieces
        self.player_capture_frame = Frame(self.main_frame, bg="#E6C88A", bd=2, relief=tk.RAISED)
        self.player_capture_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        
        Label(self.player_capture_frame, text="Bidak Pemain", font=("Arial", 12), bg="#E6C88A").pack(pady=5)
        self.player_capture_canvas = Canvas(self.player_capture_frame, width=100, height=400, bg="#E6C88A")
        self.player_capture_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Frame for board - centered with fixed size
        self.board_frame = Frame(self.main_frame, bg="#D2B48C", bd=3, relief=tk.RAISED)
        self.board_frame.grid(row=1, column=1, padx=10, sticky="n")  # Changed to "n" (north) to align to top-center
        
        # Create a container frame to center the canvas
        self.board_container = Frame(self.board_frame, bg="#D2B48C")
        self.board_container.pack(pady=10, expand=True)
        
        # Fixed size for the board - 450x450
        self.canvas = Canvas(self.board_container, width=450, height=450, bg="#D2B48C", highlightthickness=0)
        self.canvas.pack()
        
        # Frame for AI captured pieces
        self.ai_capture_frame = Frame(self.main_frame, bg="#E6C88A", bd=2, relief=tk.RAISED)
        self.ai_capture_frame.grid(row=1, column=2, padx=10, sticky="nsew")
        
        Label(self.ai_capture_frame, text="Bidak AI", font=("Arial", 12), bg="#E6C88A").pack(pady=5)
        self.ai_capture_canvas = Canvas(self.ai_capture_frame, width=100, height=400, bg="#E6C88A")
        self.ai_capture_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Add handler for clicks on the board
        self.canvas.bind("<Button-1>", self.handle_click)
        self.player_capture_canvas.bind("<Button-1>", self.handle_capture_click)
        
        # Status label
        self.status_label = Label(self.root, text="Klik bidak untuk dipilih, lalu klik posisi yang di tuju.", 
                         font=("Arial", 12), bg="#F5DEB3")
        self.status_label.pack(pady=10, fill=tk.X)
        
        # Reset button
        frame_buttons = Frame(self.root, bg="#F5DEB3")
        frame_buttons.pack(pady=5, fill=tk.X)

        self.reset_button = Button(frame_buttons, text="Restart Game", font=("Arial", 12), 
                                  command=self.reset_game, bg="#D2B48C")
        self.reset_button.pack(pady=5)
        
    def on_window_resize(self, event):
        # Hanya perbarui jika ukuran baru cukup besar
        if event.width >= 800 and event.height >= 650:
            self.update_board_display()

    def get_piece_value(self, piece):
        values = {"Pion": 1, "Lancer": 3, "Knight": 3, "Silver": 5, "Gold": 6, "Bishop": 8, "Rook": 10, "King": 100}
        # Add bonus for promoted pieces
        value = values.get(piece.name, 0)
        if piece.promoted:
            value += 2
        return value
    
    def update_board_display(self):
        self.canvas.delete("all")
        
        # Use fixed cell size for consistent board display
        cell_size = 50
        
        # Draw 9x9 board
        for y in range(9):
            for x in range(9):
                # Draw square for each cell
                self.canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, 
                                           fill="#E8C184", outline="#000000")
                
                # Draw promotion zone
                if y < 3:  # Player's promotion zone
                    self.canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, 
                                               fill="#E8C184", outline="#000000", stipple="gray50")
                elif y > 5:  # AI's promotion zone
                    self.canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, 
                                               fill="#E8C184", outline="#000000", stipple="gray50")
                
                # Draw pieces on each cell
                if self.board[y][x]:
                    piece = self.board[y][x]
                    bg_color = "#FFD700" if piece.is_player else "#FF6347"
                    text_color = "#000000"
                    
                    # Highlight selected piece
                    if self.selected_pos and self.selected_pos == (x, y):
                        bg_color = "#00FF00"
                    
                    # Create circle for piece
                    self.canvas.create_oval(x*cell_size+5, y*cell_size+5, (x+1)*cell_size-5, (y+1)*cell_size-5, 
                                          fill=bg_color, outline="#000000")
                    
                    # Add kanji for piece
                    self.canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2-7, 
                                          text=piece.get_display_name(), fill=text_color, font=("Arial", 14))
                    
                    # Add romaji below the kanji
                    self.canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2+10, 
                                          text=piece.get_display_romaji(), fill=text_color, font=("Arial", 8))
        
        # Highlight possible moves
        if self.selected_piece and self.selected_pos:
            x, y = self.selected_pos
            moves = self.selected_piece.get_moves(self.board, x, y)
            for move_x, move_y in moves:
                if self.selected_piece.is_valid_move(self.board, x, y, move_x, move_y):
                    self.canvas.create_rectangle(move_x*cell_size, move_y*cell_size, 
                                               (move_x+1)*cell_size, (move_y+1)*cell_size, 
                                               outline="#0000FF", width=2)
        
        # Update captured pieces display
        self.update_captures_display()
        
        # Update turn label
        self.turn_label.config(text="Turn: Player" if self.player_turn else "Turn: AI")
        
        # Update score label
        self.score_label.config(text=f"Player: {self.player_score} | AI: {self.ai_score}")
    
    def update_captures_display(self):
        self.player_capture_canvas.delete("all")
        self.ai_capture_canvas.delete("all")
        
        cell_size = 40
        
        # Player's captured pieces
        for i, piece in enumerate(self.player_captures):
            y = i % 10
            x = i // 10
            
            self.player_capture_canvas.create_oval(x*cell_size+5, y*cell_size+5, 
                                                (x+1)*cell_size-5, (y+1)*cell_size-5, 
                                                fill="#FFD700", outline="#000000")
            
            self.player_capture_canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2-5, 
                                                text=piece.kanji, fill="#000000", font=("Arial", 12))
            
            self.player_capture_canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2+8, 
                                                text=piece.romaji, fill="#000000", font=("Arial", 6))
        
        # AI's captured pieces
        for i, piece in enumerate(self.ai_captures):
            y = i % 10
            x = i // 10
            
            self.ai_capture_canvas.create_oval(x*cell_size+5, y*cell_size+5, 
                                             (x+1)*cell_size-5, (y+1)*cell_size-5, 
                                             fill="#FF6347", outline="#000000")
            
            self.ai_capture_canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2-5, 
                                             text=piece.kanji, fill="#000000", font=("Arial", 12))
            
            self.ai_capture_canvas.create_text(x*cell_size+cell_size/2, y*cell_size+cell_size/2+8, 
                                             text=piece.romaji, fill="#000000", font=("Arial", 6))
    
    def handle_click(self, event):
        if not self.player_turn:
            return
        
        cell_size = 50
        x = event.x // cell_size
        y = event.y // cell_size
        
        if x < 0 or x > 8 or y < 0 or y > 8:
            return
        
        # If no piece is selected, select a piece
        if self.selected_piece is None:
            if self.board[y][x] is not None and self.board[y][x].is_player:
                self.selected_piece = self.board[y][x]
                self.selected_pos = (x, y)
                self.status_label.config(text=f"Piece {self.selected_piece.name} selected. Choose destination.")
                self.update_board_display()
        # If a piece is already selected, try to move it
        else:
            # Check if we're trying to select another board piece
            if self.board[y][x] is not None and self.board[y][x].is_player:
                # Select another piece
                self.selected_piece = self.board[y][x]
                self.selected_pos = (x, y)
                self.status_label.config(text=f"Piece {self.selected_piece.name} selected. Choose destination.")
            else:
                # Trying to move to an empty space or capture
                if self.selected_pos is not None:
                    # Moving from board
                    from_x, from_y = self.selected_pos
                    if self.selected_piece.is_valid_move(self.board, from_x, from_y, x, y):
                        # Store the piece before moving (it might get reset in move_piece)
                        piece_to_check = self.selected_piece
                        
                        # Move the piece
                        self.move_piece(from_x, from_y, x, y)
                        
                        # Check if the piece needs to be promoted
                        if piece_to_check.must_promote(y):
                            piece_to_check.promote()
                            self.status_label.config(text=f"{piece_to_check.name} automatically promoted!")
                            # End player's turn after the move
                            self.end_player_turn()
                        # Check if the piece can be promoted
                        elif piece_to_check.can_promote(from_y, y):
                            # Store reference to the piece
                            self.piece_to_promote = piece_to_check
                            self.ask_promotion()
                        else:
                            # End player's turn
                            self.end_player_turn()
                    else:
                        self.status_label.config(text="Invalid move. Try again.")
                else:
                    # Dropping a captured piece
                    if self.board[y][x] is None:  # Can only drop on empty squares
                        # Try to drop the piece
                        if self.drop_piece(self.selected_piece, x, y):
                            # Remove from player captures
                            self.player_captures.remove(self.selected_piece)
                            self.status_label.config(text=f"Dropped {self.selected_piece.name}.")
                            # End player's turn
                            self.end_player_turn()
                        else:
                            self.status_label.config(text="Invalid drop. Try again.")
                    else:
                        self.status_label.config(text="Cannot drop on an occupied square.")
            
            self.update_board_display()
    
    def handle_capture_click(self, event):
        if not self.player_turn:
            return
        
        cell_size = 40
        x = event.x // cell_size
        y = event.y // cell_size
        
        idx = y + x * 10
        if idx < len(self.player_captures):
            self.selected_piece = self.player_captures[idx]
            self.selected_pos = None  # No position on board yet
            self.status_label.config(text=f"Captured {self.selected_piece.name} selected. Choose destination for drop.")
            self.update_board_display()
    
    def move_piece(self, from_x, from_y, to_x, to_y):
        # Handle captured pieces
        if self.board[to_y][to_x] is not None:
            captured = self.board[to_y][to_x]
            captured.is_player = not captured.is_player  # Change side
            captured.promoted = False  # Reset promotion status
            captured.captured = True
            
            if self.player_turn:
                self.player_captures.append(captured)
                self.player_score += self.get_piece_value(captured)
            else:
                self.ai_captures.append(captured)
                self.ai_score += self.get_piece_value(captured)
        
        # Move the piece
        if from_x is not None and from_y is not None:  # Normal move from board
            self.board[to_y][to_x] = self.board[from_y][from_x]
            self.board[from_y][from_x] = None
        else:  # Drop from captures
            if self.player_turn:
                self.board[to_y][to_x] = self.selected_piece
                self.player_captures.remove(self.selected_piece)
            else:
                self.board[to_y][to_x] = self.selected_piece
                self.ai_captures.remove(self.selected_piece)
        
        # Reset selection
        self.selected_piece = None
        self.selected_pos = None
        
        # Check for game over
        self.check_game_over()
    
    def drop_piece(self, piece, x, y):
        if self.board[y][x] is not None:
            return False
        
        # Check if it's a valid drop
        if piece.name == "Pion":
            # Check for two pawns in the same column
            for row in range(9):
                if self.board[row][x] is not None and self.board[row][x].name == "Pion" and self.board[row][x].is_player == piece.is_player:
                    self.status_label.config(text="Cannot drop Pawn in a column with another Pawn.")
                    return False
            
            # Check for dropping on the last rank
            if (piece.is_player and y == 0) or (not piece.is_player and y == 8):
                self.status_label.config(text="Cannot drop Pawn on the last rank.")
                return False
        
        # Similar restrictions for Lancer and Knight
        if piece.name == "Lancer":
            if (piece.is_player and y == 0) or (not piece.is_player and y == 8):
                self.status_label.config(text="Cannot drop Lancer on the last rank.")
                return False
        
        if piece.name == "Knight":
            if (piece.is_player and y <= 1) or (not piece.is_player and y >= 7):
                self.status_label.config(text="Cannot drop Knight on the last two ranks.")
                return False
        
        self.board[y][x] = piece
        return True
    
    def ask_promotion(self):
        result = messagebox.askyesno("Promotion", "Do you want to promote this piece?")
        if result:
            self.piece_to_promote.promote()
            self.status_label.config(text=f"{self.piece_to_promote.name} promoted!")
        
        # End player's turn regardless of promotion choice
        self.end_player_turn()

    def end_player_turn(self):
        self.player_turn = False
        self.status_label.config(text="AI's turn...")
        self.update_board_display()
        self.start_turn_timer()  # Reset the timer for AI's turn
        self.root.after(500, self.ai_move)  # Delay AI move for better UX
    
    def ai_move(self):
        # Improved AI with some basic strategies
        possible_moves = []
        
        # Check moves for pieces on the board
        for y in range(9):
            for x in range(9):
                piece = self.board[y][x]
                if piece is not None and not piece.is_player:
                    moves = piece.get_moves(self.board, x, y)
                    for to_x, to_y in moves:
                        if piece.is_valid_move(self.board, x, y, to_x, to_y):
                            # Assign a score to this move
                            score = 0
                            
                            # Higher score for capturing pieces
                            if self.board[to_y][to_x] is not None:
                                capture_value = self.get_piece_value(self.board[to_y][to_x])
                                score += capture_value * 10  # Heavily weight captures
                            
                            # Higher score for promotion
                            if piece.can_promote(y, to_y) or piece.must_promote(to_y):
                                score += 5
                            
                            # Higher score for advancing towards opponent's king
                            if piece.name != "King":  # Skip king for this strategy
                                # Find player's king position
                                king_pos = None
                                for ky in range(9):
                                    for kx in range(9):
                                        if (self.board[ky][kx] is not None and 
                                            self.board[ky][kx].name == "King" and 
                                            self.board[ky][kx].is_player):
                                            king_pos = (kx, ky)
                                            break
                                    if king_pos:
                                        break
                                
                                if king_pos:
                                    # Distance from current position to king
                                    curr_dist = abs(x - king_pos[0]) + abs(y - king_pos[1])
                                    # Distance from new position to king
                                    new_dist = abs(to_x - king_pos[0]) + abs(to_y - king_pos[1])
                                    # Reward getting closer to the king
                                    if new_dist < curr_dist:
                                        score += 3
                            
                            possible_moves.append((piece, x, y, to_x, to_y, score))
        
        # Check drop moves for captured pieces
        for piece in self.ai_captures[:]:  # Create a copy of the list to avoid modification issues
            for y in range(9):
                for x in range(9):
                    if self.board[y][x] is None:
                        # Check drop restrictions
                        if piece.name == "Pion":
                            # Check for two pawns in the same column
                            has_pawn = False
                            for row in range(9):
                                if self.board[row][x] is not None and self.board[row][x].name == "Pion" and not self.board[row][x].is_player:
                                    has_pawn = True
                                    break
                            
                            # Check for dropping on the last rank
                            if y == 8 or has_pawn:
                                continue
                        
                        elif piece.name == "Lancer" and y == 8:
                            continue
                        
                        elif piece.name == "Knight" and y >= 7:
                            continue
                        
                        # Assign a score to this drop
                        score = 2  # Base score for drops
                        
                        # Find player's king position for strategic drops
                        king_pos = None
                        for ky in range(9):
                            for kx in range(9):
                                if (self.board[ky][kx] is not None and 
                                    self.board[ky][kx].name == "King" and 
                                    self.board[ky][kx].is_player):
                                    king_pos = (kx, ky)
                                    break
                            if king_pos:
                                break
                        
                        if king_pos:
                            # Distance from drop position to king
                            dist = abs(x - king_pos[0]) + abs(y - king_pos[1])
                            # Reward drops closer to the king
                            score += max(0, (9 - dist))
                        
                        possible_moves.append((piece, None, None, x, y, score))
        
        if possible_moves:
            # Sort moves by score (highest first)
            possible_moves.sort(key=lambda m: m[5], reverse=True)
            
            # Choose one of the top 3 moves with some randomness
            top_moves = possible_moves[:3] if len(possible_moves) >= 3 else possible_moves
            piece, from_x, from_y, to_x, to_y, _ = random.choice(top_moves)
            
            self.selected_piece = piece
            self.selected_pos = (from_x, from_y)
            
            # Capture any player piece
            if self.board[to_y][to_x] is not None:
                captured = self.board[to_y][to_x]
                captured.is_player = not captured.is_player
                captured.promoted = False
                captured.captured = True
                self.ai_captures.append(captured)
                self.ai_score += self.get_piece_value(captured)
                self.status_label.config(text=f"AI captured your {captured.name}!")
            
            # Move or drop the AI piece
            if from_x is not None and from_y is not None:
                self.board[to_y][to_x] = self.board[from_y][from_x]
                self.board[from_y][from_x] = None
                
                # Check for promotion
                if piece.must_promote(to_y):
                    piece.promote()
                    self.status_label.config(text=f"AI's {piece.name} automatically promoted!")
                elif piece.can_promote(from_y, to_y):
                    # AI always promotes if beneficial
                    piece.promote()
                    self.status_label.config(text=f"AI's {piece.name} promoted!")
                else:
                    self.status_label.config(text=f"AI moved {piece.name}.")
            else:
                # Drop piece from captures - Add error handling
                self.board[to_y][to_x] = piece
                try:
                    self.ai_captures.remove(piece)
                    self.status_label.config(text=f"AI dropped {piece.name}.")
                except ValueError:
                    # Log the error but continue
                    print(f"Warning: Could not remove piece {piece.name} from AI captures, possibly already removed")
            
            # Reset selection
            self.selected_piece = None
            self.selected_pos = None
            
            # Check for game over
            self.check_game_over()
        else:
            self.status_label.config(text="AI has no legal moves!")
        
        # End AI's turn
        self.player_turn = True
        self.update_board_display()
        self.start_turn_timer()  # Reset the timer for player's turn
    
    def check_game_over(self):
        # Check if either king is captured or checkmated
        player_king_exists = False
        ai_king_exists = False
        
        for y in range(9):
            for x in range(9):
                if self.board[y][x] is not None:
                    if self.board[y][x].name == "King":
                        if self.board[y][x].is_player:
                            player_king_exists = True
                        else:
                            ai_king_exists = True
        
        if not player_king_exists:
            messagebox.showinfo("Game Over", "AI wins! Player's king is captured.")
            self.reset_game()
            return True
        
        if not ai_king_exists:
            messagebox.showinfo("Game Over", "Player wins! AI's king is captured.")
            self.reset_game()
            return True
        
        # TODO: Add checkmate detection
        
        return False
    
    def reset_game(self):
        if self.move_timer:
            self.root.after_cancel(self.move_timer)
            
        self.board = self.initialize_board()
        self.player_captures = []
        self.ai_captures = []
        self.selected_piece = None
        self.selected_pos = None
        self.player_turn = True
        self.player_score = 0
        self.ai_score = 0
        
        self.status_label.config(text="New game started. Player's turn.")
        self.update_board_display()
        self.start_turn_timer()

def main():
    root = tk.Tk()
    app = ShogiGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
