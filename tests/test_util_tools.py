import unittest

import pandas as pd

from pytar_calc.calc.base_calc import UtilTools, Calc


class UtilToolsTestCase(unittest.TestCase):
    def test_weighted_quantile(self):
        data = {'var': [10, 1, 10, 1],
                'weights': [99, 1, 0, 0],
                'groups': ['g1', 'g1', 'g2', 'g2']
                }
        df = pd.DataFrame(data)
        values = df['var'].values
        weights = df['weights'].values
        # check if no weights provided
        quantiles = UtilTools.weighted_quantile(values, [0.25, 0.5, 0.75, 0.99])
        self.assertEqual(quantiles, [1, 1, 10, 10])
        # check when weights are used
        quantiles = UtilTools.weighted_quantile(values, [0.01, 0.09, 0.5], sample_weight=weights)
        self.assertEqual(quantiles, [1, 1, 10])

    def test_weighted_quantile_in_groups(self):
        data = {'var': [10, 1, 100, 1],
                'weights': [9, 100, 1, 0],
                'groups': ['g1', 'g1', 'g1', 'g2']
                }
        df = pd.DataFrame(data)
        # no weights
        no_outliers_df = UtilTools.del_outliers_boxplot_calc_mean(df, 'var', ['groups'], )
        self.assertEqual(111 / 3.0, no_outliers_df.iat[0, 1])

        def wquantiles(group, col_name, weight_name, quantile):
            quantiles = UtilTools.weighted_quantile(group[col_name].values, [quantile],
                                                    sample_weight=group[weight_name].values)
            return quantiles[0]

        # with weights
        df_test = df.groupby('groups').apply(wquantiles, 'var', 'weights', quantile=0.5)
        self.assertEqual(df_test.at['g1'], 1)
        df_test = df.groupby('groups').apply(wquantiles, 'var', 'weights', quantile=0.99)
        self.assertEqual(df_test.at['g1'], 100)

    def test_boxplot_with_weighted_quantiles(self):
        data = {'var': [10, 1, 100, 1],
                'weights': [9, 100, 1, 9],
                'groups': ['g1', 'g1', 'g1', 'g2']
                }
        df = pd.DataFrame(data)
        result = UtilTools.del_outliers_boxplot_calc_mean(df, 'var', ['groups'], weights='weights')
        self.assertNotEqual(result.iloc[:, 1].tolist(), [(10 * 9 + 1 * 100 + 100 * 1) / 110, 1])
        self.assertEqual(result.iloc[:, 1].tolist(), [190 / 109, 1.0])
