"""
Contains helper functions related the smart contract
"""

from brownie import (
    accounts,
    network,
    config,
    Contract
)

import random
import brownie.network.gas.strategies as gas_strategy

def get_account():
    # Local account only
    return accounts[random.randint(0, len(accounts)-1)]

def get_contract(contract_name_str,contract_name, contract_abi, contract_address):
    # Use compile contract
    return Contract.from_abi(
            contract_name, contract_address, contract_abi
        )

def get_gas_price(deploy=False):    
    if deploy:
        return gas_strategy.LinearScalingStrategy(
            config["limits"]["gas_limit_deploy"]["min"],
            config["limits"]["gas_limit_deploy"]["max"],
            1.1)
    else :
        return gas_strategy.LinearScalingStrategy(
            config["limits"]["gas_limit_tx"]["min"],
            config["limits"]["gas_limit_tx"]["max"],
            1.1)

def set_default_gas_price():
    network.gas_price(get_gas_price(False))