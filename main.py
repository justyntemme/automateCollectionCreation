import json
import logging
import os
from typing import Tuple, List

import requests

logging.basicConfig(level=logging.INFO)

# Global Variables
n = None  # To shorten line lengths
TL_URL = os.environ.get("TL_URL")
PC_URL = os.environ.get("PC_URL")
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


def generate_cwp_token(access_key: str, access_secret: str) -> Tuple[int, str]:
    auth_url = f"{TL_URL}/api/v1/authenticate" if TL_URL is not n else exit(1)

    headers = {
        "accept": "application/json; charset=UTF-8",
        "content-type": "application/json",
    }
    body = {"username": access_key, "password": access_secret}
    response = requests.post(
        auth_url, headers=headers, json=body, timeout=60, verify=False
    )

    if response.status_code == 200:
        data = json.loads(response.text)
        logging.info("Token acquired")
        return 200, data["token"]
    else:
        logging.error(
            "Unable to acquire token with error code: %s", response.status_code
        )

    return response.status_code, ""


def check_param(param_name: str) -> str:
    param_value = os.environ.get(param_name)
    if param_value is None:
        logging.error(f"Missing {param_name}")
        raise ValueError(f"Missing {param_name}")
    return param_value


def main():
    P: Tuple[str, str, str] = ("PC_IDENTITY", "PC_SECRET", "TL_URL")
    access_key, access_secret, _ = map(check_param, P)
    response_code, cwp_token = (
        generate_cwp_token(access_key, access_secret)
        if access_key and access_secret
        else (None, None)
    )

    if response_code != 200 or not cwp_token:
        logging.error("Failed to acquire token")
        exit(1)

    try:
        with open(HOSTS_FILE, "r") as file:
            hosts = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"{HOSTS_FILE} not found")
        exit(1)

    for i in range(0, len(hosts), BATCH_SIZE):
        batch_hosts = hosts[i : i + BATCH_SIZE]
        collection_name = f"defenderupdatecollection{i // BATCH_SIZE + 1}"
        response_code, response_text = create_collection(
            cwp_token, collection_name, batch_hosts
        )
        if response_code == 200:
            logging.info(f"Successfully created collection: {collection_name}")
        else:
            logging.error(
                f"Failed to create collection: {collection_name}, Status Code: {response_code}, Response: {response_text}"
            )


if __name__ == "__main__":
    main()
