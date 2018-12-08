from rotkehlchen.fval import FVal
from rotkehlchen.order_formatting import MarginPosition
from rotkehlchen.tests.utils.accounting import accounting_history_process

DUMMY_HASH = '0x0'
DUMMY_ADDRESS = '0x0'

trades_history = [
    {
        'timestamp': 1446979735,  # 08/11/2015
        'pair': 'BTC_EUR',
        'type': 'buy',
        'rate': 268.678317859,
        'cost': 1343.3915893,
        'cost_currency': 'EUR',
        'fee': 0,
        'fee_currency': 'BTC',
        'amount': 5,
        'location': 'external',
    }, {
        'timestamp': 1446979735,  # 08/11/2015
        'pair': 'ETH_EUR',
        'type': 'buy',
        'rate': 0.2315893,
        'cost': 335.804485,
        'cost_currency': 'EUR',
        'fee': 0,
        'fee_currency': 'ETH',
        'amount': 1450,
        'location': 'external',
    }, {
        'timestamp': 1467378304,  # 31/06/2016
        'pair': 'BTC_EUR',  # cryptocompare hourly BTC/EUR price 612.45
        'type': 'sell',
        'rate': 612.45,
        'cost': 1531.125,
        'cost_currency': 'EUR',
        'fee': '0.15',
        'fee_currency': 'EUR',
        'amount': 2.5,
        'location': 'kraken',
    }, {
        'timestamp': 1473505138,  # 10/09/2016
        'pair': 'BTC_ETH',  # cryptocompare hourly ETH/EUR price: 10.365
        'type': 'buy',  # Buy ETH with BTC -- taxable (within 1 year)
        'rate': 0.01858275,  # cryptocompare hourly BTC/EUR price: 556.435
        'cost': 0.9291375,
        'cost_currency': 'BTC',
        'fee': 0.06999999999999999,
        'fee_currency': 'ETH',
        'amount': 50.0,
        'location': 'poloniex',
    }, {
        'timestamp': 1475042230,  # 28/09/2016
        'pair': 'BTC_ETH',  # cryptocompare hourly ETH/EUR price: 11.925
        'type': 'sell',  # Sell ETH for BTC -- taxable (within 1 year)
        'rate': 0.022165,  # cryptocompare hourly BTC/EUR price: 537.805
        'cost': 0.554125,
        'cost_currency': 'BTC',  # reminder: we calculate buying cost with paid
        'fee': 0.001,            # asset. In this case 'ETH'. So BTC buy rate is:
        'fee_currency': 'ETH',   # (1 / 0.022165) * 11.925
        'amount': 25,
        'location': 'poloniex',
    }, {
        'timestamp': 1476536704,  # 15/10/2016
        'pair': 'BTC_ETH',  # cryptocompare hourly ETH/EUR price: 10.775
        'type': 'sell',  # Sell ETH for BTC -- taxable (within 1 year)
        'rate': 0.018355,  # cryptocompare hourly BTC/EUR price: 585.96
        'cost': 3.3039,
        'cost_currency': 'BTC',  # reminder: we calculate buying cost with paid
        'fee': 0.01,             # asset.In this case 'ETH'. So BTC buy rate is:
        'fee_currency': 'ETH',   # (1 / 0.018355) * 10.775
        'amount': 180.0,
        'location': 'poloniex',
    }, {
        'timestamp': 1479200704,  # 15/11/2016
        'pair': 'DASH_BTC',  # cryptocompare hourly DASH/EUR price: 8.9456
        'type': 'buy',  # Buy DASH with BTC -- non taxable (after 1 year)
        'rate': 0.0134,  # cryptocompare hourly BTC/EUR price: 667.185
        'cost': 0.536,
        'cost_currency': 'BTC',
        'fee': 0.00082871175,
        'fee_currency': 'BTC',
        'amount': 40,
        'location': 'poloniex',
    }, {  # 0.00146445 * 723.505 + 0.005 * 8.104679571509114828039 = 1.10006029511
        'timestamp': 1480683904,  # 02/12/2016
        'pair': 'DASH_BTC',  # cryptocompare hourly DASH/EUR price: 8.104679571509114828039
        'type': 'settlement_sell',  # settlement sell DASH for BTC -- taxable (within 1 year)
        'rate': 0.011265,  # cryptocompare hourly BTC/EUR price: 723.505
        'cost': 0.00146445,
        'cost_currency': 'BTC',
        'fee': 0.005,
        'fee_currency': 'DASH',
        'amount': 0.13,
        'location': 'poloniex',
    }, {  # 129.2517-0.01 - ((0.536+0.00082871175)*10/40)*667.185 = 39.7006839878
        'timestamp': 1483520704,  # 04/01/2017
        'pair': 'DASH_EUR',  # cryptocompare hourly DASH/EUR price: 12.92517
        'type': 'sell',  # Sell DASH for EUR -- taxable (within 1 year)
        'rate': 12.92517,
        'cost': 129.2517,
        'cost_currency': 'EUR',
        'fee': 0.01,
        'fee_currency': 'EUR',
        'amount': 10,
        'location': 'kraken',
    }, {  # 0.00244725 * 942.78 + 0.01*15.36169816590634019 = 2.46083533666
        'timestamp': 1486299904,  # 05/02/2017
        'pair': 'DASH_BTC',  # cryptocompare hourly DASH/EUR price: 15.36169816590634019
        'type': 'settlement_sell',  # settlement sell DASH for BTC -- taxable (within 1 year)
        'rate': 0.016315,  # cryptocompare hourly BTC/EUR price: 942.78
        'cost': 0.00244725,
        'cost_currency': 'BTC',
        'fee': 0.01,
        'fee_currency': 'DASH',
        'amount': 0.15,
        'location': 'poloniex',
    }, {  # Partly taxable sell.
        'timestamp': 1488373504,  # 29/02/2017
        'pair': 'BTC_EUR',  # cryptocompare hourly DASH/EUR price: 15.36169816590634019
        'type': 'sell',  # sell BTC for EUR -- partly taxable (within 1 year)
        'rate': 1146.22,  # cryptocompare hourly BTC/EUR price: 1146.22
        'cost': 2292.44,
        'cost_currency': 'EUR',  # Non taxable BTC: 1.034862500. Then 0.554125
        'fee': 0.01,             # from 1475042230 and 3.3039 from 1476536704
        'fee_currency': 'EUR',   # Also note that fees at corresponding buys are
        'amount': 2,             # not yet accounted
        'location': 'kraken',
    },
]

