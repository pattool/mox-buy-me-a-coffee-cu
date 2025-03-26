#import pytest
#from moccasin.config import get_active_network
#from script.deploy import deploy_coffee
#from test.conftest import SEND_VALUE
#import boa


# WILL ONLY WORK ON A LIVE NETWORK !!!
# JUST FOR INFO, setup not quit right in the deploy.py file for Staging test!!! 
# You can not work with the same fixtures like in the unittest
# --> Better to have a new conftest in the staging folder!


#@pytest.mark.staging
#@pytest.mark.local
#@pytest.mark.ignore_isolation
#def test_can_fund_and_withdraw_live():
#    active_network = get_active_network()
#    price_feed = active_network.manifest_named("price_feed")
#    coffee = deploy_coffee(price_feed)
#    coffee.fund(value = SEND_VALUE)
#    amount_funded = coffee.address_to_amount_funded(boa.env.eoa) # boa.env.eoa = currently active account
#    assert amount_funded == SEND_VALUE
#    coffee.withdraw()
#    assert boa.env.get_balance(coffee.address) == 0