def contract_hist_specs():
    specs = {
            'CL': ['NYMEX', '202309', 1],
            'ES': ['CME', '202309', 2],
            'NQ': ['CME', '202309', 3],
            'NG': ['NYMEX', '202309', 4]
        }
    return specs


def contract_trading_specs(contract):
    specs = {
        'CL': ['NYMEX', '202309', 100],
        'ES': ['CME', '202309', 101],
        'NQ': ['CME', '202309', 102],
        'NG': ['NYMEX', '202309', 103]
    }
    return specs[contract]