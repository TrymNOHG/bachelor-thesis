import pandas as pd
import pytest
from filter_utils import filter_interval, get_hour_from_data_obj, categorize_column, s_to_ms, change_col_type_to_str


print("Testing filter based on interval: ")

@pytest.fixture
def test_df():
    test_data = {
    'node_id': [1, 2, 3, 4, 5],
    'ts': ['2023-11-01 00:00:15.270304', '2023-11-01 00:00:15.463788', '2023-11-01 00:00:15.466253', '2023-11-01 00:00:15.466253', '2023-11-01 00:00:15.466253'],
    'rtt' : [0.018055, 0.019393, 0.061758, 0.036384, 0.023214],
    'network_id' : ['2', '2', '2', '2', '2'],
    'bin_rsrp' : [-141.0, -140, -100, -44, 40],
    'bin_rssi' : [-110, -100, -10, -6, -2],
    'bin_rsrq' : [-21, -20, -10, -3, -2],
    'population' : [11277, 46519, 38364, 14000, 38364]
}
    return pd.DataFrame(test_data)


print("Running filter interval test.")

def test_filter_interval(test_df):
    filter_df = filter_interval(test_df, 'bin_rsrp', -140, -44)
    assert len(filter_df) == 3
    assert filter_df['bin_rsrp'].sum() == -140 +  -100 + -44

def test_get_hour_from_data_obj():
    assert get_hour_from_data_obj('2023-11-01 00:00:15.270304') == 0
    assert get_hour_from_data_obj('2023-11-01 00:59:59.99999') == 0
    assert get_hour_from_data_obj('2023-11-01 01:01:00.0000') == 1
    assert get_hour_from_data_obj('2023-11-01 12:01:00.0') == 12

def test_categorize_column():
    population_category_test_mapper = {
    'LOW'    : 15000,
    'MEDIUM' : 30000,
    'HIGH' : 45000
    }
    assert categorize_column(population_category_test_mapper, 10000) == 'LOW'
    assert categorize_column(population_category_test_mapper, 15000) == 'LOW'
    assert categorize_column(population_category_test_mapper, 16000) == 'LOW'
    assert categorize_column(population_category_test_mapper, 30000) == 'MEDIUM'
    assert categorize_column(population_category_test_mapper, 35000) == 'MEDIUM'
    assert categorize_column(population_category_test_mapper, 45000) == 'HIGH'
    assert categorize_column(population_category_test_mapper, 46000) == 'HIGH'


def test_s_to_ms():
    assert s_to_ms(0.001) == 1
    assert s_to_ms(0) == 0

def test_change_col_type_to_str(test_df):
    assert type(test_df['node_id'][0]) != str
    test_df = change_col_type_to_str(test_df, ['node_id'])
    assert type(test_df['node_id'][0]) == str
    