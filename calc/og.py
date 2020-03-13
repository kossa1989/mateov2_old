from calc.base_calc import Calc

class OgCalc(Calc):
    """Stores information related to OG"""
    def prepare_og(self):
        og_prep = self.tar
        og_prep['czas_hosp'] = og_prep['data_zak']-og_prep['data_przyj'] ## <--- trzeba w tabeli moze zmienić nazwę na data przyjęcia, końca hospitalizacji

        try:
            og_prep['czas_hosp'] = og_prep['czas_hosp'].dt.days
        except AttributeError:
            "jeżeli nie ma attr dt czyli odejmowanie wyszło że jest int'em a nie timedelta"
            pass

        og_join_czas = og_prep.groupby(self.kwargs['case_group'])['czas_hosp'].mean().reset_index(name='czas_hosp')
        og_join_wiek = og_prep.groupby(self.kwargs['case_group'])['wiek'].mean().reset_index(name='wiek')
        og_final = og_join_wiek.merge(og_join_czas, on=self.kwargs['case_group'])
        self.rownumeq(og_final, og_join_wiek)
        self.rownumeq(og_final, og_join_czas)
        if 'nr_ks' in self.kwargs['case_group']:
            # if nr_ks is included in grouping, adds more information that should be passed to tariff df
            og_join = og_prep.groupby(self.kwargs['case_group'])['czas_hosp'].mean().reset_index(name='czas_hosp')
            og_final = og_prep.drop(columns=['czas_hosp']).merge(og_join, on=self.kwargs['case_group'])
            self.rownumeq(og_final, og_prep)

        self.og = og_final

    def create_tar(self):
        super(OgCalc, self).create_tar()
        self.prepare_og()
