class gameboardapi:
    """
    This defines the api class to intract with the class gameboard (the application)
    """

    def __init__(self):
        pass

    def Address(self) -> str:
        """address of the player/client in str, started with 0x"""
        return ""

    def Balance(self) -> int:
        """balance of the player/client in int, in wei unit"""
        return 0
    
    def NewGame(self, amount, fee) -> dict[str, int]:
        """
        Create new game board (deploy smart contract) and join the game as player 1 if bet is greater than zero\n
        @param
            amount: amount of bet in wei
            fee:    entry fee to th game
        @return dict
            "gas_used": the gas used in the transaction
            "block_number": block number of the transaction
        """
        return {
                "gas_used": 0,
                "block_number": 0
            }
    
    def JoinGame(self, contract_addr, amount, fee) -> dict[str, int]:
        """
        Join specific game (according to smart contract address)
        @param
            amount: amount of bet in wei
            fee:    entry fee to th game
        @return dict
            "gas_used": the gas used in the transaction
            "block_number": block number of the transaction
        """
        return {
                "gas_used": 0,
                "block_number": 0
            }

    def Win(self) -> dict[str, int]:
        """
        This function is called by player which won the game. As a result, the player will recieve the bet from players
        @return dict
            "gas_used": the gas used in the transaction
            "block_number": block number of the transaction
        """
        return {
            "gas_used": 0, # in wei
            "block_number": 0
        }

    def UpdatePieces(self) -> tuple:
        """
        Obtain the information of the board, e.g. the status and position of the pieces
        @return tuple
            1. address of the board (smart contract) in str
            2. Pieces Information, please refer to solidity code
            3. Game Context, please refer to solidity code
        """
        return ("", None, None)

    def MovePieces(self, pid, r, c, cmd = 0) -> None:
        """
        Move pieces on the board and with commands. Details to be found in solidity code
        @param
            pid: piece id (int) match to enum in solidity code
            r: row to move, in range of [0,7]
            c: column to move, in range of [0,7]
            cmd: specific commands, please refer to solidity code

        """
        return None

####################################################################################
### Below definitions should match with data structure defined in the smart contract
####################################################################################
    
PIDName = ["king", "queen", "rookl", "rookr", "bishopl", "bishopr", "knightl", "knightr", "pawn1", "pawn2", "pawn3", "pawn4", "pawn5", "pawn6", "pawn7", "pawn8"]
PType = ["king", "rook", "bishop", "queen", "knight", "pawn"]

SpecCommand = {
    "Null":0, "Withdraw":1, "Pass":2, "Castle":3, "PromoteToQueen":4, "PromoteToRook":5, "PromoteToBishop":6, "PromoteToKnight":7
}

class GamePlayer:
    def __init__(self, address, state, bet) -> None:
        self.address = address
        self.state = state
        self.bet = bet

    def State(self):
        return ["Normal", "Withdraw", "Pass"][self.state]

    def StateDesc(self):
        return self.State() + " (Bet=" + str(self.bet) + " wei)"

class GameContext:
    def __init__(self, addr, p1, p2, fee, turn) -> None:
        self.address = addr
        self.player1 = GamePlayer(p1[0], p1[1], p1[2])
        self.player2 = GamePlayer(p2[0], p2[1], p2[2])
        self.fee = fee
        self.turn = turn

    def Turn(self):
        return "Black" if self.turn%2 == 0 else "White"

class GamePiece:
    def __init__(self, pid, set, ptype, row, col, alive):
        self.pid = pid
        self.set = set # 1:player1, 2:player2
        self.ptype = ptype
        self.row = row
        self.col = col
        self.alive = alive
    
    def PID(self):
        return self.pid
    
    def PieceType(self):
        return self.ptype

    def IsAt(self, r, c):
        return self.alive and self.row == r and self.col == c


def ParseBoardPieceInfo(input_arr):
    ret1 = []
    ret2 = []

    for i in range(0, 16):
        ret1.append(GamePiece(i, 1, PType[input_arr[i][1]], input_arr[i][2], input_arr[i][3], input_arr[i][4]))
    for i in range(16, 32):
        ret2.append(GamePiece(i, 2, PType[input_arr[i][1]], input_arr[i][2], input_arr[i][3], input_arr[i][4]))

    return (ret1, ret2)

def TryGetPiece(GP, r, c):
    for g in GP:
        if g.IsAt(r,c): return g
    return None
