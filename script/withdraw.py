from src import buy_me_a_coffee
from moccasin.config import get_active_network

#def withdraw():
#    active_network = get_active_network()
#    coffee = active_network.manifest_named("coffee")
#    print(f"Working with contract {coffee.address}")
#    coffee.withdraw()

# with database active in toml file from network anvil
def withdraw():
    active_network = get_active_network()
    coffee = active_network.manifest_named("buy_me_a_coffee") # from database sqlite
    # OR
    #coffee = active_network.get_latest_contract_checked("buy_me_a_coffee")
    print(f"On network {active_network.name}, withdrawing from {coffee.address}")
    coffee.withdraw()

def moccasin_main():
    return withdraw()