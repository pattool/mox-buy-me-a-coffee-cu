from eth_utils import to_wei # to_wei in Python == as_wei_value in Vyper
import boa
from tests.conftest import SEND_VALUE

RANDOM_USER = boa.env.generate_address("non-owner") # generate random user

def test_price_feed_is_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address

def test_starting_values(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether")
    assert coffee.OWNER() == account.address
    
def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts("You must spend more ETH!"):
        coffee.fund() # equivalent as in the buy_me_a_coffee.vy contract the function: 
                      # @external
                      # @payable 
                      # def fund():
                            #self._fund()

def test_fund_with_money(coffee, account):
    # Arrange
    boa.env.set_balance(account.address, SEND_VALUE * 3)
    # Act
    coffee.fund(value=SEND_VALUE)
    # Assert
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE

def test_non_owner_cannot_withdraw(coffee_funded, account):    

    with boa.env.prank(RANDOM_USER): # pretend to be another user
        with boa.reverts("Not the contract owner!"):
            coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) > 0
    
def test_owner_can_withdraw(coffee_funded):    

    with boa.env.prank(coffee_funded.OWNER()): # pretend to be another user
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) == 0

def test_owner_can_withdraw2(coffee, account):
    boa.env.set_balance(coffee.OWNER(), SEND_VALUE)
    with boa.env.prank(coffee.OWNER()):
        coffee.fund(value=SEND_VALUE)
        coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0

def test_get_rate(coffee):
    assert coffee.get_eth_to_usd_rate(SEND_VALUE) > 0















