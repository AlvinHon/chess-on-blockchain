from brownie import (
    Board,
    config
)


from scripts import (
    contract_manager as ContractManager
)

def deploy_board(acc=None) -> Board:
    """
    Deploy smart contract "Board"
    @param
        acc: specific account, if None, use local account
    @return
        board (smart contract)
    """
    account = acc if acc is not None else ContractManager.get_account()
    return Board.deploy({"from": account, "gas_price":ContractManager.get_gas_price(True)})

def main():
    deploy_board()