from moccasin.config import get_active_network
#from script.deploy_mocks import deploy_feed
from moccasin.boa_tools import VyperContract
from src import buy_me_a_coffee

import time

def deploy_coffee(price_feed: VyperContract) -> VyperContract:
    coffee: VyperContract = buy_me_a_coffee.deploy(price_feed)
    print(f"Deployed to {coffee.address}")
    
    #active_network = get_active_network()
    #if active_network.has_explorer() and active_network.is_local_or_forked_network() is False:
    #    result = active_network.moccasin_verify(coffee)
    #    result.wait_for_verification()

    print()
    active_network = get_active_network()
    print(f"Active network: {active_network.name}")
    print(f"Explorer URI: {active_network.explorer_uri}")
    print(f"Explorer type: {active_network.explorer_type}")
    print(f"Network has explorer: {active_network.has_explorer()}")
    print()

    if active_network.has_explorer() and active_network.is_local_or_forked_network() is False:
        print(f"Waiting 20 seconds for contract to be indexed by {active_network.explorer_type} ...")
        time.sleep(20)

        print(f"Starting {active_network.explorer_type} verification...")
        try:
            result = active_network.moccasin_verify(coffee)
            print(f"Verification request submitted to {active_network.explorer_type}")
            result.wait_for_verification()
            print("Verification completed succesfully!")
        except Exception as e:
            print(f"Verification failed with error: {e}")
            print(f"Error type: {type(e).__name__}")
            print()
    
    return coffee

    
def moccasin_main() -> VyperContract:
    active_network = get_active_network()
    price_feed: VyperContract = active_network.manifest_named("price_feed")
    print(f"On network {active_network.name} using price_feed at {price_feed.address}")
    return deploy_coffee(price_feed)


# simplyfied only 1 network with fake price_feed, only good for local networks.
#def moccasin_main():
#    active_network = get_active_network()
#    price_feed: VyperContract = deploy_feed()
#    coffee = buy_me_a_coffee.deploy(price_feed.address)
#    print(f"Coffee deployed at { coffee.address")
    