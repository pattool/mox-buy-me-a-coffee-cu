import boa
from tests.conftest import SEND_VALUE

## Failed test with sepolia fork
#def test_fund_10_user_with_money(coffee):
#    
#    num_funders = 10
#    for idx in range(num_funders):
#        funder =  boa.env.generate_address(idx)
#        boa.env.set_balance(funder, SEND_VALUE)
#        with boa.env.prank(funder): 
#            coffee.fund(value=SEND_VALUE)
#
#        with boa.env.prank(coffee.OWNER()): 
#            coffee.fund(value=SEND_VALUE)
#            coffee.withdraw()
#        assert boa.env.get_balance(coffee.address) == 0