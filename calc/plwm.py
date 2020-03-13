

### Wzięte z PL WM -> propzycja rozdzielenia tego - PK

import numpy as np
import pandas as pd

from calc.base_calc import Calc
#from database.db import engine as engine_daneb # zmieniono z oryginalem
from database.db import DbEngine
engine_daneb = DbEngine.create_engine('pytar')

# TODO trzeba dopytać Eli/Uli czy metoda, która wylica tar_sr_il, bedzie jeszcze potrzeban. Trzeba potem podjąc decyzję co dalej z rozdziałem tego

class PlWmPrCalc(Calc):
    def __init__(self, *args, **kwargs):
        super(PlWmPrCalc, self).__init__(*args, **kwargs)
        if self.table_type.lower() == 'pl':
            self.file_prices = self.kwargs['pl_prices']
            self.file_quantity = self.kwargs['pl_quantity']
        elif self.table_type.lower() == 'wm':
            self.file_prices = self.kwargs['wm_prices']
            self.file_quantity = self.kwargs['wm_quantity']
        if self.table_type.lower() in ['pl', 'wm']:
            self.pricelist_table = f'{self.kwargs["schema"]}.om'
            self.pricelist_col_names = self.kwargs['om_prices']


    def create_pricelist(self):
        self.pricelist_join = self.create_join(self.file_prices, self.pricelist_col_names)
        self.cols = ','.join(self.file_prices)
        self.table_name_pricelist = 'tmp.tar_pricelist_%s_%s' % (self.table_type, self.uid)

        self.create_index(engine_daneb, self.pricelist_table, self.pricelist_col_names)
        self.create_index(engine_daneb, self.table_name, self.file_prices)

        # --===!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!===--
        """ ABC -> zmaina w przyszlości na DB - PK """
        query_sql = """
                create table {table_name_pricelist} as
                select t2.*
                from (select distinct {cols} from {table_name}) t1 inner join {pricelist_table} t2 on {pricelist_join}
        """.format(**self.__dict__)

        self.execute_query(engine_daneb, query_sql)

        self.raw_pricelist = pd.read_sql('select * from %s' % self.table_name_pricelist, engine_daneb)
        self.raw_pricelist = self.ensure_dtypes(self.raw_pricelist)
        self.raw_pricelist.columns = self.raw_pricelist.columns.str.lower()

    def calc_from_pricelist(self):
        """Calculates prices from pricelist (OM)."""
        self.create_pricelist()
        b0 = self.raw_pricelist[['wartosc', 'liczba_zakup_opak', 'liczba_jedn_miary'] + self.pricelist_col_names]
        b0 = b0.assign(opakowania=(
                    b0.loc[:, 'liczba_zakup_opak'].astype(np.float32) * b0.loc[:, 'liczba_jedn_miary'].astype(
                np.float32))) # Przypisuje kolumnę i liczy cenę -> zastępuje stare wartości - PK
        b0 = b0.groupby(self.kwargs['om_prices']).sum()
        b = b0.assign(cena_om=b0.loc[:, 'wartosc'] / b0.loc[:, 'opakowania'])
        b = b.reset_index()
        self.pricelist_prices = b[self.pricelist_col_names + ['cena_om']]

    def add_pricelist(self):
        """Adds prices from pricelist OM to tar_sr_il."""
        self.tar_sr_il = self.tar_sr_il.merge(self.pricelist_prices, how='left', left_on=self.file_prices,
                                              right_on=self.pricelist_col_names)
        if (self.tar_sr_il['cena_om'].isnull()).any():
            self.messages['warnings'].append(f'Do pliku {self.table_type} dodają się puste ceny z OM.')
        self.tar_sr_il = self.tar_sr_il.drop(self.kwargs['om_prices'], axis=1)

    def calc_from_unit_price(self):
        """Calculates prices from unit price (prices from files PL, WM)"""
        self.create_tar()
        b = self.tar[['koszt_jednostki', ] + self.file_prices + self.kwargs['case_group'] + [self.quantity_col]]
        b_a = b[b[self.quantity_col] != 0]
        bavg = b_a.groupby(self.kwargs['case_group'] + self.file_prices).apply(
            lambda x: np.average(x['koszt_jednostki'], weights=x[self.file_quantity]))
        b1 = bavg
        b2 = b1.reset_index().rename(columns={0: 'cena_z_pliku'})
        self.unit_prices = b2

    def add_unit_price(self):
        """Adds unit price to PL/WM table."""
        self.tar_sr_il = self.tar_sr_il.merge(self.unit_prices, how='left',
                                              on=self.file_prices + self.kwargs['case_group'])

    def calc_tariff(self):
        self.tariff = self.tar_sr_il.groupby(self.kwargs['case_group'])['koszt_zdarzenia'].sum().reset_index(
            name="suma_%s" % self.table_type)

    # Liczy srednią wystąpień w przypadku (zajmuje się też not nullami, mask zastepuje je) - PK
    def generate_event_cost(self):
        tar_sr_il = self.tar_sr_il
        tar_sr_il['sr_wyst_w_przyp'] = tar_sr_il['sr_wyst_w_przyp'].mask(tar_sr_il['wsp'].notnull(), tar_sr_il['wsp'])
        tar_sr_il['sr_wyst_w_przyp'] = tar_sr_il['sr_wyst_w_przyp'].mask(tar_sr_il['wsp_dni'].notnull(),
                                                                         tar_sr_il['wsp_dni'] * tar_sr_il['czas_hosp'])

        def scale_groups(tar_sr_il, col):
            """Scale groups rates to sr_wyst_w_przyp. If one specifies grp wsp, method is used to expand groups to
            regular mean of occurences in case.
            """
            # grp code
            sum_past_values = tar_sr_il.groupby('grupa')['sr_wyst_w_przyp'].sum().reset_index()
            tar_sr_il_grp = tar_sr_il.reset_index().merge(sum_past_values, on='grupa',
                                                          suffixes=('', '_groups')).set_index('index')
            # calculate rates to scale sr_wyst_w_przyp
            tar_sr_il_grp['rate_to_scale_sr_wyst_groups'] = (
                        tar_sr_il_grp[col] / tar_sr_il_grp['sr_wyst_w_przyp_groups'])
            # create new sr_wyst_w_przyp for grouped rows
            tar_sr_il_grp['sr_wyst_w_przyp_groups'] = tar_sr_il_grp['rate_to_scale_sr_wyst_groups'] * tar_sr_il_grp[
                'sr_wyst_w_przyp']
            # assign new values to old variable name
            tar_sr_il_grp['sr_wyst_w_przyp'] = tar_sr_il_grp['sr_wyst_w_przyp_groups']
            # select only important cols
            tar_sr_il_grp = tar_sr_il_grp[[i for i in tar_sr_il_grp.columns if not i.endswith('_groups')]]
            # add grouped values to original df
            if col == 'gr_wsp_dni':
                tar_sr_il_grp['sr_wyst_w_przyp'] = tar_sr_il_grp['sr_wyst_w_przyp'] * tar_sr_il_grp['czas_hosp']
            tar_sr_il_join = tar_sr_il.join(tar_sr_il_grp, rsuffix='_groups', how='left')
            # assign new values to tar_sr_il
            tar_sr_il_join['sr_wyst_w_przyp'] = tar_sr_il_join['sr_wyst_w_przyp'].mask(
                tar_sr_il_join['sr_wyst_w_przyp_groups'].notnull(), tar_sr_il_join['sr_wyst_w_przyp_groups'])
            # select relevant cols
            tar_sr_il = tar_sr_il_join[[i for i in tar_sr_il_join.columns if not i.endswith('_groups')]]

            return tar_sr_il

        tar_sr_il = scale_groups(tar_sr_il, 'gr_wsp')
        tar_sr_il = scale_groups(tar_sr_il, 'gr_wsp_dni')
        self.tar_sr_il = tar_sr_il