loans_list = [
    {  # before query period -- (0.0002 - 0.000001) * 10.785 = 2.146215e-3
        'open_time': 1463505138,
        'close_time': 1463508234,  # 17/05/2016
        'currency': 'ETH',  # cryptocompare hourly ETH/EUR: 10.785
        'fee': FVal(0.000001),
        'earned': FVal(0.0002),
        'amount_lent': FVal(2),
    }, {  # (0.002-0.0001) * 10.9698996 = 0.02084280924
        'open_time': 1483350000,
        'close_time': 1483351504,  # 02/01/2017
        'currency': 'DASH',  # cryptocompare hourly DASH/EUR: 10.9698996
        'fee': FVal(0.0001),
        'earned': FVal(0.002),
        'amount_lent': FVal(2),
    }, {  # (0.003-0.00015)*13.22106438 = 0.037680033483
        'open_time': 1485250000,
        'close_time': 1485252304,  # 24/01/2017
        'currency': 'DASH',  # cryptocompare hourly DASH/EUR: 13.22106438
        'fee': FVal(0.00015),
        'earned': FVal(0.003),
        'amount_lent': FVal(2),
    }, {  # (0.0035-0.00011)*15.73995672 = 0.0533584532808
        'open_time': 1487021001,
        'close_time': 1487027104,  # 13/02/2017
        'currency': 'DASH',  # cryptocompare hourly DASH/EUR: 15.73995672
        'fee': FVal(0.00011),
        'earned': FVal(0.0035),
        'amount_lent': FVal(2),
    }, {  # outside query period -- should not matter
        'open_time': 1520113204,
        'close_time': 1520118304,  # 03/03/2018
        'currency': 'DASH',  # cryptocompare hourly DASH/EUR: 475.565
        'fee': FVal(0.0001),
        'earned': FVal(0.0025),
        'amount_lent': FVal(2),
    },
]

