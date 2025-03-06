import pandas as pd
import asyncio
from web3 import Web3
import configparser
from utils.get_config_path import config_path

async def get_eth_balance_async(loop, web3, address):
    try:
        if web3:
            balance_wei = await loop.run_in_executor(None, web3.eth.get_balance, address)
            balance_eth = round(web3.from_wei(balance_wei, 'ether'), 5)
            return balance_eth
        return '-'
    except Exception as e:
        return f"Ошибка при получении баланса: {e}"

async def process_address(address, loop, connections):
    tasks = [
        get_eth_balance_async(loop, connections['ethereum'], address),
        get_eth_balance_async(loop, connections['arbitrum'], address),
        get_eth_balance_async(loop, connections['optimism'], address),
        get_eth_balance_async(loop, connections['linea'], address),
        get_eth_balance_async(loop, connections['zksync'], address),
        get_eth_balance_async(loop, connections['scroll'], address),
        get_eth_balance_async(loop, connections['base'], address),
        get_eth_balance_async(loop, connections['arbitrum_nova'], address),
    ]
    try:
        results = await asyncio.gather(*tasks)
        return {'Address': address, 'ETH': results[0], 'ETH_arb': results[1],
                'ETH_op': results[2], 'ETH_linea': results[3],
                'ETH_zksync': results[4], 'ETH_scroll': results[5],
                'ETH_base': results[6], 'ETH_arb_nova': results[7]}
    except Exception as e:
        return {'Address': address, 'error': f"Ошибка при обработке адреса: {e}"}

async def async_main(addresses, connections, excel_filename, progress_callback=None):
    results = []
    loop = asyncio.get_event_loop()
    total = len(addresses)
    for i, address in enumerate(addresses):
        res = await process_address(address, loop, connections)
        results.append(res)
        if progress_callback:
            progress_callback(int((i + 1) / total * 100))
    df = pd.DataFrame(results)
    df.to_excel(excel_filename, index=False)
    print(f"Балансы сохранены в файл {excel_filename}")

def run_balance_check(addresses, progress_callback=None):
    # Считываем актуальную конфигурацию при запуске проверки
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Получаем настройки включённых сетей
    network_to_process = {key: config.getboolean('Networks', key) for key in config['Networks']}
    if not any(network_to_process.values()):
        raise ValueError("Не выбрана ни одна сеть в конфигурационном файле. Выберите хотя бы одну сеть.")
    
    def connect_to_network(network_name, provider_url):
        if network_to_process.get(network_name):
            return Web3(Web3.HTTPProvider(provider_url))
        return None

    # Создаём подключения к сетям, используя актуальные настройки
    connections = {}
    connections['ethereum'] = connect_to_network('ethereum', config.get('RPCs', 'ethereum'))
    connections['arbitrum'] = connect_to_network('arbitrum', config.get('RPCs', 'arbitrum'))
    connections['optimism'] = connect_to_network('optimism', config.get('RPCs', 'optimism'))
    connections['linea'] = connect_to_network('linea', config.get('RPCs', 'linea'))
    connections['zksync'] = connect_to_network('zksync', config.get('RPCs', 'zksync'))
    connections['scroll'] = connect_to_network('scroll', config.get('RPCs', 'scroll'))
    connections['base'] = connect_to_network('base', config.get('RPCs', 'base'))
    connections['arbitrum_nova'] = connect_to_network('arbitrum_nova', config.get('RPCs', 'arbitrum_nova'))

    output_dir = config.get("Output", "output_dir", fallback="").strip()
    if output_dir:
        # Если указан, добавляем "/" или используем os.path.join для формирования пути
        import os
        excel_filename = os.path.join(output_dir, "ethereum_balances.xlsx")
    else:
        excel_filename = "ethereum_balances.xlsx"

    asyncio.run(async_main(addresses, connections, excel_filename, progress_callback))
