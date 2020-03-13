patient = {
    'path':'',
    'query_sm':"""create table %s as select t1.nr_ks, t1.kod_sw, t1.kod_prod from wb17.sm t1 inner join wb17.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks where kod_prod like "5.51.01.0016006" """,
    'name':'',
    'schema':'wb17',
    'permissive':True,
    'case_group':'kod_prod,kod_sw,nr_ks'
}

provider = {
    'path':'',
    'query_sm':"""create table %s as select t1.nr_ks, t1.kod_sw, t1.kod_prod from wb17.sm t1 inner join wb17.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks where kod_prod like "5.51.01.0016006" """,
    'name':'',
    'schema':'wb17',
    'permissive':True,
    'case_group':'kod_prod,kod_sw'
}

drg = {
    'path':'',
    'query_sm':"""create table %s as select t1.nr_ks, t1.kod_sw, t1.kod_prod from wb17.sm t1 inner join wb17.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks where kod_prod like "5.51.01.0016006" """,
    'name':'',
    'schema':'wb17',
    'permissive':True,
    'case_group':'kod_prod'
}

templates = {'na_pacjenta':patient, 'na_kod_sw':provider, 'na_kod_prod':drg}