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

# patterns
depart_ptrn = r'[А-Яа-я]{2,}'
teacher_ptrn_FIO = r'[А-Я][А-Яа-я]{2,}\s{1,}[А-Я][.]{0,1}\s{0,}[А-Я][.]{0,1}'
teacher_ptrn_FI = r'[А-Я][А-Яа-я]{2,}\s{1,}[А-Я][.]{0,1}'
type_ptrn = r'(\s|-)(пр|лаб|лб|лк|лек)[.]{0,1}'
grp_ptrn = r'[А-Яа-я]{2,}\s{0,1}-\s{0,1}\d{2}'
aud_ptrn = r'(а.{0,4}?\d{3}|а.{0,4}?-\d{2,3}|ЦДП|ЦИОТ)'
name_ptrn = r'^.{0,}?\d'
evenodd_ptrn =r'(чет|неч)'


def load_obj(path):
    with open(path, 'rb') as input:
        return pickle.load(input)

xclsrc = load_obj('src.dump')

def parse_department(ptrn, dkey):
    department = re.search(ptrn, dkey)
    if department:
        return department.group(0)
    else:
        this_error = f'строка: {dkey}, шаблон: {ptrn}'
        print(this_error)
        raise ValueError(f'Кафедра не найдена!\n{this_error}\n')


def parse_teachername(tkey, dep):

    tnamesearch = re.search(teacher_ptrn_FIO, tkey)
    if tnamesearch:
        tname = tnamesearch.group(0)
    else:
        tnamesearch = re.search(teacher_ptrn_FI, tkey)
        if tnamesearch:
            tname = tnamesearch.group(0)
        else:
            tname = f'{dep} {tkey.strip()}'
    
    return tname                

def parse_subjtype(ptrn, line):

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

def parse_subjname(ptrn, line):
    res = re.findall(ptrn, line)
    if res:
        sname = res[0][:-1].strip()
    else:
        sname = line.strip()
    return sname

def prepare_for_parsing(line):
    line = line.replace(' -', '-', -1).replace('- ', '-', -1)
    return line


def parse_auditory(ptrn, line):
    res = re.findall(ptrn, line)
    if res:
        if len(res) > 1:
            aud = res
        else:
            aud = res[0]
    else:
        aud = 'aud not found'
    return aud

def parse_oddeven(ptrn, line):
    res = re.findall(ptrn, line)
    if res:
        if len(res) > 1:
            evenodd = res
        else:
            evenodd = res[0]
    else:
        evenodd = 'full'
    return evenodd

def solve_paralel_first_digit(kurs_digit):
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


def parse_stgroup(grp_ptrn, subjcell, all_groups, subtype):


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
                    fd = solve_paralel_first_digit(c)
                    if f'{shortname}-{fd}' in fullname:
                        grps.add(fullname)

        res = re.findall(grp_ptrn, subjcell)
    else:
        for group in all_groups:
            if group in subjcell.upper():
                grps.add(group)
    grps = list(grps)
    return grps

def list_all_groups(ptrn, xclsrc):
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

                        subjcell = prepare_for_parsing(subjcell)
                        res = re.search(ptrn, subjcell)
                        if res:
                            res_str = res.group(0)
                            all_groups.add(res_str.upper())

    return all_groups


def cellparse():
    result = list()

    all_grps = list_all_groups(grp_ptrn, xclsrc)
    all_grps = list(all_grps)

    for dkey in xclsrc:
        for wkey in xclsrc[dkey]:
            for pkey in xclsrc[dkey][wkey]:
                for tkey in xclsrc[dkey][wkey][pkey]:
                    cell = xclsrc[dkey][wkey][pkey][tkey]
                    
                    for i in range(2, len(cell), 2):
                        subjcell = cell[i : i+2]

                        line1 = subjcell[0].strip()
                        if len(line1) > 3:
                            if len(subjcell) > 1:
                                subjcell = line1 + ' ' + subjcell[1].strip()
                            else:
                                subjcell = line1
                        else: continue

                        subjcell = prepare_for_parsing(subjcell)

                        jsobj = dict()
                        jsobj['department'] = parse_department(depart_ptrn, dkey)
                        jsobj['teacher_name'] = parse_teachername(tkey, jsobj['department'])
                        jsobj['weekday'] = wkey
                        jsobj['sub_time'] = pkey
                        jsobj['sub_name'] = parse_subjname(name_ptrn, line1)
                        jsobj['sub_type'] = parse_subjtype(type_ptrn, subjcell)
                        jsobj['st_group'] = parse_stgroup(grp_ptrn, subjcell, all_grps, jsobj['sub_type'])
                        jsobj['au_number'] = parse_auditory(aud_ptrn, subjcell)
                        jsobj['odd_even'] = parse_oddeven(evenodd_ptrn, subjcell)
                        result.append(jsobj)
        
    return result

result = cellparse()

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)