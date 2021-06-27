
from logger import my_logger
from MongoBasse import (base_balance, base_dividents, base_grow_express,
                        base_income, base_score_table, base_temp_express)


class ExpressAnaliz:

    score_table = {
        'grow_revenue': ((0.03, 0.06), 1,),
        'use_of_profit': ((0.07, 0.11), 2,),
        'grow_operation_margin': ((0.06, 0.14), 2,),
        'dynamics_operation_margin': ((-2, 2), 2,),
        'grow_profit_margin': ((0.06, 0.1), 2,),
        'dynamics_profit_margin': ((-2, 2), 1,),
        'grow_EPS': ((0.04, 0.1,), 2,),
        'grow_debt_level': ((0.5, 0.7), -1,),
        'grow_ROE': ((0.1, 0.16), 2,),
        'grow_ROA': ((0.06, 0.08), 1,),
    }

    def dynamic(self, massive):
        preview = None
        score = 0
        for i in range(len(massive)):
            if preview is None:
                preview = massive[i]
                continue
            if 0 < (massive[i] - preview) > preview * 0.02:
                score += 1
            elif -1 * preview * 0.02 > (massive[i] - preview) < -2:
                score -= 1
            preview = massive[i]
        return score

    def __init__(
            self,
            balance_collection,
            income_collection,
            dividents_collection,
            base_temp_express,
            base_grow_express
    ):
        self.balance_col = balance_collection
        self.income_col = income_collection
        self.dividents_col = dividents_collection
        self.express_col = base_temp_express
        self.grow_col = base_grow_express
        self.score_col = base_score_table

    def write_temp_express_analiz(self, data):
        new_obj = {}
        new_obj['_id'] = data['ticket']
        for key in data['years_data']:
            new_obj[key] = {}
            for i in range(len(data['years'])):
                new_obj[key].update(
                    {data['years'][i]: data['years_data'][key][i]}
                )
        self.express_col.insert_single(new_obj)

    def write_express_grow_data(self, all_data):

        for data in all_data:
            new_obj = {}
            data_express, grow_data = data
            self.grow_col.insert_single(grow_data)
            new_obj['_id'] = data_express['ticket']
            for key in data_express['years_data']:
                new_obj[key] = {}
                for i in range(len(data_express['years'])):
                    new_obj[key].update(
                        {data_express['years'][i]: data_express['years_data'][key][i]}
                    )
            self.express_col.insert_single(new_obj)

    def write_grow_data(self, obj):
        self.grow_col.insert_single(obj)

    def compound_interest(self, last_val, first_val, period):
        value = (last_val / first_val)
        if value < 0:
            return -(abs(value)**(1/period)) - 1
        return value ** (1 / period) - 1

    def get_all_data(self):
        all_income = self.income_col.collection.find()
        for obj in all_income:
            ticket = obj['_id']
            # [-1] because we don't need the latest data (TTM).
            total_revenue = list(obj['Total Revenue'].values())[:-1]
            if 'Total Operating Profit/Loss' in obj.keys():
                total_income_operation = list(
                    obj['Total Operating Profit/Loss'].values()
                )[:-1]
            else:
                total_income_operation = list(
                    obj['Net Income from Continuing Operations'].values()
                )[:-1]
            stockholders_income = list(
                obj['Net Income Available to Common Stockholders'].values()
            )[:-1]
            total_EPS = list(obj['Basic EPS'].values())[:-1]
            actual_len = len(total_revenue)
            grow_revenue = self.compound_interest(
                total_revenue[-1],
                total_revenue[0],
                len(total_revenue) - 1
            )
            grow_EPS = self.compound_interest(
                total_EPS[-1],
                total_EPS[0],
                len(total_EPS) - 1
            )
            operation_margin = list(
                round(total_income_operation[i] / total_revenue[i], 5) for i in range(len(total_revenue))
            )
            profit_margin = list(
                round(stockholders_income[i] / total_revenue[i], 5) for i in range(len(total_revenue))
            )
            grow_operation_margin = sum(operation_margin)/len(operation_margin)
            grow_profit_margin = sum(profit_margin)/len(profit_margin)
            try:
                ticket_balance = self.balance_col.collection.find({'_id': ticket})[0]
            except (KeyError, IndexError):
                my_logger(message='ticket no exist in Balance collection')
            total_assets = list(
                ticket_balance['Total Assets'].values()
            )[:actual_len]
            total_liabilities = list(ticket_balance['Total Liabilities'].values())[:actual_len]
            shareholders_equity = list(
                round(total_assets[i] - total_liabilities[i], 5) for i in range(actual_len))
            # средний рост собственных средств
            grow_shareholders_equity = self.compound_interest(
                shareholders_equity[-1],
                shareholders_equity[0],
                len(shareholders_equity) - 1
            )
            try:
                ticket_dividents = self.dividents_col.collection.find({'_id': ticket})[0]
            except (KeyError, IndexError):
                my_logger(message='ticket no exist in Dividents collection')
            trailing_dividend = list(ticket_dividents['Trailing Dividend Yield %'].values())[:actual_len]
            buyback_yield = list(
                ticket_dividents['Buyback Yield %'].values()
            )[:actual_len]
            # ср.процент отдачи в виде див.
            grow_dividents = sum(trailing_dividend)/(actual_len*100)
            # ср. процент buyback
            grow_buyback = sum(buyback_yield)/(actual_len*100)
            debt_level = list(
                round(total_liabilities[i] / total_assets[i], 5) for i in range(actual_len)
            )  # уровень долга
            grow_debt_level = sum(debt_level) / len(debt_level)
            ROE = list(
                round(stockholders_income[i] / shareholders_equity[i], 5) for i in range(actual_len)
            )
            ROA = list(
                round(stockholders_income[i] / total_assets[i], 5) for i in range(actual_len)
            )
            grow_ROE = sum(ROE) / len(ROE)
            grow_ROA = sum(ROA) / len(ROA)
            use_profit = sum(
                [grow_shareholders_equity, grow_dividents, grow_buyback]
            )
            dynamics_operation_margin = self.dynamic(operation_margin)
            dynamic_profit_margin = self.dynamic(profit_margin)
            all_years = list(
                year for year in obj['Total Revenue'] if year != 'TTM'
            )
            yield (
                {
                    'ticket': ticket,
                    'years': all_years,
                    'years_data': {
                                'Shareholders’ Equity': shareholders_equity,
                                'operation_margin': operation_margin,
                                'profit_margin': profit_margin,
                                'debt_level': debt_level,
                                'ROE': ROE,
                                'ROA': ROA,
                              }
                },
                {
                    '_id': ticket,
                    'grow_revenue': grow_revenue,
                    'grow_EPS': grow_EPS,
                    'grow_dividents': grow_dividents,
                    'grow_buyback': grow_buyback,
                    'grow_shareholders_equity': grow_shareholders_equity,
                    'grow_operation_margin': grow_operation_margin,
                    'dynamics_operation_margin': dynamics_operation_margin,
                    'grow_profit_margin': grow_profit_margin,
                    'dynamics_profit_margin': dynamic_profit_margin,
                    'grow_debt_level': grow_debt_level,
                    'grow_ROE': grow_ROE,
                    'grow_ROA': grow_ROA,
                    'use_of_profit': use_profit,
                    'period': actual_len
                }
            )

    def get_score(self):
        all_grow = self.grow_col.collection.find()
        for obj in all_grow:
            score_obj = {}
            score = 0
            score_obj['_id'] = obj['_id']

            for key in self.score_table:
                if obj[key] <= self.score_table[key][0][0]:

                    score += -1 * self.score_table[key][1]
                    score_obj[key] = -1 * self.score_table[key][1]
                    continue
                elif obj[key] >= self.score_table[key][0][1]:

                    score += 1 * self.score_table[key][1]
                    score_obj[key] = 1 * self.score_table[key][1]
                    continue
                score_obj[key] = 0
            score_obj['score'] = score
            self.score_col.insert_single(score_obj)


if __name__ == '__main__':

    analiz = ExpressAnaliz(
        base_balance,
        base_income,
        base_dividents,
        base_temp_express,
        base_grow_express
    )
    all_data = analiz.get_all_data()
    analiz.write_express_grow_data(all_data)
    analiz.get_score()
