import pandas as pd
import math

# скрипт читает файл в таблицу пандас
# 1) выкидываем из таблицы повторные колонки с днями недели
# 2) выкидываем из таблицы повторные строки с именами преподов
# 3) в майне разбиваем таблицу на ячейки, у каждой ячейки есть 3 координаты 
# - день недели, 
# - время начала пары, 
# - имя препода.

class PsutiScheduleParser(object):
    """
    TODO
    """
    def __init__(self, page) -> None:
        super().__init__()
        # self.xlsx_path = xlsx_path
        self.page = page


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
        


if __name__ == '__main__':
    xlsx_name = 'src.xlsx'

    xlsx = pd.ExcelFile(xlsx_name)

    # Now you can list all sheets in the file
    # print(xlsx.sheet_names)
    # ['house', 'house_extra', ...]

    # to read just one sheet to dataframe:
    # df = pd.read_excel(file_name, sheetname="house")

    # Read all sheets and store it in a dictionary. Same as first but more explicit.

    # # to read all sheets to a map
    df_map = dict()
    for sheet_name in xlsx.sheet_names:
        df_map[sheet_name] = xlsx.parse(sheet_name)

    for pname in df_map:
        obj = df_map[pname]


        obj = PsutiScheduleParser(obj)
        obj.drop_weekday_columns(obj.page)
        obj.drop_teachernames_rows(obj.page)
        teachers_indexes = obj.define_teachernames_indexes(obj.page)
        
        schedule = dict()
        weekdays_df = obj.decompose_by_weekday(obj.page)
        weekdays_key = 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'
        for wkey, wdf in zip(weekdays_key, weekdays_df):
            schedule[wkey] = dict()
            pairtimes_df = obj.decompose_by_time(wdf)
            pairtimes_key = '8:10', '9:55', '11:40', '13:35', '15:20', '17:05'

            for pkey, pdf in zip(pairtimes_key, pairtimes_df):
                schedule[wkey][pkey] = dict()
                teacher_df = obj.decompose_by_teacher(pdf, teachers_indexes)

                i = 0
                for tkey, tdf in zip(teachers_indexes.keys(), teacher_df):
                    # schedule[wkey][pkey][tkey] = tdf
                    # print(wkey, pkey, tkey)
                    # print(tdf)

                    # print(f'{i})')

                    cell = list()
                    for index, line in tdf.iterrows():
                        line = (' '.join([str(e) if not isinstance(e , (float, )) else '' for e in line.values]))
                        cell.append(line)

                    if any(cell):
                        schedule[wkey][pkey][tkey] = cell

                    i += 1

        df_map[pname] = schedule

        import pickle

        def save_obj(obj, path):
            with open(path, 'wb') as output:
                pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

        save_obj(df_map, 'src.dump')


# print(page.info())
# for i, row in page.iterrows():
#     print(row)

# days = page.iloc[:, 0]

# columns_to_delete = list()
# for i in range(2, page.shape[1]):
#     if any(page.iloc[:, i].eq(days)):
#         _name = page.iloc[:, i].name
#         columns_to_delete.append(_name)
#         _name = page.iloc[:, i + 1].name
#         columns_to_delete.append(_name)

# page.drop(columns=columns_to_delete, inplace=True)


# rows_to_delete = list()
# teachers_row = page.iloc[0]
# print(teachers_row)
# for i in range(1, page.shape[0]):
#     if any(page.iloc[i].eq(teachers_row)):
#         rows_to_delete.append(i)

# page.drop(index=rows_to_delete, inplace=True)

# page.rename(columns={page.iloc[:, 0].name: 'weekday'}, inplace=True)
# page.rename(columns={page.iloc[:, 1].name: 'time'}, inplace=True)

# print(page)

def hide():
    xlsx = pd.ExcelFile(xlsx_name)

    # Now you can list all sheets in the file
    print(xlsx.sheet_names)
    # ['house', 'house_extra', ...]

    # to read just one sheet to dataframe:
    # df = pd.read_excel(file_name, sheetname="house")

    # Read all sheets and store it in a dictionary. Same as first but more explicit.

    # # to read all sheets to a map
    df_map = dict()
    for sheet_name in xlsx.sheet_names:
        df_map[sheet_name] = xlsx.parse(sheet_name)

    for key in df_map:
        page = df_map[key]
        print(page.shape)
        break