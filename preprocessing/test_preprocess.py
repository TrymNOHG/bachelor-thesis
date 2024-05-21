import pandas as pd
import pytest
from preprocess import shift_fault, find_avg_rtt_in_timespan


@pytest.fixture
def get_timestamp_seconds():
    return ['15.270304', '16.463788', '17.966253', '18.466253', '19.466253'],


@pytest.fixture
def test_df():
    test_data = {
    'node_id': [1, 1, 1, 1, 1],
    'ts': ['2023-11-01 00:00:15.270304', '2023-11-01 00:00:16.463788', '2023-11-01 00:00:17.966253', '2023-11-01 00:00:18.166253', '2023-11-01 00:00:19.466253'],
    'rtt' : [0.018055, 0.019393, 0.061758, 0.036384, 0.023214],
    'is_fault' : [True, False, False, True, False],
}
    df = pd.DataFrame(test_data)
    df['ts'] = pd.to_datetime(df['ts'])
    return df


def test_shift_value(test_df):
    shifted_df = shift_fault(test_df)
    # Final datapoint should be NaN since it cannot have a label attached
    assert len(shifted_df) == 5
    shifted_df.dropna(inplace=True)
    assert len(shifted_df) == 4
    assert list(shifted_df['is_fault']) == [False, False, True, False]


def test_rtt_aggregation(test_df):
    df = test_df.groupby('node_id').apply(lambda group: find_avg_rtt_in_timespan(group, "2s")).reset_index(drop=True)
    means = list(df["rtt_2s_mean"])
    raw_rtts = list(test_df["rtt"])

    # Helper
    mean = lambda l: sum(l) / len(l)

    # First mean should be "itself" because there are no other datapoints to calculate a mean from
    assert means[0] == raw_rtts[0]

    # Second mean should be the mean of the current and previous RTT
    assert means[1] == mean(raw_rtts[:2])

    # Third mean should also be the mean of the current and previous RTT
    assert means[2] == mean(raw_rtts[1:3])

    # Fourth mean should actually be the mean of the current and two previous RTTs (see the TS's)
    assert means[3] == mean(raw_rtts[1:4])

    # Fifth is similar to fourth. It own RTT plus the previous two.
    assert means[4] == mean(raw_rtts[2:5])
