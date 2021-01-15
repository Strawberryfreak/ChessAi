"""
Dit is onze main file. Hij is responsible for user input and displaying the current gamestate.
"""

import pygame as p
from Chess import ChessEngine, SmartMoveFinder


WIDTH = HEIGHT = 512 #400 is een andere optie
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
initialize a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['bB', 'bK', 'bN', 'bp', 'bQ', 'bR','wB', 'wK', 'wN', 'wp', 'wQ', 'wR']
    for piece in pieces:
        IMAGES[piece] = p.image.load("images/"+ piece +".png")



    '''
    The main driver for our code. This will handle user input and update graphics
    '''
def main():
     p.init()
     screen = p.display.set_mode((WIDTH,HEIGHT))
     clock = p.time.Clock()
     screen.fill(p.Color("white"))
     gs = ChessEngine.GameState()
     validMoves = gs.getValidMoves()
     moveMade = False #flag variable for when a move is made
     animate = False
     loadImages()
     running = True
     sqSelected = () #no squere is selected, keep track of the last click of the user.
     playerClicks = [] #keep track of player clicks
     gameOver = False
     playerOne = True #if a human is playing white, then this wilb e True. If an AI is playing, then its false
     playerTwo = False #same as above but for black
     while running:
         humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
         for e in p.event.get():
             if e.type == p.QUIT:
                 running = False
             #mouse handler
             elif e.type == p.MOUSEBUTTONDOWN:
                 if not gameOver and humanTurn:
                     location = p.mouse.get_pos() #(x,y) location of mouse
                     col = location[0]//SQ_SIZE
                     row = location[1]//SQ_SIZE
                     if sqSelected == (row,col): #the user clicked the same squere twice
                         sqSelected = () #deselect
                         playerClicks = [] #clear player clicks
                     else :
                         sqSelected = (row, col)
                         playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                     if len(playerClicks) == 2: #after 2nd click
                         move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                         print(move.getChessNotation())
                         for i in range(len(validMoves)):
                             if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                         if not moveMade:
                            playerClicks = [sqSelected]


             #key handlers
             elif e.type == p.KEYDOWN:
                 if e.key == p.K_z: #undo when 'z' is pressed
                     gs.undoMove()
                     moveMade = True
                     animate = False
                 if e.key == p.K_r:#reset the board 'r' is pressed
                     gs = ChessEngine.GameState()
                     validMoves = gs.getValidMoves()
                     sqSelected = ()
                     playerClicks = []
                     moveMade = False
                     animate = False


    #Ai move finder
         if not gameOver and not humanTurn:
             AIMove = SmartMoveFinder.findRandomMove(validMoves)
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
             gameOver = True
             if gs.whiteToMove:
                 drawText(screen, 'Black wins by checkmate')
             else:
                 drawText(screen, 'White wins by checkmate')
         elif gs.staleMate:
             gameOver = True
             drawText(screen, 'Stalemate')
         clock.tick(MAX_FPS)
         p.display.flip()

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparance value - > 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))









def drawGameState(screen, gs, validMoves, sqSelected):
     drawBoard(screen) #draw squares on the board
     highlightSquares(screen, gs, validMoves, sqSelected)
     drawPieces(screen, gs.board) #draw pieces on top of those squares

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
           color = colors [((r+c) % 2)]
           p.draw.rect(screen, color, p.Rect(r*SQ_SIZE,c*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
animating  a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10 # frames
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC * frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Blue'))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)





if __name__ == "__main__":
    main()
