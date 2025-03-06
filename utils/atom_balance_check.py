import requests
import pandas as pd
# Ваш публичный или локальный REST-эндпоинт для сети Cosmos
BASE_URL = "https://cosmos-rest.publicnode.com"

def get_balance(address):
    # Получаем баланс
    url = f"{BASE_URL}/cosmos/bank/v1beta1/balances/{address}"
    r = requests.get(url)
    if r.status_code != 200:
        return 0.0
    data = r.json()
    balances = data.get("balances", [])
    uatom_bal = next((b for b in balances if b["denom"] == "uatom"), None)
    if uatom_bal:
        return float(uatom_bal["amount"]) / 1_000_000
    return 0.0

def get_staked(address):
    # Получаем делегированные (стейкнутые) средства
    url = f"{BASE_URL}/cosmos/staking/v1beta1/delegations/{address}"
    r = requests.get(url)
    if r.status_code != 200:
        return 0.0
    data = r.json()
    delegations = data.get("delegation_responses", [])
    total_ua = 0.0
    for d in delegations:
        total_ua += float(d["balance"]["amount"])
    return total_ua / 1_000_000

def get_rewards(address):
    # Получаем награды за стейкинг (непретендованные)
    url = f"{BASE_URL}/cosmos/distribution/v1beta1/delegators/{address}/rewards"
    r = requests.get(url)
    if r.status_code != 200:
        return 0.0
    data = r.json()
    total = data.get("total", [])
    uatom_reward = next((r for r in total if r["denom"] == "uatom"), None)
    if uatom_reward:
        return float(uatom_reward["amount"]) / 1_000_000
    return 0.0


def get_address_data(address):
    return [address, get_balance(address), get_staked(address), get_rewards(address)]

