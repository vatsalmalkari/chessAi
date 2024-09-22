import pygame as p
from Chess import ChessEngine, CoolMove

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION  # Use integer division
MAX_FPS = 15
IMAGES = {}
p.init()

def loadimages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
            print(f"Loaded {piece} successfully")
        except Exception as e:
            print(f"Failed to load {piece}: {e}")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadimages()
    running = True
    sqSelected = ()
    playerClicks = []
    promotionPending = False  # Track if promotion is pending
    promotionMove = None  # Store the move that needs promotion
    gameEnd = False
    playerWhite = False  # human is white then it is true, if ai is white then its false
    playerBlack = True  # same as above for black

    while running:
        humanTurn = (gs.whiteToMove and playerWhite) or (not gs.whiteToMove and playerBlack)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN and not promotionPending:
                if not gameEnd and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # Deselect when clicking the same square twice
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                        if len(playerClicks) == 2:  # After 2nd click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            print(move.getChessNotation())
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    animate = True
                                    if move.isPromotion:  # Check if the move is a pawn promotion
                                        promotionPending = True
                                        promotionMove = move  # Store the move to update after choosing a piece
                                    sqSelected = ()
                                    playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if promotionPending:
                    if e.key == p.K_UP:
                        promotionMove.promotionChoice = 'Q'  # Promote to Queen
                    elif e.key == p.K_LEFT:
                        promotionMove.promotionChoice = 'B'  # Promote to Bishop
                    elif e.key == p.K_RIGHT:
                        promotionMove.promotionChoice = 'N'  # Promote to Knight
                    elif e.key == p.K_DOWN:
                        promotionMove.promotionChoice = 'R'  # Promote to Rook
                    # Update the board with the chosen piece
                    gs.board[promotionMove.endRow][promotionMove.endCol] = promotionMove.pieceMoved[0] + promotionMove.promotionChoice
                    promotionPending = False  # Promotion is complete, so reset flag
                    promotionMove = None
                    moveMade = True
                    animate = True

                elif e.key == p.K_BACKSPACE:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameEnd = False

                elif e.key == p.K_ESCAPE:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    promotionPending = False
                    promotionMove = None
                    gameEnd = False

        if not gameEnd and not humanTurn and not promotionPending:
            AIMove = CoolMove.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = CoolMove.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameEnd = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins')
            else:
                drawText(screen, 'White wins')

        elif gs.staleMate:
            gameEnd = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def drawboard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawboard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    fps = 10
    frameCount = (abs(dR) + abs(dC)) * fps
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawboard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Draw the captured piece back if one exists
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw the piece that is being animated
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 50, True, False)
    textObject = font.render(text, 0, p.Color('Yellow'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Purple'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
