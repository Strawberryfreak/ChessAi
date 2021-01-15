"""
Alle informatie wordt hierna toe gebracht over wat is op het bord. Ook kijkt hij of de spelers de regels aanhoudt.
 En hij houdt een move log bij.
"""
class GameState():
    def __init__(self):
        #dit is onze 2d bord.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]







    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can do undo it later
        self.whiteToMove = not self.whiteToMove #swap players

        #update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn

        #update enpassant variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook

            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves the rook
                self.board[move.endRow][move.endCol-2] = '--'


        #update castling rights - whenever is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))





    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
                move = self.moveLog.pop()
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.whiteToMove = not self.whiteToMove #switch turns back
                #update the king's position if needed
                if move.pieceMoved == "wK":
                    self.whiteKingLocation = (move.startRow, move.startCol)
                elif move.pieceMoved == "bK":
                    self.blackKingLocation = (move.startRow, move.startCol)
                #undo enpassant move
                if move.isEnpassantMove:
                    self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                    self.board[move.startRow][move.endCol] = move.pieceCaptured
                    self.enpassantPossible = (move.endRow, move.endCol)
                 #undo a 2 swuare pawn advance
                if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                    self.enpassantPossible = ()

                #undo castling rights
                self.castleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
                newRights = self.castleRightsLog[-1]
                self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

                #undo the castle move
                if move.isCastleMove:
                    if move.endCol - move.startCol == 2: #kingside
                        self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                        self.board[move.endRow][move.endCol-1] = '--'
                    else: #queenside
                        self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                        self.board[move.endRow][move.endCol+1] = '--'


    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False




    '''
    All moves considering checks. This function wil check if the player can do this move, is the other player pinning the check? He generate the possible moves from the oppenent and look if thats a check.
    '''

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1.  ) generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2. ) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list go backwards through that list
            self.makeMove(moves[i])
            # 3. ) generate all oppnent's moves
            # 4. ) for each of your opponent's moves, see if they attack your
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5. ) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderattack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderattack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy attack the square r, c
    '''

    def squareUnderattack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to oppenent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False


    '''
    All moves without considering checks. All the possible moves that are legal to move. No need to worry about checks and pinning etc.
    '''

    def getAllPossibleMoves(self):
        moves = [] #create a list of the pieces on the currentstate of the board.
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based

        return moves


    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawns moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == "b": #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == "b": #enemy to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))


        else: #black pawn moves
                if self.board[r+1][c] == "--": #1 square pawn advance
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  #2 square pawn advance
                        moves.append(Move((r, c), (r+2, c), self.board))
                if c-1 >= 0:  # captures to the left
                    if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                    elif (r+1, c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
                if c+1 <= 7:  # captures to the right
                    if self.board[r+1][c+1][0] == 'w':  # enemy to capture
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                    elif (r+1, c+1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))




    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down , right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #friendly piece invalid
                        break
                else: #off  board
                    break
    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1,-2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece( empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    '''
    Get all the Bishop moves for the Bishop located at row, col and add these moves to the list
    '''

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #4 diaganols
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #friendly piece invalid
                        break
                else: #off  board
                    break






    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (1, -1), (0, 1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece( empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))



    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderattack(r, c):
            return #can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)



    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderattack(r, c+1) and not self.squareUnderattack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))



    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderattack(r, c-1) and not self.squareUnderattack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


       #wat wil ik met deze ai: Deze ai doet random moves. Hij capture al de pieces die hij krijgen.
   # def ChessAi(self, r, c,moves):

        #pion naar voren elke zet.
        #stap 1 Selecteer de linker pion.
        #self.selectPion = 'bp' in (c, 1)
        #stap 2: krijg de functie van dat pion.
        #self.getPawnMoves()
        #stap 3: Move die pion naar voren.
        #if self.board[r-1][c] == "--":
         #   moves.append(Move((r, c), (r - 1, c), self.board))

        #self.whiteToMove = True


    #def chessAIMove(self, r, c):
       # self.selectPion
        #pass










class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move():
    #maps keys to values
    # key : value
    ranksToRows = { "1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        #castle move
        self.isCastleMove = isCastleMove


        self.moveID = self.startRow * 1000 + self.startCol * 1000 + self.endRow * 10 + self.endCol


    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        #you can add to make this real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]