import boa
from tests.conftest import SEND_VALUE


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