asset_movements_list = [
    {  # before query period -- 8.915 * 0.001 = 8.915e-3
        'exchange': 'kraken',
        'category': 'withdrawal',
        'timestamp': 1479510304,  # 18/11/2016,
        'asset': 'ETH',  # cryptocompare hourly ETH/EUR: 8.915
        'amount': 95,
        'fee': 0.001,
    }, {  # 0.0087*52.885 = 0.4600995
        'exchange': 'kraken',
        'category': 'withdrawal',
        'timestamp': 1493291104,  # 27/04/2017,
        'asset': 'ETH',  # cryptocompare hourly ETH/EUR: 52.885
        'amount': 125,
        'fee': 0.0087,
    }, {  # deposit have no effect
        'exchange': 'kraken',
        'category': 'deposit',
        'timestamp': 1493636704,  # 01/05/2017,
        'asset': 'EUR',
        'amount': 750,
        'fee': 0,
    }, {  # 0.00029*1964.685 = 0.56975865
        'exchange': 'poloniex',
        'category': 'withdrawal',
        'timestamp': 1495969504,  # 28/05/2017,
        'asset': 'BTC',  # cryptocompare hourly BTC/EUR: 1964.685
        'amount': 8.5,
        'fee': 0.00029,
    }, {  # 0.0078*173.77 = 1.355406
        'exchange': 'poloniex',
        'category': 'withdrawal',
        'timestamp': 1502715904,  # 14/08/2017,
        'asset': 'DASH',  # cryptocompare hourly DASH/EUR: 173.77
        'amount': 20,
        'fee': 0.0078,
    }, {  # after query period -- should not matter
        'exchange': 'bittrex',
        'category': 'withdrawal',
        'timestamp': 1517663104,  # 03/02/2018,
        'asset': 'ETH',
        'amount': 120,
        'fee': 0.001,
    },
]

eth_tx_list = [
    {  # before query period: ((2000000000 * 25000000) / (10 ** 18)) * 9.185 = 0.45925
        'timestamp': 1463184190,  # 14/05/2016
        'block_number': 1512689,  # cryptocompare hourtly ETH/EUR: 9.186
        'hash': DUMMY_HASH,
        'from_address': DUMMY_ADDRESS,
        'to_address': DUMMY_ADDRESS,
        'value': 12323,
        'gas': 5000000,
        'gas_price': 2000000000,
        'gas_used': 25000000,
    }, {  # ((2000000000 * 1000000) / (10 ** 18)) * 47.5 = 0.095
        'timestamp': 1491062063,  # 01/04/2017
        'block_number': 3458409,  # cryptocompare hourly ETH/EUR: 47.5
        'hash': DUMMY_HASH,
        'from_address': DUMMY_ADDRESS,
        'to_address': DUMMY_ADDRESS,
        'value': 12323,
        'gas': 5000000,
        'gas_price': 2000000000,
        'gas_used': 1000000,
    }, {  # ((2200000000 * 2500000) / (10 ** 18)) * 393.955 = 2.1667525
        'timestamp': 1511626623,  # 25/11/2017
        'block_number': 4620323,  # cryptocompare hourly ETH/EUR: 393.955
        'hash': DUMMY_HASH,
        'from_address': DUMMY_ADDRESS,
        'to_address': DUMMY_ADDRESS,
        'value': 12323,
        'gas': 5000000,
        'gas_price': 2200000000,
        'gas_used': 2500000,
    }, {  # after query period -- should not matter
        'timestamp': 1523399409,  # 10/04/2018
        'block_number': 5417790,
        'hash': DUMMY_HASH,
        'from_address': DUMMY_ADDRESS,
        'to_address': DUMMY_ADDRESS,
        'value': 12323,
        'gas': 5000000,
        'gas_price': 2100000000,
        'gas_used': 1900000,
    },
]

