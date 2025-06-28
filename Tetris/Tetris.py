from flask import Flask, render_template, jsonify, request
import random
import time

app = Flask(__name__)

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
PIECES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

board = []
score = 0
current_piece = None
current_x = 0
current_y = 0


def reset_game():
    global board, score, current_piece, current_x, current_y
    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    score = 0
    current_piece = None
    current_x = 0
    current_y = 0


def rotate_piece(piece):
    return [list(reversed(col)) for col in zip(*piece)]


def can_place_piece(board, piece, x, y):
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == 1:
                if (
                    y + i >= BOARD_HEIGHT or
                    x + j < 0 or
                    x + j >= BOARD_WIDTH or
                    board[y + i][x + j] == 1
                ):
                    return False
    return True


def place_piece(board, piece, x, y):
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == 1:
                board[y + i][x + j] = 1


def add_current_piece_to_board(board, piece, x, y):
    temp_board = [row[:] for row in board]
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == 1:
                temp_board[y + i][x + j] = 1
    return temp_board


def clear_lines(board):
    lines_cleared = 0
    for y in range(BOARD_HEIGHT - 1, -1, -1):
        if all(board[y]):
            del board[y]
            board.insert(0, [0] * BOARD_WIDTH)
            lines_cleared += 1
    return lines_cleared


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_game():
    reset_game()
    return jsonify({'board': board, 'score': score})


@app.route('/control', methods=['POST'])
def control_action():
    global board, score, current_piece, current_x, current_y

    action = request.args.get('action', '')

    if current_piece is None:
        current_piece = random.choice(PIECES)
        current_x = BOARD_WIDTH // 2 - len(current_piece[0]) // 2
        current_y = 0

        if not can_place_piece(board, current_piece, current_x, current_y):
            return jsonify({'board': board, 'score': score, 'game_over': True})

    if action == 'left' and can_place_piece(board, current_piece, current_x - 1, current_y):
        current_x -= 1
    elif action == 'right' and can_place_piece(board, current_piece, current_x + 1, current_y):
        current_x += 1
    elif action == 'rotate':
        rotated = rotate_piece(current_piece)
        if can_place_piece(board, rotated, current_x, current_y):
            current_piece = rotated
    elif action == 'drop':
        while can_place_piece(board, current_piece, current_x, current_y + 1):
            current_y += 1
    elif action == 'tick':
        if can_place_piece(board, current_piece, current_x, current_y + 1):
            current_y += 1
        else:
            place_piece(board, current_piece, current_x, current_y)
            lines_cleared = clear_lines(board)
            score += lines_cleared * 10
            current_piece = None

    temp_board = add_current_piece_to_board(board, current_piece, current_x, current_y) if current_piece else board
    return jsonify({'board': temp_board, 'score': score, 'game_over': False})


if __name__ == '__main__':
    app.run(debug=True)
