from brownie import (
    config,
    accounts,
    Board
)

from scripts import (
    contract_manager as ContractManager
)

from scripts.deploy import deploy_board
import ast
from . import performance

def test_deploy():
    performance.newgame()

def test_Pawn():
    performance.AllPawnMoveStep()
    performance.AllPawnMoveStep(None, 2)

def test_Knight():
    performance.KnightMoveStep()

def test_Rook():
    performance.RookMoveStep()

def test_Bishop():
    performance.BishopMoveStep()

def test_Queen():
    performance.QueenMoveStep()

def test_King():
    performance.KingMoveStep()

#TODO add exception and boundary cases