margin_history = [
    MarginPosition(  # before query period -- BTC/EUR: 422.90
        exchange='poloniex',
        open_time=1463184190,  # 14/05/2016
        close_time=1464393600,  # 28/05/2016
        profit_loss=FVal(0.05),
        pl_currency='BTC',
        notes='margin1',
    ), MarginPosition(  # before query period -- BTC/EUR: 542.87
        exchange='poloniex',
        open_time=1472428800,  # 29/08/2016
        close_time=1473897600,  # 15/09/2016
        profit_loss=FVal('-0.042'),
        pl_currency='BTC',
        notes='margin2',
    ), MarginPosition(  # BTC/EUR: 1039.935
        exchange='poloniex',
        open_time=1489276800,  # 12/03/2017
        close_time=1491177600,  # 03/04/2017
        profit_loss=FVal('-0.042'),
        pl_currency='BTC',
        notes='margin3',
    ), MarginPosition(  # BTC/EUR: 2244.255
        exchange='poloniex',
        open_time=1496534400,  # 04/06/2017
        close_time=1498694400,  # 29/06/2017
        profit_loss=FVal(0.124),
        pl_currency='BTC',
        notes='margin4',
    )]


def test_end_to_end_tax_report(accountant):
    result = accounting_history_process(
        accountant=accountant,
        start_ts=0,
        end_ts=1514764799,  # 31/12/2017
        history_list=trades_history,
        loans_list=loans_list,
        asset_movements_list=asset_movements_list,
        eth_transaction_list=eth_tx_list,
        margin_list=margin_history,
    )
    result = result['overview']
    general_trade_pl = FVal(result['general_trade_profit_loss'])
    assert general_trade_pl.is_close('5048.20025137')
    taxable_trade_pl = FVal(result['taxable_trade_profit_loss'])
    assert taxable_trade_pl.is_close('3927.02376907')
    loan_profit = FVal(result['loan_profit'])
    assert loan_profit.is_close('0.114027511004')
    settlement_losses = FVal(result['settlement_losses'])
    assert settlement_losses.is_close('3.56089563177')
    asset_movement_fees = FVal(result['asset_movement_fees'])
    assert asset_movement_fees.is_close('2.39417915')
    ethereum_transaction_gas_costs = FVal(result['ethereum_transaction_gas_costs'])
    assert ethereum_transaction_gas_costs.is_close('2.7210025')
    margin_pl = FVal(result['margin_positions_profit_loss'])
    assert margin_pl.is_close('232.95481')
    expected_total_taxable_pl = (
        taxable_trade_pl +
        margin_pl +
        loan_profit -
        settlement_losses -
        asset_movement_fees -
        ethereum_transaction_gas_costs
    )
    total_taxable_pl = FVal(result['total_taxable_profit_loss'])
    assert expected_total_taxable_pl.is_close(total_taxable_pl)
    expected_total_pl = (
        general_trade_pl +
        margin_pl +
        loan_profit -
        settlement_losses -
        asset_movement_fees -
        ethereum_transaction_gas_costs
    )
    total_pl = FVal(result['total_profit_loss'])
    assert expected_total_pl.is_close(total_pl)


def test_end_to_end_tax_report_in_period(accountant):
    result = accounting_history_process(
        accountant=accountant,
        start_ts=1483228800,  # 01/01/2017
        end_ts=1514764799,  # 31/12/2017
        history_list=trades_history,
        loans_list=loans_list,
        asset_movements_list=asset_movements_list,
        eth_transaction_list=eth_tx_list,
        margin_list=margin_history,
    )
    result = result['overview']
    general_trade_pl = FVal(result['general_trade_profit_loss'])
    assert general_trade_pl.is_close('1522.86543605')
    taxable_trade_pl = FVal(result['taxable_trade_profit_loss'])
    assert taxable_trade_pl.is_close('614.735631324')
    loan_profit = FVal(result['loan_profit'])
    assert loan_profit.is_close('0.111881296004')
    settlement_losses = FVal(result['settlement_losses'])
    assert settlement_losses.is_close('2.46083533666')
    asset_movement_fees = FVal(result['asset_movement_fees'])
    assert asset_movement_fees.is_close('2.38526415')
    ethereum_transaction_gas_costs = FVal(result['ethereum_transaction_gas_costs'])
    assert ethereum_transaction_gas_costs.is_close('2.2617525')
    margin_pl = FVal(result['margin_positions_profit_loss'])
    assert margin_pl.is_close('234.61035')
    expected_total_taxable_pl = (
        taxable_trade_pl +
        margin_pl +
        loan_profit -
        settlement_losses -
        asset_movement_fees -
        ethereum_transaction_gas_costs
    )
    total_taxable_pl = FVal(result['total_taxable_profit_loss'])
    assert expected_total_taxable_pl.is_close(total_taxable_pl)
    expected_total_pl = (
        general_trade_pl +
        margin_pl +
        loan_profit -
        settlement_losses -
        asset_movement_fees -
        ethereum_transaction_gas_costs
    )
    total_pl = FVal(result['total_profit_loss'])
    assert expected_total_pl.is_close(total_pl)


