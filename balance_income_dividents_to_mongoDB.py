import copy
import os
import shutil

import pandas
from dotenv import load_dotenv
from logger import my_logger
from MongoBasse import base_balance, base_dividents, base_income

load_dotenv()


class DirsFiles:
    """get_files: return all files in path class."""

    def __init__(self, path=None):
        self.path = path

    def __get_files(self, path):
        return (
            file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))
        )

    def get_files(self):
        return self.__get_files(self.path)


class FileToMongo:
    """Writes financial statements to the local MongoDb database.

    Algorithm from the book: "65 Steps From Zero To Pro" | Barshevsky Grigory

    Data: MorningStar(Premium accaunt.) -
    Income Statement_Annual_As Originally Reported,
    Balance Sheet_Annual_As Originally Reported),
    Dividents data.
    """

    intresting_docs = {
        'Balance': [
            'Total Assets',
            'Total Liabilities',
        ],
        'Income': [
            'Total Revenue',
            'Total Operating Profit/Loss',
            'Net Income from Continuing Operations',
            'Net Income Available to Common Stockholders',
            'Basic EPS'
        ],
        'Dividents': [
            'Trailing Dividend Yield %',
            'Buyback Yield %',
        ]
    }

    exel_ext = ('.xls', '.xlm',)

    def __init__(self, path):
        self.path = path
        self.files = DirsFiles(path)

    def exel_data_frame(self, file):
        rez = {}
        clear_data = {}
        actual_intresting_doc = {}
        if os.path.splitext(file)[1] in FileToMongo.exel_ext:
            file_data_frame = pandas.read_excel(
                os.path.join(self.path, file), header=0, index_col=0
            )
            # We get the lines of interest.
            # Different companies have slightly different reporting headers.
            for title in FileToMongo.intresting_docs:
                if title in file:
                    rows = list(file_data_frame.iterrows())
                    try:
                        for key in FileToMongo.intresting_docs[title]:
                            for row in rows:
                                if key == row[0].rstrip().lstrip():
                                    actual_intresting_doc.update({row[0]: 0})
                                    break
                    except KeyError:
                        my_logger(
                            self.__class__.__name__,
                            method=self.exel_data_frame.__name__,
                            message=f'{title} not in {file}'
                        )
                    # Filling objects with data from rows of interest.
                    for key in actual_intresting_doc:
                        raw_data = file_data_frame.loc[key].to_dict()
                        for key_raw in raw_data:
                            data = raw_data[key_raw]
                            if isinstance(data, dict):
                                data = list(data.values())[0]
                            if data == '—':
                                data = 0
                            if isinstance(data, str):
                                clear_data[str(key_raw)] = float(
                                    data.replace(',', '')
                                )
                            else:
                                clear_data[str(key_raw)] = float(data)
                        rez.update({key.lstrip(): copy.deepcopy(clear_data)})
                    rez.update(
                        {'_id': file_data_frame.T.axes[1].name.split('_')[0]}
                    )
                    rez.update({'Collection': title})
            try:
                shutil.move(
                    os.path.join(path, file),
                    os.path.join(path, 'old', rez['_id'] + '_' + file),
                )
            except PermissionError as e:
                my_logger(
                    self.__class__.__name__,
                    method='shutil.move',
                    file=file,
                    message=e
                )
            return rez

        else:
            my_logger(
                self.__class__.__name__,
                method=self.exel_data_frame.__name__,
                file=file,
                message='extension not support read_exel pandas'
            )


if __name__ == '__main__':

    mongo_dict = {
        'Balance': base_balance,
        'Income': base_income,
        'Dividents': base_dividents,
    }
    path = r'c:\exel'
    parse_work = FileToMongo(path=path)
    all_files = parse_work.files.get_files()
    mongo_temp = []
    for file in all_files:
        temp = parse_work.exel_data_frame(file)
        if temp:
            mongo_temp.append(temp)
    for mongo in mongo_temp:
        a = mongo_dict[mongo['Collection']].insert_single(mongo)
