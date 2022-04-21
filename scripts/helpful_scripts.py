from brownie import (
    network,
    accounts,
    config,
    interface,
    MockV3Aggregator,
    Contract,
    web3,
    chain,
)
import os
import time

# Set a default gas price
from brownie.network import priority_fee

OPENSEA_FORMAT = "https://testnets.opensea.io/assets/{}/{}"
NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None

def get_publish_source():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or not os.getenv(
        "ETHERSCAN_TOKEN"
    ):
        return False
    else:
        return True

def get_icon_name(iconNumber):
    switch = {0: "cartman", 1: "homer", 2: "ironman", 3: "panda", 4: "kyle", 5: "stan", 6: "mario", 7: "walter"}
    return switch[iconNumber]


def get_verify_status():
    verify = (
        config["networks"][network.show_active()]["verify"]
        if config["networks"][network.show_active()].get("verify")
        else False
    )
    return verify