# Calculation notes for all events in this end to end test
# --> 1467378304 (taxable)

# Sell BTC for EUR

# gain: 612.45*2.5 - 0.15 = 1530.975

# bought_cost: 671.695794648

# profit: 1530.975 - 671.695794648 = 859.279205352


# --> 1473505138 (taxable)

# Buy ETH with BTC -- Sell BTC for EUR

# gain: 0.9291375*556.435 - 0.06999999999999999*10.365
# gain: 516.279074813

# bought_cost: 0.9291375 *268.678317859
# bought_cost: 249.63910056

# profit: 516.279074813 - 249.63910056
# profit: 266.639974253


# --> 1475042230 (taxable)

# Sell ETH for BTC

# gain: 0.554125 * 537.805 - 0.001 * 11.925
# gain: 297.999270625

# bought_cost: 25 * 0.2315893
# bought_cost: 5.7897325

# profit: 297.999270625 - 5.7897325 = 292.209538125

# --> 1476536704

# Sell ETH for BTC

# gain: 3.3039 * 585.96 - 0.01*10.775
# gain: 1935.845494

# bought_cost: 180 * 0.2315893
# bought_cost: 41.686074

# profit: 1935.845494 - 41.686074
# profit: 1894.15942

# --> 1479200704  (sell is non taxable -- after 1 year)

# Buy Dash with BTC -- Sell BTC for EUR

# gain: (0.536 - 0.00082871175)* 667.185
# gain: 357.058255951

# part_from_1st_btc_buy =  2.5-0.5136 = 1.9864

# bought_cost = 0.536 * 268.678317859 = 144.011578372

# profit: 357.058255951 - 144.011578372
# profit: 213.046677579

# --> 1483520704  (taxable)

# Sell DASH for EUR

# gain: 129.2517 - 0.01 = 129.2417

# bought_cost: (0.536 + 0.00082871175)*667.185*(10/40)
# bought_cost: 89.5410160122

# profit: 129.2417 - 89.5410160122 = 39.7006839878

# --> 1488373504 (partly taxable)

# Sell 2 BTC for EUR

# gain: 2292.44 - 0.01 = 2292.43

# taxfree_bought_cost = 1.034862500 * 268.678317859 = 278.045115715

# part_from_1st_btc_buy: 2.5-1.4651375 = 1.0348625
# part_from_1nd_margin_profit: 0.05
# part_from_2nd_btc_buy: 0.554125
# part_from_3rd_btc_buy: 2 - 1.0348625 - 0.554125 - 0.05 = 0.3610125

# taxable_bought_cost = 0.05 * 422.90 + 0.554125 * ((1 / 0.022165) * 11.925) + 0.001 *11.925 +
# 0.3610125 * ((1 / 0.018355) * 10.775) + (0.3610125/3.3039) * 0.01 * 10.775
# taxable_bought_cost = 531.220132224

# general_pl = 2292.43 - (531.220132224 + 278.045115715)
# general_pl = 1483.16475206

# taxable_pl = ((0.554125+0.4110125)/2)*2292.43 - 531.220132224
# taxable_pl = 575.034947336
