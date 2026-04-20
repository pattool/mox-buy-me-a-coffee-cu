# pragma version 0.4.0

# ------------------------------------------------------------------
#                             NATSPEC
# ------------------------------------------------------------------
"""
@license MIT
@title Buy me a Coffee!
@author Patrick
@notice copy code buy_me_a_coffee to practice
"""


# ------------------------------------------------------------------
#                             IMPORTS
# ------------------------------------------------------------------
from interfaces import AggregatorV3Interface
import get_price_module


# ------------------------------------------------------------------
#                      CONSTANTS & IMMUTABLES
# ------------------------------------------------------------------
MINIMUM_USD: public(constant(uint256)) = as_wei_value(5, "ether")
PRICE_FEED: public(immutable(AggregatorV3Interface)) #0x694AA1769357215DE4FAC081bf1f309aDC325306 ETH/USD on sepolia network
OWNER: public(immutable(address))


# ------------------------------------------------------------------
#                        STORAGE VARIABLES
# ------------------------------------------------------------------
funders: public(DynArray[address, 1000])
funder_to_amount_funded: public(HashMap[address, uint256])


# ------------------------------------------------------------------
#                           CONSTRUCTOR
# ------------------------------------------------------------------
@deploy
def __init__(price_feed: address):
    PRICE_FEED = AggregatorV3Interface(price_feed)
    OWNER = msg.sender


# ------------------------------------------------------------------
#                        EXTERNAL FUNCTIONS
# ------------------------------------------------------------------
@external
@payable
def fund():
    self._fund()

@external
def withdraw():
    """Take the money out of the contract, that people sent via the fund function.

    How do we make sure only we can pull the money out?
    """
    assert msg.sender == OWNER, "Not the contract owner!"
    raw_call(OWNER, b"", value=self.balance)
    for funder: address in self.funders:
        self.funder_to_amount_funded[funder] = 0
    self.funders = []

@external
@payable
def __default__():
    self._fund()


# ------------------------------------------------------------------
#                     EXTERNAL VIEW FUNCTIONS
# ------------------------------------------------------------------
@external
@view
def get_eth_to_usd_rate(eth_amount: uint256) -> uint256:
    return get_price_module._get_eth_to_usd_rate(PRICE_FEED, eth_amount)


# ------------------------------------------------------------------
#                        INTERNAL FUNCTIONS
# ------------------------------------------------------------------
@internal
@payable
def _fund():
    """
    Allows users to send $ to this contract
    Have a minimum $ amount to send
    How do we convert the ETH amount to dollars amount?
    """
    usd_value_of_eth: uint256 = get_price_module._get_eth_to_usd_rate(PRICE_FEED, msg.value)
    assert usd_value_of_eth >= MINIMUM_USD, "You must spend more ETH!"
    self.funders.append(msg.sender)
    self.funder_to_amount_funded[msg.sender] += msg.value

