from brownie import (
    Board,
    exceptions,
    accounts,
)

import scripts.contract_manager as ContractManager
import ast

deploy_stat = []

def newgame():
    acc0 = accounts[0]
    acc1 = accounts[1]
    acc2 = accounts[2]
    b = Board.deploy({"from": acc0, "gas_price":ContractManager.get_gas_price(True)})
    deploy_stat.append(b.tx.gas_used)
    b.JoinGame(0, {"from":acc1, "value":0})
    b.JoinGame(0, {"from":acc2, "value":0})
    piecesinfo = ast.literal_eval(b.GetPiecesInfo())
    return (acc1, acc2, b, piecesinfo)

def AllPawnMoveStep(ng = None, step = 1):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    # move for all pawn
    for i in range (8,16):
        p = piecesinfo[i]
        tx = b.MovePiece(i,p[2] + step,p[3],0, {"from":acc1})
        gas_stat_black.append(tx.gas_used)
        p = piecesinfo[i+16]
        tx = b.MovePiece(i+16,p[2] - step,p[3],0, {"from":acc2})
        gas_stat_white.append(tx.gas_used)
    black = sum(gas_stat_black[1:])/(len(gas_stat_black)-1) # first move consume more so ignore
    white = sum(gas_stat_white)/len(gas_stat_white)
    return (black, white)

def KnightMoveStep(ng = None):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    b.MovePiece(8,piecesinfo[8][2] + 1,piecesinfo[8][3],0, {"from":acc1}) # dummy first move
    gas_stat_black=[]
    gas_stat_white=[]
    # init: Black knightL(6) = (0,1) knightR(7) = (0,6)
    #       White knightL(22) = (7,1) knightR(23) = (7,6)
    for (r,c) in [(2,2),(3,0),(5,1),(4,3),(5,5),(3,6),(2,4),(4,3),(2,2),(0,1)]:
        tx = b.MovePiece(22,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
        tx = b.MovePiece(6,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
    for (r,c) in [(2,5),(3,7),(5,6),(4,4),(5,2),(3,1),(2,3),(4,4),(2,5),(0,6)]:
        tx = b.MovePiece(23,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
        tx = b.MovePiece(7,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)


    return (
        sum(gas_stat_black)/len(gas_stat_black),
        sum(gas_stat_white)/len(gas_stat_white)
    )

def RookMoveStep(ng = None):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    #allow space for rook
    b.MovePiece(8,piecesinfo[8][2] + 2,piecesinfo[8][3],0, {"from":acc1}) 
    b.MovePiece(24,piecesinfo[24][2] - 2,piecesinfo[24][3],0, {"from":acc2})
    b.MovePiece(15,piecesinfo[15][2] + 2,piecesinfo[15][3],0, {"from":acc1})
    b.MovePiece(31,piecesinfo[31][2] - 2,piecesinfo[31][3],0, {"from":acc2})

    # init: Black rookL(2) = (0,0) rookR(3) = (0,7)
    #       White rookL(18) = (7,0) rookR(19) = (7,7)
    for (r,c) in [(2,0),(2,6),(3,6),(3,1),(2,1),(2,0),(0,0)]:
        tx = b.MovePiece(2,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(18,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    for (r, c) in [(2,7),(2,1),(3,1),(3,6),(2,6),(2,7),(0,7)]:
        tx = b.MovePiece(3,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(19,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    return (
        sum(gas_stat_black)/len(gas_stat_black),
        sum(gas_stat_white)/len(gas_stat_white)
    )


def BishopMoveStep(ng = None):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    #allow space for bishop
    b.MovePiece(9,piecesinfo[9][2] + 1,piecesinfo[9][3],0, {"from":acc1}) 
    b.MovePiece(25,piecesinfo[25][2] - 1,piecesinfo[25][3],0, {"from":acc2})
    b.MovePiece(14,piecesinfo[14][2] + 1,piecesinfo[14][3],0, {"from":acc1})
    b.MovePiece(30,piecesinfo[30][2] - 1,piecesinfo[30][3],0, {"from":acc2})

    # init: Black bishopL(4) = (0,2) bishopR(5) = (0,5)
    #       White bishopL(20) = (7,2) bishopR(20) = (7,5)
    for (r,c) in [(2,0),(5,3),(3,5),(2,4),(4,2),(2,0),(0,2)]:
        tx = b.MovePiece(4,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(20,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    for (r,c) in [(2,7),(5,4),(3,2),(2,3),(4,5),(2,7),(0,5)]:
        tx = b.MovePiece(5,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(21,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    
    return (
        sum(gas_stat_black)/len(gas_stat_black),
        sum(gas_stat_white)/len(gas_stat_white)
    )

def QueenMoveStep(ng = None):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    #allow space for queen
    b.MovePiece(11,piecesinfo[11][2] + 1,piecesinfo[11][3],0, {"from":acc1})
    b.MovePiece(27,piecesinfo[27][2] - 1,piecesinfo[27][3],0, {"from":acc2})
    # init: Black Queen(1) = (0,2) White Queen(17) = (7,2)
    for (r,c) in [(1,3),(2,2),(5,5),(3,7),(2,6),(4,4),(2,2),(2,1),(3,2),(2,2),(3,1),(3,2)]:
        tx = b.MovePiece(1,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(17,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    return (
        sum(gas_stat_black)/len(gas_stat_black),
        sum(gas_stat_white)/len(gas_stat_white)
    )

def KingMoveStep(ng = None):
    (acc1, acc2, b, piecesinfo) = newgame() if ng is None else ng
    gas_stat_black = []
    gas_stat_white = []
    #allow space for king
    b.MovePiece(12,piecesinfo[12][2] + 2,piecesinfo[12][3],0, {"from":acc1})
    b.MovePiece(28,piecesinfo[28][2] - 2,piecesinfo[28][3],0, {"from":acc2})
    # init: Black King(0) = (0,2) White King(16) = (7,2)
    for (r,c) in [(1,4),(2,4),(2,3),(3,3),(2,3),(2,4)]:
        tx = b.MovePiece(0,r,c,0,{"from":acc1})
        gas_stat_black.append(tx.gas_used)
        tx = b.MovePiece(16,7-r,c,0,{"from":acc2})
        gas_stat_white.append(tx.gas_used)
    return (
        sum(gas_stat_black)/len(gas_stat_black),
        sum(gas_stat_white)/len(gas_stat_white)
    )
