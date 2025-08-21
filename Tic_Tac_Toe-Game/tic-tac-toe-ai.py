import tkinter as tk
import math

# Initialize board
board = [[" " for _ in range(3)] for _ in range(3)]
user_symbol = "X"
ai_symbol = "O"

# Check winner
def check_winner(b):
    # Rows & Cols
    for row in b:
        if row.count(row[0]) == 3 and row[0] != " ":
            return row[0]
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] != " ":
            return b[0][col]
    # Diagonals
    if b[0][0] == b[1][1] == b[2][2] != " ":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != " ":
        return b[0][2]
    return None

def is_moves_left(b):
    return any(" " in row for row in b)

# Minimax Algorithm
def minimax(b, depth, is_maximizing):
    winner = check_winner(b)
    if winner == ai_symbol: return 1
    if winner == user_symbol: return -1
    if not is_moves_left(b): return 0

    if is_maximizing:
        best = -math.inf
        for i in range(3):
            for j in range(3):
                if b[i][j] == " ":
                    b[i][j] = ai_symbol
                    score = minimax(b, depth+1, False)
                    b[i][j] = " "
                    best = max(best, score)
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if b[i][j] == " ":
                    b[i][j] = user_symbol
                    score = minimax(b, depth+1, True)
                    b[i][j] = " "
                    best = min(best, score)
        return best

# AI Move
def ai_move():
    best_score = -math.inf
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = ai_symbol
                score = minimax(board, 0, False)
                board[i][j] = " "
                if score > best_score:
                    best_score = score
                    move = (i, j)
    if move:
        board[move[0]][move[1]] = ai_symbol
        buttons[move[0]][move[1]].config(
            text=ai_symbol,
            fg="blue" if ai_symbol == "O" else "red",
            state="disabled"
        )
        check_game_status()

# Check status
def check_game_status():
    winner = check_winner(board)
    if winner:
        if winner == user_symbol:
            label.config(text="🎉 You Win!", fg="green")
        else:
            label.config(text="😎 AI Wins!", fg="red")
        disable_all()
    elif not is_moves_left(board):
        label.config(text="🤝 It's a Draw", fg="orange")
        disable_all()

def disable_all():
    for row in buttons:
        for btn in row:
            btn.config(state="disabled")

# Player Move
def player_move(i, j):
    if board[i][j] == " ":
        board[i][j] = user_symbol
        buttons[i][j].config(
            text=user_symbol,
            fg="red" if user_symbol == "X" else "blue",
            state="disabled"
        )
        check_game_status()
        if is_moves_left(board) and not check_winner(board):
            ai_move()

# Restart Game
def restart():
    global board
    board = [[" " for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text=" ", state="normal", fg="black")
    label.config(text=f"You: {user_symbol}   |   AI: {ai_symbol}", fg="black")
    # If AI goes first
    if user_symbol == "O":
        ai_move()

# Choose Symbol
def choose_symbol(symbol):
    global user_symbol, ai_symbol
    user_symbol = symbol
    ai_symbol = "O" if user_symbol == "X" else "X"
    label.config(text=f"You: {user_symbol}   |   AI: {ai_symbol}", fg="black")
    choice_frame.pack_forget()  # hide choice buttons
    frame.pack()
    restart_btn.pack(pady=10)
    if user_symbol == "O":  # AI plays first
        ai_move()

# GUI Setup
root = tk.Tk()
root.title("Tic Tac Toe AI 🎮")
root.config(bg="#f0f0f0")

label = tk.Label(root, text="Choose X or O to start", font=("Arial", 16, "bold"), bg="#f0f0f0")
label.pack(pady=10)

# Choice buttons
choice_frame = tk.Frame(root, bg="#f0f0f0")
choice_frame.pack()
tk.Button(choice_frame, text="Play as X", font=("Arial", 14), bg="#FF5555", fg="white",
          command=lambda: choose_symbol("X")).pack(side="left", padx=10)
tk.Button(choice_frame, text="Play as O", font=("Arial", 14), bg="#5555FF", fg="white",
          command=lambda: choose_symbol("O")).pack(side="left", padx=10)

# Board buttons
frame = tk.Frame(root, bg="#f0f0f0")
buttons = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(frame, text=" ", font=("Arial", 24, "bold"), width=5, height=2,
                                  relief="ridge", bg="white",
                                  command=lambda i=i, j=j: player_move(i, j))
        buttons[i][j].grid(row=i, column=j, padx=5, pady=5)

restart_btn = tk.Button(root, text="🔄 Restart", font=("Arial", 14, "bold"),
                        bg="#4CAF50", fg="white", relief="raised", command=restart)

root.mainloop()
