
from django.shortcuts import render
import json
import time
from datetime import datetime, timezone
from binance import Client
from .keys import api_key, api_secret, api_secret1, api_key1
from django.core.mail import send_mail


client = Client(api_key, api_secret)
client1 = Client(api_key1, api_secret1)


def home(request):
    start = time.time()
    date = datetime.now()
    data = pending_orders(client)
    profit = create_report(client)
    previous_orders = prev_orders(client)
    context = {'date': date, 'data': data, 'profit': profit, 'previousorder': previous_orders, "name": "Srivardhan",
               'site': "next"}
    print(time.time()-start)
    return render(request, 'home/index.html', context)


def index(request):
    date = datetime.now()
    data = pending_orders(client1)
    profit = create_report(client1)
    previous_orders = prev_orders(client1)
    context = {'date': date, 'data': data, 'profit': profit, 'previousorder': previous_orders, 'name': "DivyaPratap",
               'site': ""}
    return render(request, 'home/index.html', context)


def profit_data(request):
    date = datetime.now()
    pnl = json.load(open('pnl.json'))
    context = {'pnl': pnl, 'date': date}
    return render(request, 'home/pnl.html', context)


def pending_orders(client):
    end = int(datetime.now(timezone.utc).timestamp()) * 1000
    start = end - 100000000
    history = client.get_c2c_trade_history(startDate=start, endDate=end)['data']
    return [i for i in history if i['orderStatus'] not in ['COMPLETED', "CANCELLED", "CANCELLED_BY_SYSTEM"]]


def create_report(client_d):
    current_date = time.strftime("%d%m%y", time.localtime())
    sell_qty = 0
    buy_qty = 0
    buy_avg = 0
    sell_avg = 0
    sell_total = 0
    buy_total = 0
    diff = 0
    profit = 0

    end = int(datetime.now(timezone.utc).timestamp()) * 1000
    start = end - 200000000
    history = client_d.get_c2c_trade_history(startDate=start, endDate=end)['data']
    for i in history:
        tn = int(str(i['createTime'])[:10])
        trade_date = datetime.fromtimestamp(tn).strftime('%d%m%y')

        if current_date == trade_date and i['orderStatus'] == 'COMPLETED' and i['fiat'] == "INR":
            if i['tradeType'] == "BUY":
                buy_qty += float(i['amount'])
                buy_total += float(i['totalPrice'])

            if i['tradeType'] == "SELL":
                sell_qty += float(i['amount'])
                sell_total += float(i['totalPrice'])


    if buy_qty and sell_qty:
        buy_avg = round(buy_total / buy_qty, 3)
        sell_avg = round(sell_total / sell_qty, 3)
        diff = round(sell_avg - buy_avg, 2)
        profit = round(diff * sell_qty, 2)
        buy_total = round(buy_total, 2)
        sell_total = round(sell_total, 2)
        buy_qty = round(buy_qty, 2)
        sell_qty = round(sell_qty, 2)

    return {'profit': profit, 'buy_total': round(buy_total, 2), 'sell_total': sell_total,
            'diff': diff, 'sell_qty': sell_qty, 'buy_qty': buy_qty, 'buy_avg': buy_avg, 'sell_avg': sell_avg}


def prev_orders(client_d):
    current_date = time.strftime("%d%m%y", time.localtime())
    data = []
    end = int(datetime.now(timezone.utc).timestamp()) * 1000
    start = end - 200000000
    for i in client_d.get_c2c_trade_history()['data']:
        tn = int(str(i['createTime'])[:10])
        trade_date = datetime.fromtimestamp(tn).strftime('%d%m%y')

        if current_date == trade_date and i['orderStatus'] not in ["TRADING", "BUYER_PAYED", "IN_APPEAL"]:
            data.append(i)

    return data


def send_report(client):
    data = create_report(client)
    date = time.strftime("%d%m%y", time.localtime())
    send_mail(f'Binance P2P Trade Report {date}.', f'Today\'s Report \n Profit: {data["profit"]}', 'geek@techstackup.tech', ['srivardhan.singh.rathore@gmail.com'], fail_silently=False)
    print("Sent Mail.")

