from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from web_site.analysis.models import Analyses
from unittest import mock
# Create your tests here.

class AnalysisTestcase(TestCase):
    analytic_template = 'wb17'
    qsm = """
            create table %s as
            select t1.nr_ks, t1.kod_sw, t1.kod_prod, '1' as kod_dod
            from {0}.sm t1 inner join {0}.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks
            where kod_prod like "5.51.01.0005047" limit 1
    """
    if analytic_template=='wb17':
        qsm = qsm.format('wb17')

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('sadf',password='*&(@#^GFD#^*@DGgvC^GFgd7&T#')
        super(AnalysisTestcase, cls).setUpClass()

    def test_analysis_runs(self):
        # path should be any writable path just to test xlsx write
        path = r'T:\organizacyjne_robocze\012_Taryfikator\test'
        c = Client()
        c.force_login(self.user)
        c.get(reverse('analysis:index'))
        c.post(reverse('analysis:index'), data={'path':path,
                                                'name':'testowy taryfikator',
                                                'query_sm':self.qsm})
        my_analyses = Analyses.objects.filter(user=self.user)
        self.assertEqual(len(my_analyses),1)
