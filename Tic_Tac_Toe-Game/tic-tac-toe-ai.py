import tkinter as tk
import math

# Initialize the board
board = [[" " for _ in range(3)] for _ in range(3)]

# Check winner
def check_winner(b):
    # Rows, Cols
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
    if winner == "O": return 1
    if winner == "X": return -1
    if not is_moves_left(b): return 0

    if is_maximizing:
        best = -math.inf
        for i in range(3):
            for j in range(3):
                if b[i][j] == " ":
                    b[i][j] = "O"
                    score = minimax(b, depth+1, False)
                    b[i][j] = " "
                    best = max(best, score)
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if b[i][j] == " ":
                    b[i][j] = "X"
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
                board[i][j] = "O"
                score = minimax(board, 0, False)
                board[i][j] = " "
                if score > best_score:
                    best_score = score
                    move = (i, j)
    if move:
        board[move[0]][move[1]] = "O"
        buttons[move[0]][move[1]].config(text="O", fg="blue", state="disabled")
        check_game_status()

# Check status
def check_game_status():
    winner = check_winner(board)
    if winner:
        if winner == "X":
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
        board[i][j] = "X"
        buttons[i][j].config(text="X", fg="red", state="disabled")
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
    label.config(text="You: X   |   AI: O", fg="black")

# GUI Setup
root = tk.Tk()
root.title("Tic Tac Toe AI 🎮")
root.config(bg="#f0f0f0")

label = tk.Label(root, text="You: X   |   AI: O", font=("Arial", 16, "bold"), bg="#f0f0f0")
label.pack(pady=10)

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack()

buttons = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(frame, text=" ", font=("Arial", 24, "bold"), width=5, height=2,
                                  relief="ridge", bg="white",
                                  command=lambda i=i, j=j: player_move(i, j))
        buttons[i][j].grid(row=i, column=j, padx=5, pady=5)

restart_btn = tk.Button(root, text="🔄 Restart", font=("Arial", 14, "bold"),
                        bg="#4CAF50", fg="white", relief="raised", command=restart)
restart_btn.pack(pady=10)

root.mainloop()
