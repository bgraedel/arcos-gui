from arcos_gui import arcos_module
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

@pytest.fixture
def fixture_columns():
    columns = {
        'frame': 'Frame', 
        'x_coordinates': 'X', 
        'y_coordinates': 'Y',
        'track_id': 'track_id',
        'measurment': 'Measurment',
        'field_of_view_id': 'Position'
        }
    return columns

@pytest.fixture
def import_data(fixture_columns):
    my_input = arcos_module.process_input(csv_file="src/arcos_gui/_tests/fixtures/filter_test.csv", columns=fixture_columns)
    my_input.read_csv()
    return my_input

@pytest.fixture
def create_arocs_testfixture(fixture_columns):
    my_input = arcos_module.process_input(csv_file="src/arcos_gui/_tests/fixtures/arcos_test.csv", columns=fixture_columns)
    my_input.read_csv()
    data = my_input.return_pd_df()
    arcos = arcos_module.ARCOS(dataframe=data, columns=fixture_columns)
    arcos.create_arcosTS()
    return arcos

def is_unique(s):
    a = s.to_numpy()
    return (a[0] == a).all()

def test_filter_input(import_data):
    out = import_data.filter_position(2, True).reset_index(drop=True)
    data=[['2_1',  239.842, 161.539, 0, 0.861779, 2]]
    cols=['track_id','X','Y','Frame','Measurment','Position',]
    test_df = pd.DataFrame(data= data, columns=cols)
    assert_frame_equal(out, test_df, check_index_type=False)

def test_filter_tracklength(import_data):
    out = import_data.filter_tracklength(1,1, return_dataframe=True).reset_index(drop=True)
    data=[['2_1',  239.842, 161.539, 0, 0.861779, 2]]
    cols=['track_id','X','Y','Frame','Measurment','Position',]
    test_df = pd.DataFrame(data= data, columns=cols)
    assert_frame_equal(out, test_df)

def test_rescale_measurment(import_data):
    import_data.filter_position(2, True)
    out = import_data.rescale_measurment(10, return_dataframe=True).reset_index(drop=True)
    data=[['2_1',  239.842, 161.539, 0, 8.61779, 2]]
    cols=['track_id','X','Y','Frame','Measurment','Position',]
    test_df = pd.DataFrame(data= data, columns=cols)
    assert_frame_equal(out, test_df)

def test_interpolate_measurements(create_arocs_testfixture, fixture_columns):
    out = create_arocs_testfixture.interpolate_measurements(return_dataframe=True)
    assert (len(out[fixture_columns['measurment']].dropna()) == len(out[fixture_columns['measurment']]))

def test_clip_measurments(create_arocs_testfixture, fixture_columns):
    create_arocs_testfixture.interpolate_measurements()
    clipped = create_arocs_testfixture.clip_measurements(clip_low= 1, clip_high = 1, return_dataframe = True)
    assert (is_unique(clipped[fixture_columns['measurment']]))

def test_bin_measurments(create_arocs_testfixture):
    create_arocs_testfixture.interpolate_measurements()
    out = create_arocs_testfixture.bin_measurements(biasmethod = 'none', peak_thr = 0.15, bin_thr = 0.15, return_dataframe = True)
    assert (out.iloc[3, 7] == 1)

def test_track_events(create_arocs_testfixture):
    create_arocs_testfixture.interpolate_measurements()
    create_arocs_testfixture.bin_measurements(biasmethod = 'none', peak_thr = 0.15, bin_thr = 0.15)
    out = create_arocs_testfixture.track_events(min_clustersize = 1, return_dataframe = True)
    assert ((out.columns == 'collid').any())

def test_filter_events(create_arocs_testfixture):
    create_arocs_testfixture.interpolate_measurements()
    create_arocs_testfixture.bin_measurements(biasmethod = 'none', peak_thr = 0.15, bin_thr = 0.15)
    create_arocs_testfixture.track_events(min_clustersize = 1, return_dataframe = True)
    out = create_arocs_testfixture.filter_tracked_events(min_duration = 3, total_event_size = 3, as_pd_dataframe = True)
    assert (len(out) == 6)

def test_calculate_stats(create_arocs_testfixture):
    create_arocs_testfixture.interpolate_measurements()
    create_arocs_testfixture.bin_measurements(biasmethod = 'none', peak_thr = 0.15, bin_thr = 0.15)
    create_arocs_testfixture.track_events(min_clustersize = 1, return_dataframe = True)
    create_arocs_testfixture.filter_tracked_events(min_duration = 3, total_event_size = 3)
    out = create_arocs_testfixture.calculate_stats()
    out_int = out['clDur'].squeeze()
    assert (out_int == 3)
