import pytest
from Tetris.Tetris import app, reset_game, rotate_piece, can_place_piece, place_piece, clear_lines

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_start_game(client):
    response = client.post('/start')
    assert response.status_code == 200
    data = response.get_json()
    assert 'board' in data
    assert 'score' in data
    assert data['score'] == 0

def test_rotate_piece():
    piece = [[1, 1, 1], [0, 1, 0]]
    rotated = rotate_piece(piece)
    assert rotated == [[0, 1], [1, 1], [0, 1]]

def test_can_place_piece():
    board = [[0 for _ in range(10)] for _ in range(20)]
    piece = [[1, 1], [1, 1]]
    assert can_place_piece(board, piece, 0, 0) == True
    assert can_place_piece(board, piece, -1, 0) == False
    assert can_place_piece(board, piece, 9, 0) == False

def test_place_piece():
    board = [[0 for _ in range(10)] for _ in range(20)]
    piece = [[1, 1], [1, 1]]
    place_piece(board, piece, 0, 0)
    assert board[0][0] == 1
    assert board[0][1] == 1
    assert board[1][0] == 1
    assert board[1][1] == 1

def test_clear_lines():
    board = [[0 for _ in range(10)] for _ in range(20)]
    # Fill a row completely
    board[19] = [1 for _ in range(10)]
    lines_cleared = clear_lines(board)
    assert lines_cleared == 1
    assert all(cell == 0 for cell in board[0])