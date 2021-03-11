import argparse
from datetime import datetime
import create_database
import record_trade
import stock_params


def get_args():
    parser = argparse.ArgumentParser(description='GCBE')
    parser.add_argument('-Dividend', '-d', dest='Div', required=False, nargs='+', help='Dividend Yield')
    parser.add_argument('-P/E', '-pe', dest='Ratio', required=False, nargs='+', help='P/E Ratio')
    parser.add_argument('-Transaction', '-t', dest='Transaction', required=False, nargs='?', const=1,
                        help='Transaction Details, Provide, Quantity[default 1],Type[Buy or Sell] and Price')
    parser.add_argument('-VolWtStock', '-v', dest='VWS', required=False, nargs='?', const=1,
                        help='Volume Weighted Stock')
    parser.add_argument('-AllSharedIndex', '-asi', dest='AllSharedIndex', required=False, nargs='?', const=1,
                        help='All Shared Index')
    return parser.parse_args()


def main():
    args = get_args()
    print(args)
    if args.Div or args.Ratio:
        div = stock_params.StockParams()
        if args.Div:
            result = div._calc_dividend_yield(args.Div[0], args.Div[1])
        else:
            result = div._calc_ratio(args.Ratio[0], args.Ratio[1])
        if not result:
            print("Could not get correct Result")
            return
        print(result)

    if args.Transaction:
        # self.shutdown_signal = threading.Event()
        print("Provide Record entries")
        now = datetime.now()
        time_stamp = now.strftime("%d/%m/%Y%H/%M/%S")
        stock = input("Provide Stock")
        quantity = float(input("Provide Stock Quantity"))
        typeStock = input("Provide Stock Type, B for Buy, S for Sell")
        price = float(input("Provide Stock Price"))
        if typeStock == 'B':
            price = abs(price)
        else:
            price = -abs(price)
        # while not self.shutdown_signal.set())
        recTrade = record_trade.RecordTrade()
        recTrade._add_record_entry(stock, time_stamp, quantity, typeStock, price)
        if recTrade.status:
            print("Entry successfully added")
        else:
            print("Trade could not be added since details are not provided properly, Check for help")

    if args.VWS:
        recTrade = record_trade.RecordTrade()
        result = recTrade._get_volume_weighted_average(args.VWS)
        if not result:
            print("Wrong result")
        print(result)

    if args.AllSharedIndex:
        recTrade = record_trade.RecordTrade()
        result = recTrade._all_shared_index()
        if not result:
            print("Wrong result")
        print(result)


main()
