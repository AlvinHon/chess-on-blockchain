from brownie import (
    Board,
    exceptions
)
from scripts.deploy import deploy_board
from scripts.gameboard import gameboard as GameBoard
from scripts.gameboard import gameboardapi as GameBoardAPI
import scripts.contract_manager as ContractManager
import ast

class ChessGameAPI (GameBoardAPI.gameboardapi):
    """
    This class overide the API gameboardapi to interact with the application by implementing the \
    logics of smart contract.\n
    Please see the class on details of the API description.
    """
    def __init__(self):
        self.__account = ContractManager.get_account()
    
    def Address(self):
        return self.__account.address

    def Balance(self):
        return self.__account.balance()

    def NewGame(self, amount=0, fee=0):
        self.__board = deploy_board(self.__account)
        gs = self.__board.tx.gas_used
        bn = self.__board.tx.block_number
        if amount > 0:
            try:
                txinfo = self.__board.JoinGame(fee, {"from":self.__account, "value": amount})
                gs += txinfo.gas_used
                bn = txinfo.block_number
            except exceptions.VirtualMachineError as e:
                raise Exception(e.revert_msg)
        return {
                "gas_used": gs, # in wei
                "block_number": bn
            }
    
    def JoinGame(self, contract_addr, amount=0, fee=0):
        gs, bn = 0, 0
        try:
            self.__board = ContractManager.get_contract("Board", Board._name, Board.abi, contract_addr)
            ctx = self.__board.ctx()
            print(ctx[0][0], ctx[1][0], self.__account.address)
            if ctx[0][0] == str(self.__account.address) or ctx[1][0] == str(self.__account.address):
                gs, bn = 0, 0
            else:
                fee = amount if ctx[0][0] == str(self.__account.address) else ctx[2]
                txinfo = self.__board.JoinGame(fee, {"from":self.__account, "value": ctx[2]})
                gs, bn = txinfo.gas_used, txinfo.block_number
        except exceptions.VirtualMachineError as e:
            raise Exception(e.revert_msg)
        return {
            "gas_used": gs,
            "block_number": bn
        }

    def Win(self):
        gs, bn = 0, 0
        try:
            txinfo = self.__board.Win({"from":self.__account})
            gs, bn = txinfo.gas_used, txinfo.block_number
        except exceptions.VirtualMachineError as e:
            print (e)
            raise Exception(e.revert_msg)
        return {
            "gas_used": gs, # in wei
            "block_number": bn
        }

    def UpdatePieces(self):
        ctx = self.__board.ctx()
        piecesinfo = ast.literal_eval(self.__board.GetPiecesInfo())
        return (self.__board.address, piecesinfo, ctx)
    
    def MovePieces(self, pid, r, c, cmd = 0):
        try:
            txn_getinfo = self.__board.MovePiece(pid,r,c,cmd, {"from":self.__account})
            #txn_getinfo.wait(1)
            return {
                "gas_used": txn_getinfo.gas_used, # in wei
                "block_number": txn_getinfo.block_number
            }
        except exceptions.VirtualMachineError as e:
            print(e)
            raise Exception(e.revert_msg)
        return None
    
def main():
    gameapi = ChessGameAPI()
    menu = GameBoard.GameMenu(gameapi)
    menu.mainLoop()