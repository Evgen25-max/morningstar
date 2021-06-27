import pymongo
from logger import my_logger


class MongoBase:
    """Save_data to mongoDB.

    database: morningstar.
    collection:
    Balance - interesting data from balance sheet
    Income - interesting data from income sheet
    Dividents - interesting data from divident sheet
    temp_express_analiz -
    grow_data - average indicators
    score - final score company
    """

    def __init__(self, db, collect, address='localhost', port=27017):
        self.client = pymongo.MongoClient(address, port)
        self.db = self.client[db]
        self.collection = self.db[collect]

    def insert_single(self, obj):
        try:
            self.collection.insert_one(obj)
        except pymongo.errors.DuplicateKeyError as error:
            my_logger(
                self.__class__.__name__,
                method=self.insert_single.__name__,
                error=error,
            )


base_balance = MongoBase('morningstar', 'Balance')
base_income = MongoBase('morningstar', 'Income')
base_dividents = MongoBase('morningstar', 'Dividents')
base_temp_express = MongoBase('morningstar', 'temp_express_analiz')
base_grow_express = MongoBase('morningstar', 'grow_data')
base_score_table = MongoBase('morningstar', 'score')
