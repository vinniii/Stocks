import consts


class StockParams:
    def __init__(self):
        # default value for GCBE and stock price is 0
        self._price = 0.0
        self._annual_dividend = float(
            consts.annualDividend[consts.Global_Beverage_Corporation_Exchange]
        )
        self._company_earning = float(
            consts.companyEarning[consts.Global_Beverage_Corporation_Exchange]
        )

    def _calc_dividend_yield(self, company, price):
        try:
            self._price = float(price)
            # We can have an API implemented if we have 
            # annual Dividend of various companies. For now I am 
            # assuming a dict in consts
            self._annual_dividend = float(consts.annualDividend[company])
        except KeyError as err:
            print('Company not present in the list, Update Annual Dividend of Company')
            print("GCBE dividend Yield" + str(self._annual_dividend / self._price))
            return None
        try:
            div = self._annual_dividend / self._price
        except ZeroDivisionError as err:
            div = 0.0
            print("Stock price supplied is zero %s", err)
        return div

    def _calc_ratio(self, company, price):
        try:
            self._price = float(price)
            # We can have an API implemented if we have 
            # Company Earning of various companies. For now I am 
            # assuming a dict in consts
            self._company_earning = float(consts.companyEarning[company])
        except KeyError as err:
            print('Company not present in the list, Update company Earning of Company')
            print("GCBE ratio" + str(self._company_earning / self._price))
            return None
        self._price = price
        try:
            ratio = self._company_earning / self._price
        except ZeroDivisionError as err:
            ratio = 0.0
            print("Stock price supplied is zero %s", err)
        return ratio
