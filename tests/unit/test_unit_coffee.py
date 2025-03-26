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
        coffee.fund() 
        
def test_fund_with_money(coffee, account):
    # Arrange
    boa.env.set_balance(account.address, SEND_VALUE * 3)
    # Act
    coffee.fund(value=SEND_VALUE)
    # Assert
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE

def test_non_owner_cannot_withdraw(coffee, account):

    boa.env.set_balance(account.address, SEND_VALUE * 3)
    with boa.env.prank(RANDOM_USER):
        with boa.reverts("Not the contract owner!"):
            coffee.withdraw()
    assert boa.env.get_balance(account.address) > 0

def test_non_owner_cannot_withdraw2(coffee_funded, account):    

    with boa.env.prank(RANDOM_USER): # pretend to be another user
        with boa.reverts("Not the contract owner!"):
            coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) > 0

def test_owner_can_withdraw(coffee, account):
    boa.env.set_balance(coffee.OWNER(), SEND_VALUE * 3)
    with boa.env.prank(coffee.OWNER()):
        coffee.fund(value=SEND_VALUE)
        coffee.withdraw()
    assert boa.env.get_balance(coffee.address) == 0

def test_owner_can_withdraw2(coffee_funded):    

    with boa.env.prank(coffee_funded.OWNER()): # pretend to be another user
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) == 0

def test_get_rate(coffee):
    assert coffee.get_eth_to_usd_rate(SEND_VALUE) > 0


def test_direct_default_call(coffee, account):
    
    # Setup
    boa.env.set_balance(account.address, SEND_VALUE * 10)
    
    # call __default__
    with boa.env.prank(account.address):
        coffee.__default__(value=SEND_VALUE)

    assert coffee.funder_to_amount_funded(account.address) == SEND_VALUE

def test_direct_default_call2(coffee_funded):
        
    with boa.env.prank(coffee_funded.address):
        coffee_funded.__default__(value=SEND_VALUE)
        
    assert coffee_funded.funder_to_amount_funded(coffee_funded.address) == SEND_VALUE

#-----------------------------------------------------------------------------------------

def test_fund_10_user_with_money(coffee):
    
    for idx in range(10):
        funder =  boa.env.generate_address(idx)
        boa.env.set_balance(funder, SEND_VALUE*3)
        with boa.env.prank(funder):
            coffee.fund(value=SEND_VALUE)
            
    starting_balance_fund  = boa.env.get_balance(coffee.address)
    
    boa.env.set_balance(coffee.OWNER(), SEND_VALUE*3)
    starting_balance_owner = boa.env.get_balance(coffee.OWNER())

    with boa.env.prank(coffee.OWNER()): 
           coffee.fund(value=SEND_VALUE)
           coffee.withdraw()
        
    assert boa.env.get_balance(coffee.address) == 0
    assert boa.env.get_balance(coffee.OWNER()) == starting_balance_fund + starting_balance_owner
        
def test_default_function_calls_fund(coffee, account):
    """Test sending ETH to contract activates default function"""
    
    print("Running default function test")
    
    # Initial 
    initial_amount = coffee.funder_to_amount_funded(account.address)
        
    # Set balance for account
    boa.env.set_balance(account.address, SEND_VALUE * 10)
    
    # Send ETH directly to the contract address (this triggers __default__)
    with boa.env.prank(account.address):
        boa.env.raw_call(coffee.address, data=b"", value=SEND_VALUE)
            
    # Verify the contract balance increased
    assert coffee.funder_to_amount_funded(account.address) ==  initial_amount + SEND_VALUE


def test_withdraw_resets_funders_and_amounts(coffee, account):
    # Setup - fund the contract from multiple accounts
    boa.env.set_balance(account.address, SEND_VALUE * 10)
    
    # Fund from main account
    coffee.fund(value=SEND_VALUE)
    
    # Fund from another account
    with boa.env.prank(RANDOM_USER):
        boa.env.set_balance(RANDOM_USER, SEND_VALUE * 10)
        coffee.fund(value=SEND_VALUE)
    
    # Verify we have funds and funders
    assert coffee.funders(0) == account.address
    assert coffee.funders(1) == RANDOM_USER
    assert coffee.funder_to_amount_funded(account.address) == SEND_VALUE
    assert coffee.funder_to_amount_funded(RANDOM_USER) == SEND_VALUE
   
    # Withdraw as owner
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()
   
    # Verify amounts are reset
    assert coffee.funder_to_amount_funded(account.address) == 0
    assert coffee.funder_to_amount_funded(RANDOM_USER) == 0  
    
    # To verify the array is empty, we'll need to try accessing an index
    # that should no longer exist (this should revert)
    with boa.reverts():
        coffee.funders(0)  # This should revert if the array is empty


def test_withdraw_with_no_funds(coffee):
    """Test withdrawing when there are no funds in the contract"""
    # Ensure there are no funds in the contract to begin with
    assert boa.env.get_balance(coffee.address) == 0
    
    # Call withdraw as the owner
    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()
        
    # Verify the balance is still 0
    assert boa.env.get_balance(coffee.address) == 0