class PlWmCalc(PlWmPrCalc):
    def create_tar_sr_il(self):
        super(PlWmCalc, self).create_tar_sr_il()
        self.tar_sr_il['pl_wm'] = np.NaN # uzupełnia DF ciągiem logicznym potrzebnym do indexowania pl_wm - PK

    def generate_event_cost(self):
        """Adds event costs."""
        super(PlWmCalc, self).generate_event_cost()
        price_col = self.kwargs['price_priority']
        secondary_col = 'cena_om' if price_col != 'cena_om' else 'cena_z_pliku'

        self.tar_sr_il['cena_do_analizy'] = np.where(self.tar_sr_il[price_col].isnull(), self.tar_sr_il[secondary_col],
                                                     self.tar_sr_il[price_col]) # np.where zwraca alement po spełnieniu warunków PK
        self.tar_sr_il['koszt_zdarzenia'] = self.tar_sr_il['cena_do_analizy'] * self.tar_sr_il['sr_wyst_w_przyp']
        self.summarize_event_costs()


class PlCalc(PlWmCalc):
    pass


class WmCalc(PlWmCalc):
    def __init__(self, *args, **kwargs):
        super(WmCalc, self).__init__(*args, **kwargs)
        self.wm_unit_price = self.kwargs['wm_unit_price']
