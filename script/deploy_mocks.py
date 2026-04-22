from src.mocks import mock_v3_aggregator
from moccasin.boa_tools import VyperContract


STARTING_DECIMALS = 8
STARTING_PRICE = int(2000e8) # 2000$ in uint8-> e8 = 8decimals

def deploy_feed() -> VyperContract:
    return mock_v3_aggregator.deploy(STARTING_DECIMALS, STARTING_PRICE)


def moccasin_main() -> VyperContract:
    return deploy_feed()
    