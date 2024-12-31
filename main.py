import json
import logging
import os
from typing import Tuple, List

import requests

logging.basicConfig(level=logging.INFO)

# Global Variables
n = None  # To shorten line lengths
HOSTS_FILE = "hosts.txt"
BATCH_SIZE = 1000


def create_collection(
    token: str, collection_name: str, hosts: List[str]
) -> Tuple[int, str]:
    collection_url = f"{TL_URL}/api/v1/collections"
    headers = {
        "accept": "application/json; charset=UTF-8",
        "content-type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"name": collection_name, "hosts": hosts}
    response = requests.post(
        collection_url, headers=headers, json=payload, timeout=60, verify=False
    )
    return response.status_code, response.text

def main():


    try:
        with open(HOSTS_FILE, "r") as file:
            hosts = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"{HOSTS_FILE} not found")
        exit(1)

    for i in range(0, len(hosts), BATCH_SIZE):
        batch_hosts = hosts[i : i + BATCH_SIZE]
        collection_name = f"defender-update-collection-{i // BATCH_SIZE + 1}"
        response_code, response_text = create_collection(
            "TODO REPLACE ME WITH TOKEN", collection_name, batch_hosts
        )
        if response_code == 200:
            logging.info(f"Successfully created collection: {collection_name}")
        else:
            logging.error(
                f"Failed to create collection: {collection_name}, Status Code: {response_code}, Response: {response_text}"
            )


if __name__ == "__main__":
    main()
