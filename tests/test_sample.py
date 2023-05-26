#
# NOTE: This import is here ONLY to check that pytest works. 
#
from solution.database import foo

def test_smoke_test():
    """
    Test that pytest works also using personal tests
    """
    import sys
    print(sys.modules.keys())
