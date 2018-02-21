# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 07:18:48 2018

@author: spa
"""
import os.path
import sys
import json
import datetime
import time
from time import sleep
import api_binance

MAX_REPEAT = 2
SLEEP_PERIOD = 0.5

def get_keys(secret_file):
    """ read and output data as a string list """
    keys = []
    if os.path.isfile(secret_file):
        f = open(secret_file, 'r')
        while True:
            try:
                line_next = next(f)
            except StopIteration:
                break
            keys.append(line_next.rstrip()) # remove whitespace at the line end
        f.close()
        apikey = keys[0]
        secretkey = keys[1]
    else:
        apikey = input('\tFile with keys not found.\n '\
                       '\tEnter API key or q[uit] for exit:\n'\
                            '==> ')
        if apikey == 'q' or apikey == 'Q':
            return ('', '')

        secretkey = input('\tEnter secret key or q[uit] for exit:\n'\
                            '==> ')
        if secretkey == 'q' or secretkey == 'Q': sys.exit()
    return (apikey, secretkey)

def sigint_handler():
    """Handler for ctrl+c"""
    print('\n==> CTRL+C pressed. Exiting...')
    sys.exit()

def main():
    print('\t\tWelcome to Trade Bot!')
    print('\t\t====================')
    print('\t   Press CTRL+C to exit at anytime')
    print('\t   -------------------------------\n')

    # set keys
    (apikey, secretkey) = get_keys('keys.txt')
    if apikey == '':
        print('API key do not found')
        return
    api = api_binance.ClientAPI(apikey, secretkey)

    # check server abailability and calculate deltatime
    print('Check server abailability...')

    st_code = 0; i = 0
    while st_code != 200 and i < MAX_REPEAT:
        (st_code, response_json, inf) = api.server_time()
        if st_code != 200:
            sleep(SLEEP_PERIOD)
            i = i + 1
    if st_code != 200:
        print(i, ' attempts failed')
        print(inf)
        print('Bot says goodbye to you ...')
        return inf

    timestamp = response_json
    deltatime = timestamp - 1000 * time.time()
    #dtUTC = datetime.datetime.fromtimestamp(int(timestamp)/1000)
    #date_time = dtUTC.strftime('%Y-%m-%d %H:%M:%S')
    d_t = datetime.datetime.fromtimestamp(int(timestamp)/1000)
    date_time = d_t.strftime('%Y-%m-%d %H:%M:%S')
    print('\nserver:\tdate&time:\n', date_time)
    print('deltatime= ', deltatime, 'ms\n')
    # fetch exchange information
    print('Fetch exchange information...')
    st_code = 0; i = 0
    while st_code != 200 and i < MAX_REPEAT:
        (st_code, exchange_info, inf) = api.exchange_info()
        if st_code != 200:
            sleep(SLEEP_PERIOD)
            i = i + 1
    if st_code != 200:
        print(i, ' attempts failed')
        print(inf)
        print('Bot says goodbye to you ...')
        return inf

    #get account BTC balance
    print('Check account BTC balance and validation of keys...\n')

    st_code = 0; i = 0
    while st_code != 200 and i < MAX_REPEAT:
        (st_code, response_json, inf) = api.acc_inf(deltatime=deltatime)
        if st_code != 200:
            sleep(SLEEP_PERIOD)
            i = i + 1
    if st_code != 200:
        print('Check keys')
        print(i, ' attempts failed')
        print(inf)
        print('Bot says goodbye to you ...')
        return inf

    for idict in response_json['balances']:
        if idict['asset'] == 'BTC':
            balanceBTC = float(idict['free'])
            print('Balance: ', balanceBTC, 'BTC\n')

    # input trading mode
    trade_mode = input('Do you want to use TEST mode? '\
                       'Not more than 0,01 BTC per order (y/n)\n '\
                       '==> ')
    if trade_mode.upper() == 'Y':
        print('You chose TEST mode\n')
    else:
        print('You chose NORMAL mode (trading for 50% of the deposit in BTC per order)\n')

    # input coin
    coin = input('\nEnter coin for trading or q[uit] for exit:\n'\
                       '==> ')
    if coin == 'q' or coin == 'Q': sys.exit()
    coin = coin.upper()
    symbol = coin + 'BTC'

    list__buyorder = []
    amount_buyorder = 0
    exit_cycle = False
    while not exit_cycle:
        print('\n-------------------------------')
        print('Press CTRL+C to exit at anytime')
        print('-------------------------------\n')

        #1. candle 5 min
        st_code = 0; i = 0
        while st_code != 200 and i < MAX_REPEAT:

            (st_code, response_json, inf) =\
            api.candle(symbol=symbol, interval='5m', limit=2)
            if st_code != 200:
                sleep(SLEEP_PERIOD)
                i = i + 1

        if st_code != 200:
            print(i, ' attempts failed')
            print('server:', inf)
            print('Bot says goodbye to you ...')
            return

        price_open = float(response_json[0][1])
        price_high = float(response_json[0][2])
        price_low = float(response_json[0][3])
        price_close = float(response_json[0][4])
        volume = float(response_json[0][5])
        time_close = response_json[0][6]

        d_t = datetime.datetime.fromtimestamp(int(response_json[0][0])/1000)
        time_open = d_t.strftime('%Y-%m-%d %H:%M:%S')
        d_t = datetime.datetime.fromtimestamp(int(response_json[0][6])/1000)
        time_close = d_t.strftime('%Y-%m-%d %H:%M:%S')

        print('Last whole 5 min candlestick, symbol ', symbol, ':\n')
        print('\topen time\t', time_open)
        print('\tclose time\t', time_close)
        print('\tprice "Open"\t', '%.8f' % price_open)
        print('\tprice "High"\t', '%.8f' % price_high)
        print('\tprice "Low"\t', '%.8f' % price_low)
        print('\tprice "Close"\t', '%.8f' % price_close)
        print('\tvolume\t\t', volume, '\n')
        #print('response_json=', response_json)


        #2. order calculation
        # minQty, minNotional
        for idict in exchange_info['symbols']:
            if idict['baseAsset'] == coin:
                for jdict in idict['filters']:
                    if jdict['filterType'] == 'PRICE_FILTER':
                        tickSize = float(jdict['tickSize'])
                    if jdict['filterType'] == 'LOT_SIZE':
                        minQty = float(jdict['minQty'])
                        stepSize = float(jdict['stepSize'])
                    if jdict['filterType'] == 'MIN_NOTIONAL':
                        minNotional = float(jdict['minNotional'])

        #price for BUY LIMIT => * 1.1, rounded with tickSize
        order_price = tickSize * int(price_close/tickSize + 1)
        #stop-loss  => * 0.99, rounded with tickSize
        stopPrice = tickSize * int((price_close * 0.99)/tickSize)
        if stopPrice == order_price:
            stopPrice = order_price - tickSize

        if trade_mode.upper() == 'Y':
            balanceBTC = 0.02         # TEST mode

        order_qty = (0.5 * balanceBTC) / order_price
        order_qty = 10 * stepSize * int(order_qty / (10 * stepSize))  # rounded down
        order_BTC = order_qty * order_price
        newClientOrderId = '%s_%s' % (symbol, str(int(time.time()*1000)))

        print('Binance restrictions for ', coin, ":")
        print('LOT_SIZE, min qty =\t', '%.8f' % minQty)
        print('LOT_SIZE, stepSize =\t', '%.8f' % stepSize)
        print('PRICE, tickSize =\t', '%.8f' % tickSize)
        print('MIN_NOTIONAL, min =\t', '%.8f' % minNotional)
        print('\nYour next order:')
        print('quantity =\t\t', '%.8f' % order_qty)
        print('BUY LIMIT order price =\t', '%.8f' % order_price)
        print('     stop-loss price =\t', '%.8f' % stopPrice)
        print('Cost in BTC =\t\t', '%.8f' % order_BTC)

        if order_BTC > balanceBTC:
            print('\nInsufficient funds for trading!!!')
            print('You have ', balanceBTC, ' BTC available')
            print('You need ', order_BTC, 'for this order')
            print('Bot says goodbye to you ...')
            return 'Insufficient funds for tradind'

        #3. put order 'BUY STOP_LOSS_LIMIT'
        print('put order BUY LIMIT with stop-loss...')
        kargs = {'symbol':symbol,
                 'side':'BUY',
                 'type':'STOP_LOSS_LIMIT',
                 'quantity':order_qty,
                 'price':order_price,
                 'stopPrice': '%.8f' % stopPrice,
                 'newClientOrderId':newClientOrderId,
                 'recvWindow':5000,
                 'timeInForce':'GTC'
                }
        st_code = 0; i = 0
        while st_code != 200 and i < MAX_REPEAT:
            # This is real order!
            (st_code, response_json, inf) =\
                api.new_order(deltatime=deltatime, **kargs)

            if st_code != 200:
                sleep(SLEEP_PERIOD)
                i = i + 1

        if st_code != 200:
            print(i, ' attempts failed')
            print('server:', inf)
            print('Bot says goodbye to you ...')
            return

        #print(json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ': ')))
        amount_buyorder += 1

        print('newClientOrderId=', kargs['newClientOrderId'])
        print('Order Ok')
        print('total opened "BUY" orders:', amount_buyorder)
        list__buyorder.append(newClientOrderId)
        for orderid in list__buyorder:
            print('\nClientOrderId=', orderid)

        #3. check order
        '''
        print('Check new order...\n')
        kargs = {'symbol':symbol,
                 'origClientOrderId':newClientOrderId
                }

        st_code = 0; i = 0
        while st_code != 200 and i < MAX_REPEAT:
            (st_code, response_json, inf) =\
                api.query_order(deltatime=deltatime, **kargs)

            if st_code != 200:
                sleep(SLEEP_PERIOD)
                i = i + 1

        if st_code != 200:
            print(i, ' attempts failed')
            print('server:', inf)
            print('Bot says goodbye to you ...')
            return

        if response_json['isWorking'] == 'true':
            print('Order Ok')
        else:
            print('response_json=', response_json)
            print(json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ': ')))

        '''
        #4. put order TAKE_PROFIT
        print('Put order SELL LIMIT (take profit)...')
        stopPrice = tickSize * round(price_close * 1.1 / tickSize)
        kargs = {'stopPrice': '%.8f' % stopPrice,
                 'symbol':symbol,
                 'side':'SELL',
                 'type':'TAKE_PROFIT',
                 'quantity':order_qty,
                 'recvWindow':10000,
                }
        # This is real order!
        st_code = 0; i = 0
        while st_code != 200 and i < MAX_REPEAT:
            (st_code, response_json, inf) =\
                api.new_order(deltatime=deltatime, **kargs)
            if st_code != 200:
                sleep(SLEEP_PERIOD)
                i = i + 1

        if st_code != 200:
            print(i, ' attempts failed')
            print('server:', inf)
            print('Bot says goodbye to you ...')
            return

        #print(json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ': ')))
        print('Order Ok')

        #5. check total amount opders and waiting filling
        while amount_buyorder == 2:
            st_code = 0; i = 0
            while st_code != 200 and i < MAX_REPEAT:
                for orderid in list__buyorder:
                    kargs = {'symbol':symbol,
                             'origClientOrderId':orderid}
                    (st_code, response_json, inf) =\
                        api.query_order(deltatime=deltatime, **kargs)

                    if st_code == 200 and 'status' in response_json:
                        if response_json['status'] != 'NEW' or\
                           response_json['status'] != 'PARTIALLY_FILLED'or\
                           response_json['status'] != 'PENDING_CANCEL':
                            list__buyorder.remove(orderid)
                            amount_buyorder -= 1

                    if st_code == 400:
                        if '"code":-2013' in inf:
                            print('server: Order does not exist.')
                            list__buyorder.remove(orderid)
                            amount_buyorder -= 1

                if st_code != 200:
                    sleep(SLEEP_PERIOD)
                    i = i + 1

            if st_code != 200:
                print('server:', inf)
                sleep(SLEEP_PERIOD)

            sleep(SLEEP_PERIOD)
            
        #print(json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ': ')))
        print(list__buyorder)

def dump_output_file(obj, file):
    outputfile = open(file, 'w')
    outputfile.write(json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))
    outputfile.close()

if __name__ == '__main__':
    main()
