#!/usr/bin/python3
import os
import requests
import json
from brownie import NFTDemo, accounts, network, config
from scripts.helpful_scripts import OPENSEA_FORMAT, get_publish_source, get_icon_name
from os import listdir
from os.path import isfile
from metadata import sample_metadata
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
icon_metadata_dic = {}

def create_nfts(dev, nft_contract):
    for f in listdir('img'):
        if isfile:
            token_id = nft_contract.tokenCounter()
            transaction = nft_contract.createCollectible("None", {"from": dev})
            transaction.wait(1)

    print(f"A total of {nft_contract.tokenCounter()} NFTs were created")

def get_metadata_file_name(token_id):
    return (
            "./metadata/{}/".format(network.show_active())
            + str(token_id)
            + "-"
            + get_icon_name(token_id)
            + ".json"
        )
def write_metadata(nft_contract):
    for token_id in range(nft_contract.tokenCounter()):
        collectible_metadata = sample_metadata.metadata_template
        metadata_file_name = get_metadata_file_name(token_id)
        if Path(metadata_file_name).exists():
            print(
                "{} already found, delete it to overwrite!".format(
                    metadata_file_name)
            )
        else:
            print("Creating Metadata file: " + metadata_file_name)
            collectible_metadata["name"] = get_icon_name(token_id)

            collectible_metadata["description"] = "ICON! {}".format(
                collectible_metadata["name"]
            )
            image_to_upload = None
            if os.getenv("UPLOAD_IPFS") == "true":
                image_path = f"./img/{token_id+1}.png"
                image_to_upload = upload_to_ipfs(image_path)

            collectible_metadata["image"] = image_to_upload
            with open(metadata_file_name, "w") as file:
                json.dump(collectible_metadata, file)
            if os.getenv("UPLOAD_IPFS") == "true":
                icon_metadata_dic[token_id] = upload_to_ipfs(metadata_file_name)

def upload_to_ipfs(filepath):
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        ipfs_url = (
            os.getenv("IPFS_URL")
            if os.getenv("IPFS_URL")
            else "http://localhost:5001"
        )
        response = requests.post(ipfs_url + "/api/v0/add",
                                 files={"file": image_binary})
        ipfs_hash = response.json()["Hash"]
        filename = filepath.split("/")[-1:][0]
        image_uri = "http://ipfs.io/ipfs/{}?filename={}".format(
            ipfs_hash, filename)
    return image_uri

def get_tokenURI_from_id(token_id):

    metadata_file_name = get_metadata_file_name(token_id)
    if Path(metadata_file_name).exists():
        metadata_file = open(metadata_file_name)
        nft_metadata = json.load(metadata_file)
        return nft_metadata['image']

def set_tokenURI(dev, nft_contract):
    for token_id in range(nft_contract.tokenCounter()):
        if not nft_contract.tokenURI(token_id).startswith("https://"):
            nft_contract.setTokenURI(token_id, icon_metadata_dic[token_id], {"from": dev})
            print(
                "Awesome! You can view your NFT at {}".format(
                OPENSEA_FORMAT.format(nft_contract.address, token_id)
                )
            )
            print('Please give up to 20 minutes, and hit the "refresh metadata" button')

        else:
            print("Skipping {}, we already set that tokenURI!".format(token_id))

def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    NFTDemo.deploy({"from": dev}, publish_source=get_publish_source())
    nft_demo = NFTDemo[len(NFTDemo) - 1]
    create_nfts(dev, nft_demo)
    write_metadata(nft_demo)
    set_tokenURI(dev, nft_demo)
