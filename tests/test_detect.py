"""Testing HFO detection algorithms."""

import pytest
from scipy.signal import butter, filtfilt
from sklearn.utils.estimator_checks import parametrize_with_checks

from mne_hfo.detect import LineLengthDetector, RMSDetector, HilbertDetector


@parametrize_with_checks([
    RMSDetector(sfreq=2000),
    LineLengthDetector(sfreq=2000),
    # HilbertDetector(sfreq=2000),
])
def test_sklearn_compat(estimator, check):
    """Tests sklearn API compatability."""
    check(estimator)


def test_detect_hfo_ll(create_testing_eeg_data, benchmark):
    fs = 5000
    b, a = butter(3, [80 / (fs / 2), 600 / (fs / 2)], 'bandpass')
    filt_data = filtfilt(b, a, create_testing_eeg_data)
    window_size = int((1 / 80) * fs)

    compute_instance = LineLengthDetector(sfreq=fs, win_size=window_size)
    compute_instance.params = {'window_size': window_size}
    dets = benchmark(compute_instance.run_windowed,
                     filt_data, 50000)

    compute_instance.run_windowed(filt_data,
                                  5000,
                                  n_cores=2)

    expected_vals = [(5040, 5198),
                     (34992, 35134)]

    for exp_val, det in zip(expected_vals, dets):
        assert det[0] == exp_val[0]
        assert det[1] == exp_val[1]


def test_detect_hfo_rms(create_testing_eeg_data, benchmark):
    fs = 5000
    b, a = butter(3, [80 / (fs / 2), 600 / (fs / 2)], 'bandpass')
    filt_data = filtfilt(b, a, create_testing_eeg_data)
    window_size = int((1 / 80) * fs)

    compute_instance = RMSDetector(sfreq=fs)
    compute_instance.params = {'window_size': window_size}
    dets = benchmark(compute_instance.run_windowed,
                     filt_data, 50000)

    compute_instance.run_windowed(filt_data,
                                  5000,
                                  n_cores=2)

    expected_vals = [(5040, 5198),
                     (35008, 35134)]

    for exp_val, det in zip(expected_vals, dets):
        assert det[0] == exp_val[0]
        assert det[1] == exp_val[1]


@pytest.mark.skip(reason='need to implement...')
def test_detect_hfo_hilbert(create_testing_eeg_data, benchmark):
    fs = 5000

    compute_instance = HilbertDetector(sfreq=fs)
    compute_instance.params = {'fs': fs,
                               'low_fc': 80,
                               'high_fc': 600,
                               'threshold': 7}
    dets = benchmark(compute_instance.run_windowed,
                     create_testing_eeg_data, 50000)

    compute_instance.run_windowed(create_testing_eeg_data,
                                  5000,
                                  n_cores=2)

    expected_vals = [(5056, 5123),
                     (35028, 35063)]

    for exp_val, det in zip(expected_vals, dets):
        assert det[0] == exp_val[0]
        assert det[1] == exp_val[1]


@pytest.mark.skip(reason='need to implement...')
def test_detect_hfo_cs_beta(create_testing_eeg_data, benchmark):
    fs = 5000
    compute_instance = CSDetector()
    compute_instance.params = {'fs': 5000,
                               'low_fc': 40,
                               'high_fc': 1000,
                               'threshold': 0.1,
                               'cycs_per_detect': 4.0}

    dets = benchmark(compute_instance.run_windowed,
                     create_testing_eeg_data, 50000)

    compute_instance.run_windowed(create_testing_eeg_data,
                                  5000,
                                  n_cores=2)

    # Only the second HFO is caught by CS (due to signal artificiality)
    expected_vals = [(34992, 35090),  # Band detection
                     (34992, 35090)]  # Conglomerate detection

    for exp_val, det in zip(expected_vals, dets):
        assert det[0] == exp_val[0]
        assert det[1] == exp_val[1]