import pandas as pd
import math

# скрипт читает файл в таблицу пандас
# 1) разбивает excel документ на словарь таблиц из эксель листов
# 2) выкидываем из таблицы повторные колонки с днями недели
# 3) выкидываем из таблицы повторные строки с именами преподов
# 4) в майне разбиваем таблицу на ячейки, у каждой ячейки есть 3 координаты 
# - день недели, 
# - время начала пары, 
# - имя препода.
# 5) сохраняет бинарно словарь


class PsutiToDictParser(object):
    """
    TODO
    """
    WEEKDAY_KEYS = 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'
    PAIRTIME_KEYS = '8:10', '9:55', '11:40', '13:35', '15:20', '17:05'

    def __init__(self, xlsx_name) -> None:
        super().__init__()
        self.xlsx_pages = self.get_xlsx_pages_map(xlsx_name)
        self.schedule = dict()


    def drop_weekday_columns(self, page):
        """
        TODO
        """
        days_column = page.iloc[:, 0]

        columns_to_delete = list()
        for i in range(2, page.shape[1]):
            if any(page.iloc[:, i].eq(days_column)):
                _name = page.iloc[:, i].name
                columns_to_delete.append(_name)
                _name = page.iloc[:, i + 1].name
                columns_to_delete.append(_name)

        page.drop(columns=columns_to_delete, inplace=True)        


    def drop_teachernames_rows(self, page):
        """
        TODO
        """
        rows_to_delete = list()
        teachers_row = page.iloc[0]

        for i in range(1, page.shape[0]):
            if any(page.iloc[i].eq(teachers_row)):
                rows_to_delete.append(i)

        page.drop(index=rows_to_delete, inplace=True)

        page.rename(columns={page.iloc[:, 0].name: 'weekday'}, inplace=True)
        page.rename(columns={page.iloc[:, 1].name: 'time'}, inplace=True)


    def define_teachernames_indexes(self, page):
        """
        TODO
        """
        teachers_row = page.iloc[0]
        teachers_indexes = dict()
        first_index = None
        tkey = None
        for i, e in enumerate(teachers_row):
            if not isinstance(e, (float,)):
                last_index = i
                if not first_index is None:
                    teachers_indexes[tkey] = (first_index, last_index)
                first_index = i
                tkey = e

        if tkey:
            teachers_indexes[tkey] = (first_index, teachers_row.size)
        return teachers_indexes


    def decompose_by_weekday(self, page):
        """
        TODO
        """
        result = list()
        first_index = None
        for i, wd in enumerate(page.iloc[:, 0]):
            if isinstance(wd, (float,)) and math.isnan(wd):
                pass
            else:
                last_index = i
                if last_index > 1:
                    result.append(page.iloc[first_index : last_index])
                first_index = i
        result.append(page.iloc[first_index : page.shape[0]])
        return result


    def decompose_by_time(self, day_df):
        """
        TODO
        """
        result = list()
        first_index = None
        for i, pairtime in enumerate(day_df.iloc[:, 1]):
            if isinstance(pairtime, (float,)) and math.isnan(pairtime):
                pass
            else:
                last_index = i
                if last_index > 1:
                    result.append(day_df.iloc[first_index : last_index])
                first_index = i
        result.append(day_df.iloc[first_index : day_df.shape[0]])
        return result        


    def decompose_by_teacher(self, pairtime_df, teachers_indexes):
        """
        TODO
        """
        result = list()

        for col1, col2 in teachers_indexes.values():
            result.append(pairtime_df.iloc[:, col1 : col2])
        return result
        
    def get_xlsx_pages_map(self, xlsx_filepath: str):
        """
        TODO
        """
        xlsx = pd.ExcelFile(xlsx_filepath)

        df_map = dict()
        for sheet_name in xlsx.sheet_names:
            df_map[sheet_name] = xlsx.parse(sheet_name)        

        return df_map

    def process_xlsx_book(self, xlsx_pages=None):
        if xlsx_pages:
            self.xlsx_pages = xlsx_pages

        for pname in self.xlsx_pages:
            page = self.xlsx_pages[pname]

            self.drop_weekday_columns(page)
            self.drop_teachernames_rows(page)
            teachers_indexes = self.define_teachernames_indexes(page)
            
            schedule = dict()
            weekdays_df = self.decompose_by_weekday(page)
            weekday_keys = self.WEEKDAY_KEYS
            for wkey, wdf in zip(weekday_keys, weekdays_df):
                schedule[wkey] = dict()
                pairtimes_df = self.decompose_by_time(wdf)
                pairtime_keys = self.PAIRTIME_KEYS

                for pkey, pdf in zip(pairtime_keys, pairtimes_df):
                    schedule[wkey][pkey] = dict()
                    teacher_df = self.decompose_by_teacher(pdf, teachers_indexes)

                    i = 0
                    for tkey, tdf in zip(teachers_indexes.keys(), teacher_df):

                        cell = list()
                        for index, line in tdf.iterrows():
                            line = (' '.join([str(e) if not isinstance(e , (float, )) else '' for e in line.values]))
                            cell.append(line)

                        if any(cell):
                            schedule[wkey][pkey][tkey] = cell

                        i += 1

            self.schedule[pname] = schedule  

        return self.schedule


    @staticmethod    
    def save_as_binary_file(obj, path: str):
        """
        TODO
        """
        import pickle
        with open(path, 'wb') as output:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)    


if __name__ == '__main__':
    parser = PsutiToDictParser(xlsx_name := 'src.xlsx')
    parser.process_xlsx_book()
    parser.save_as_binary_file(parser.schedule, 'src.dump')
