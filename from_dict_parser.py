import pickle
import json
import re


"""
· Id
Тип данных: int

· time (Время)
Тип данных: time

· subject_name (Название предмета)
Тип данных: text

· is_remotely (дистанционно)
Тип данных: bool (1 – дист. 0 – недист.)

· type (Тип(лк, пр, лб))
Тип данных: text

· audience_number (Номер аудитории)
Тип данных: text

· group (Группа)
Тип данных: text

· teacher_name (Преподаватель)
Тип данных: text

· department (Для вывода расписания для всей кафедры)
Тип данных: text

· day_of_week (день недели, можно цифры от 1 до 7)
Тип данных: int

· isEvenOrOdd (1 – нечёт, 2 – чёт, 0 – чёт/нечёт)
Тип данных: перечесление int 

"""

class PsutiFromDictParser(object):

    # patterns
    depart_ptrn = r'[А-Яа-я]{2,}'
    teacher_ptrn_FIO = r'[А-Я][А-Яа-я]{2,}\s{1,}[А-Я][.]{0,1}\s{0,}[А-Я][.]{0,1}'
    teacher_ptrn_FI = r'[А-Я][А-Яа-я]{2,}\s{1,}[А-Я][.]{0,1}'
    type_ptrn = r'(\s|-)(пр|лаб|лб|лк|лек)[.]{0,1}'
    grp_ptrn = r'[А-Яа-я]{2,}\s{0,1}-\s{0,1}\d{2}'
    aud_ptrn = r'(а.{0,4}?\d{3}|а.{0,4}?-\d{2,3}|ЦДП|ЦИОТ)'
    name_ptrn = r'^.{0,}?\d'
    evenodd_ptrn =r'(чет|неч)'

    def __init__(self, filepath) -> None:
        super().__init__()
        self.xclsrc = self.load_obj(filepath)

    def load_obj(self, path):
        with open(path, 'rb') as input:
            return pickle.load(input)


    def parse_department(self, ptrn, dkey):
        department = re.search(ptrn, dkey)
        if department:
            return department.group(0)
        else:
            this_error = f'строка: {dkey}, шаблон: {ptrn}'
            print(this_error)
            raise ValueError(f'Кафедра не найдена!\n{this_error}\n')


    def parse_teachername(self, tkey, dep):

        tnamesearch = re.search(self.teacher_ptrn_FIO, tkey)
        if tnamesearch:
            tname = tnamesearch.group(0)
        else:
            tnamesearch = re.search(self.teacher_ptrn_FI, tkey)
            if tnamesearch:
                tname = tnamesearch.group(0)
            else:
                tname = f'{dep} {tkey.strip()}'
        
        return tname                

    def parse_subjtype(self, ptrn, line):

        res = re.search(ptrn, line)
        if res:
            if 'лк' in res.group(0) or 'лек' in res.group(0):
                stype = 'лк'
            elif 'лб' in res.group(0) or 'лаб' in res.group(0):
                stype = 'лб'
            else:
                stype = 'пр'
        else: 
            stype = 'undefined'

        return stype

    def parse_subjname(self, ptrn, line):
        res = re.findall(ptrn, line)
        if res:
            sname = res[0][:-1].strip()
        else:
            sname = line.strip()
        return sname

    def prepare_for_parsing(self, line):
        line = line.replace(' -', '-', -1).replace('- ', '-', -1)
        return line


    def parse_auditory(self, ptrn, line):
        res = re.findall(ptrn, line)
        if res:
            aud = res
        else:
            aud = 'aud not found'
        return aud

    def parse_oddeven(self, ptrn, line):
        res = re.findall(ptrn, line)
        if res:
            if len(res) > 1:
                evenodd = res
            else:
                evenodd = res[0]
        else:
            evenodd = 'full'
        return evenodd

    def solve_paralel_first_digit(self, kurs_digit):
        import datetime
        
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        current_year = 2022
        current_month = 2
        if current_month >= 9:
            first_digit = current_year + 1 - int(kurs_digit)
        else:
            first_digit = current_year - int(kurs_digit)
        
        return str(first_digit)[-1]


    def parse_stgroup(self, grp_ptrn, subjcell, all_groups, subtype):


        grps = set()
        potok = set()
        if subtype == 'лк':
            for fullname in all_groups:
                potok.add(fullname[: fullname.find('-')])
            
            for shortname in potok:
                if shortname in subjcell.upper():
                    for fullname in all_groups:
                        for c in subjcell:
                            if c.isdigit():
                                kurs_number = c
                                break
                        fd = self.solve_paralel_first_digit(c)
                        if f'{shortname}-{fd}' in fullname:
                            grps.add(fullname)

            res = re.findall(grp_ptrn, subjcell)
        else:
            for group in all_groups:
                if group in subjcell.upper():
                    grps.add(group)
        grps = list(grps)
        return grps


    def list_all_groups(self, ptrn, xclsrc):
        all_groups = set()
        for dkey in xclsrc:
            for wkey in xclsrc[dkey]:
                for pkey in xclsrc[dkey][wkey]:
                    for tkey in xclsrc[dkey][wkey][pkey]:
                        cell = xclsrc[dkey][wkey][pkey][tkey]

                        for i in range(2, len(cell), 2):
                            subjcell = cell[i : i+2]
                            line1 = subjcell[0].strip()
                            if line1:
                                if len(subjcell) > 1:
                                    subjcell = line1 + ' ' + subjcell[1].strip()
                                else:
                                    subjcell = line1
                            else: continue

                            subjcell = self.prepare_for_parsing(subjcell)
                            res = re.search(ptrn, subjcell)
                            if res:
                                res_str = res.group(0)
                                all_groups.add(res_str.upper())

        return all_groups


    def cellparse(self):
        result = list()

        all_grps = self.list_all_groups(self.grp_ptrn, self.xclsrc)
        all_grps = list(all_grps)

        for dkey in self.xclsrc:
            for wkey in self.xclsrc[dkey]:
                for pkey in self.xclsrc[dkey][wkey]:
                    for tkey in self.xclsrc[dkey][wkey][pkey]:
                        cell = self.xclsrc[dkey][wkey][pkey][tkey]
                        
                        for i in range(2, len(cell), 2):
                            subjcell = cell[i : i+2]

                            line1 = subjcell[0].strip()
                            if len(line1) > 3:
                                if len(subjcell) > 1:
                                    subjcell = line1 + ' ' + subjcell[1].strip()
                                else:
                                    subjcell = line1
                            else: continue

                            subjcell = self.prepare_for_parsing(subjcell)

                            jsobj = dict()
                            jsobj['department'] = self.parse_department(self.depart_ptrn, dkey)
                            jsobj['teacher_name'] = self.parse_teachername(tkey, jsobj['department'])
                            jsobj['weekday'] = wkey
                            jsobj['sub_time'] = pkey
                            jsobj['sub_name'] = self.parse_subjname(self.name_ptrn, line1)
                            jsobj['sub_type'] = self.parse_subjtype(self.type_ptrn, subjcell)
                            jsobj['st_group'] = self.parse_stgroup(self.grp_ptrn, subjcell, all_grps, jsobj['sub_type'])
                            jsobj['au_number'] = self.parse_auditory(self.aud_ptrn, subjcell)
                            jsobj['odd_even'] = self.parse_oddeven(self.evenodd_ptrn, subjcell)
                            result.append(jsobj)
            
        return result


if __name__ == "__main__":
    result = PsutiFromDictParser('src.dump').cellparse()

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        