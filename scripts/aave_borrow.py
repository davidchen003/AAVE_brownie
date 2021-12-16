from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")  # 0.1 ETH


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()

    # Approve sending our ERC20 token
    approve_tx = approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    print("Depositing...")

    # Deposit money to AAVE
    tx = lending_pool.deposit(
        erc20_address,
        AMOUNT,
        account.address,
        0,
        {"from": account},  # 0 is for referralCode, deprecated.
    )
    tx.wait(1)
    print("Deposited!")


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx
