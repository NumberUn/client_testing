import logging
import multiprocessing
import ccxt
import time

from py_timex.client import WsClientTimex


bot = ccxt.timex({
})

data = bot.load_markets()
pairs = set(data)
coins = []
for pair in data:
    # pairs.append(data[pair]['id'])
    coins.append(data[pair]['baseId'])
    coins.append(data[pair]['quoteId'])
coins = set(coins)
coins.discard('TIMEV1')
pairs.discard('TIMEV1/BTC')
pairs.discard('TIMEV1/ETH')
print(pairs)
print(coins)
triangles_coins = []
triangle_sets = []
for pair_1 in pairs:
    for pair_2 in pairs:
        for pair_3 in pairs:
            if pair_1 == pair_2 or pair_1 == pair_3 or pair_2 == pair_3:
                continue
            all_coins = [pair_1.split('/')[0], pair_1.split('/')[1], pair_2.split('/')[0], pair_2.split('/')[1], pair_3.split('/')[0], pair_3.split('/')[1]]
            flag = False
            for coin in all_coins:
                if all_coins.count(coin) != 2:
                    flag = True
            if flag:
                flag = False
                continue
            # if len(all_coins) == 3:
            if set([pair_1, pair_2, pair_3]) not in triangle_sets:
                triangle_sets.append(set([pair_1, pair_2, pair_3]))
                    # triangles_coins.append({'coins': all_coins, 'pairs': [pair_1, pair_2, pair_3]})
pairs = []
for triangle in triangle_sets:
    for pair in triangle:
        pairs.append(pair)
pairs = set(pairs)
print(f"Pairs:")
for pair in pairs:
    print(pair)
print(f"Total pairs: {len(pairs)}")

coins = []
for pair in pairs:
    coins.append(pair.split('/')[0])
    coins.append(pair.split('/')[1])
coins = set(coins)
print(f"Coins: {coins}")
print(f"Total coins: {len(coins)}")

print(f"Triangles:")
for triangle in triangle_sets:
    print(triangle)
print(f"Total triangles: {len(triangle_sets)}")

FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s (%(funcName)s)'
logging.basicConfig(format=FORMAT)
log = logging.getLogger("sample bot")
log.setLevel(logging.DEBUG)

api_key = '0A41D9336BEF4D07A722FDD3A0AA294A'
api_secret = 'YR4NQHQWOR5OXE5N'


queue = multiprocessing.Queue(1024)


def handle_update(update: dict):
    queue.put(update)


client = WsClientTimex(api_key, api_secret)
orderbooks = {}
for pair in pairs:
    orderbooks.update({pair: None})
	client.subscribe(f"{pair.split('/')[0] + pair.split('/')[1]}")
# pair = 'ETH/BTC'
# client.subscribe(f"{pair.split('/')[0] + pair.split('/')[1]}")
client.start_background_updater(handle_update)
while True:
    orderbook = {'asks': [], 'bids': [], 'market': None}
    upd = queue.get()
    # print(upd)
    if upd.get('responseBody'):
        # print(upd.data)
        if upd.data['responseBody'].get('bid'):
            orderbook['market'] = upd.data['responseBody']['bid'][0]['market']
            for bid in upd.data['responseBody']['bid']:
                orderbook['bids'].append([float(bid['price']), float(bid['quantity'])])
            orderbooks[orderbook['market']] = orderbook
        if upd.data['responseBody'].get('ask'):
            orderbook['market'] = upd.data['responseBody']['ask'][0]['market']
            for ask in upd.data['responseBody']['ask']:
                orderbook['asks'].append([float(ask['price']), float(ask['quantity'])])
            orderbooks[orderbook['market']] = orderbook
    if upd.get('bid'):
        orderbook['market'] = upd['bid'][0]['market']
        for bid in upd['bid']:
            orderbook['bids'].append([float(bid['price']), float(bid['quantity'])])
        orderbooks[orderbook['market']] = orderbook
    if upd.get('ask'):
        orderbook['market'] = upd['ask'][0]['market']
        for ask in upd['ask']:
            orderbook['asks'].append([float(ask['price']), float(ask['quantity'])])
        orderbooks[orderbook['market']] = orderbook
    # log.info("order book updated. exchange: %s\tmarket: %s", upd["exchange"], upd["market"])
    print(orderbooks)