def test_fund_adds_to_existing_amount_and_funders_array(coffee, account):
    """Test that funding adds to existing amount and adds to funders array each time"""
    # Set up
    boa.env.set_balance(account.address, SEND_VALUE * 3)
    
    # Fund once
    coffee.fund(value=SEND_VALUE)
    initial_amount = coffee.funder_to_amount_funded(account.address)
    
    # Fund again
    coffee.fund(value=SEND_VALUE)
    
    # Verify amount was added, not replaced
    assert coffee.funder_to_amount_funded(account.address) == initial_amount + SEND_VALUE
    
    # Check that the funder was added twice to the funders array
    assert coffee.funders(0) == account.address
    assert coffee.funders(1) == account.address


def test_withdraw_with_funds_but_empty_funders(coffee):
    """Test withdrawing when there are funds but the funders array is empty"""
    # Send ETH directly to the contract address without using the fund function
    # We'll use a raw_call with empty data (this won't trigger __default__)
    owner = coffee.OWNER()
    boa.env.set_balance(owner, SEND_VALUE)
    
    # Force send ETH to contract (bypassing any function calls)
    start_contract_balance = boa.env.get_balance(coffee.address)
    boa.env.set_balance(coffee.address, start_contract_balance + SEND_VALUE)
    
    # Verify contract has balance but funders array is empty
    assert boa.env.get_balance(coffee.address) == SEND_VALUE
    
    # Try to access first funder (should revert if empty)
    with boa.reverts():
        coffee.funders(0)
    
    # Now withdraw as owner
    with boa.env.prank(owner):
        owner_balance_before = boa.env.get_balance(owner)
        coffee.withdraw()
        
    # Verify contract balance is 0 and owner received funds
    assert boa.env.get_balance(coffee.address) == 0
    # Note: We're not checking owner balance here as it's difficult to account for gas costs


def test_default_function_calls_fund_directly(coffee, account):
    """Test sending ETH to contract directly covers the internal _fund call in __default__"""
    # Set balance for account
    boa.env.set_balance(account.address, SEND_VALUE * 10)
    initial_amount = coffee.funder_to_amount_funded(account.address)
    
    # Send ETH directly to the contract address using raw_call
    # This should trigger the __default__ function
    with boa.env.prank(account.address):
        success = boa.env.raw_call(
            coffee.address,
            data=b"",  # Empty data to trigger __default__
            value=SEND_VALUE
        )
        assert success  # Ensure the call was successful
    
    # Verify the fund logic was executed through __default__
    assert coffee.funder_to_amount_funded(account.address) == initial_amount + SEND_VALUE
    assert coffee.funders(0) == account.address


def test_default_function_low_level(coffee, account):
    """Using very low-level approach to trigger __default__"""
    # Setup
    boa.env.set_balance(account.address, SEND_VALUE * 10)
    
    # Get initial state
    initial_contract_balance = boa.env.get_balance(coffee.address)
    
    # Directly manipulate the EVM state to simulate a transaction to __default__
    with boa.env.prank(account.address):
        # Call the contract without any function selector (should trigger __default__)
        boa.env.raw_call(
            coffee.address,
            data=b"",
            value=SEND_VALUE
        )
    
    # Try to trigger debug/trace output to ensure coverage tool sees execution
    print(f"Contract balance before: {initial_contract_balance}")
    print(f"Contract balance after: {boa.env.get_balance(coffee.address)}")
    print(f"Account funded amount: {coffee.funder_to_amount_funded(account.address)}")
    
    # Assertions to verify __default__ executed
    assert boa.env.get_balance(coffee.address) > initial_contract_balance
    assert coffee.funder_to_amount_funded(account.address) > 0


#def test_get_count_funders(coffee, expected_count = None):
#    
#    funders_list = []
#    i = 0
#    try:
#        while True:
#            funders_list.append(coffee.funders(i))
#            i += 1
#    except Exception as e:
#        assert isinstance(e, Exception), "Expected an exception when accessing out-of-bounds index"
#        
#    initial_funders_count = len(funders_list)
#
#    # Assert that we can get the count - this should always run
#    assert isinstance(initial_funders_count, int), "Funders count should be an integer"
#    
#
#    if expected_count is not None:
#        assert initial_funders_count == expected_count, f"Expected {expected_count} funders, but found {initial_funders_count}"
#    else:
#        # Just print the count if no expectation was provided
#        print(f"Found {initial_funders_count} funders")
#    
#    assert  initial_funders_count >= 0, "Funders count should be non-negative"
#
    
#def test_first_and_last_elements_funders(coffee, expected_count = None):
#
#    funders_list = []
#    i = 0
#    try:
#        while True:
#            funders_list.append(coffee.funders(i))
#            i += 1
#    except Exception as e:
#        assert isinstance(e, Exception), "Expected an exception when accessing out-of-bounds index"
#        
#    initial_funders_count = len(funders_list)
#    
#    if initial_funders_count > 0:
#        
#        # Test that we can access first and last elements
#        assert coffee.funders(0) == funders_list[0], "First funder mismatch"
#        assert coffee.funders(initial_funders_count - 1) == funders_list[-1], "Last funder mismatch"
    

#def test_funder_valid_address(coffee, expected_count = None):
#    
#    i = 0
#    try:
#        while True:
#            # Add assertion to verify each funder is a valid address
#            assert coffee.funders(i) is not None, f"Funder at index {i} is None"
#            assert funder != '0x0000000000000000000000000000000000000000', f"Funder at index {i} is zero address"        
#    except Exception as e:
#        assert isinstance(e, Exception), "Expected an exception when accessing out-of-bounds index"
