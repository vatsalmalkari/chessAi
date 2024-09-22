import random

scores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
positional_scores = {
    "p": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
        [0.5, 1, 1, -2, -2, 1, 1, 0.5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    "N": [
        [-5, -4, -3, -3, -3, -3, -4, -5],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
        [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
        [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
        [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
        [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
        [-5, -4, -3, -3, -3, -3, -4, -5]
    ],
    # Add positional scores for bishops, rooks, queens, and king as well
}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    # Adjust the depth dynamically based on game stage
    if len(gs.moveLog) > 40:  # Mid or Endgame
        searchDepth = 4  # Increase depth in the endgame
    else:
        searchDepth = DEPTH
    findMoveNegaMaxAlphaBeta(gs, validMoves, searchDepth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(f"Evaluated {counter} positions")
    return nextMove


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # Move ordering: prioritize captures and checks
    validMoves.sort(key=lambda move: 1 if move.pieceCaptured != '--' else 0, reverse=True)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square != "--":
                piecePositionScore = 0
                if square[1] in positional_scores:
                    piecePositionScore = positional_scores[square[1]][gs.board.index(row)][row.index(square)]
                if square[0] == 'w':
                    score += scores[square[1]] + piecePositionScore
                elif square[0] == 'b':
                    score -= scores[square[1]] + piecePositionScore
    return score


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += scores[square[1]]
            elif square[0] == 'b':
                score -= scores[square[1]]
    return score
