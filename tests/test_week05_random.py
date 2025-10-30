import hashlib
import sys
from collections.abc import Generator

sys.path.append('solutions')

import numpy as np
import pytest
from pytest import FixtureRequest
from pytest_regressions.ndarrays_regression import NDArraysRegressionFixture

import week03
import week05
from utils import (
    cache_data_stream_per_function,
    parameterize_random_general_sum_tests,
    parameterize_random_zero_sum_tests,
)

BASE_SEED = 141


@pytest.fixture
def rng(request: FixtureRequest) -> np.random.Generator:
    """Create a random seed based on the function name to ensure reproducibility."""

    digest = hashlib.md5(request.node.originalname.encode()).hexdigest()
    seed = (BASE_SEED + int(digest, 16)) % (2**32)

    return np.random.default_rng(seed)


@pytest.fixture
@cache_data_stream_per_function
def general_sum_data_stream(request: FixtureRequest, rng: np.random.Generator) -> Generator:
    return parameterize_random_general_sum_tests(300, rng)


@pytest.fixture
@cache_data_stream_per_function
def zero_sum_data_stream(request: FixtureRequest, rng: np.random.Generator) -> Generator:
    return parameterize_random_zero_sum_tests(300, rng)


@pytest.mark.parametrize('zero_sum_data_stream', range(10), indirect=True)
def test_double_oracle(
    zero_sum_data_stream: Generator,
    ndarrays_regression: NDArraysRegressionFixture,
    request: FixtureRequest,
    rng: np.random.Generator,
) -> None:
    row_matrix, col_matrix, *_ = next(zero_sum_data_stream)

    strategies, supports = week05.double_oracle(row_matrix, 1e-2, rng)
    exploitability = week03.compute_exploitability(row_matrix, col_matrix, *strategies[-1])

    for (row_strategy, col_strategy), (row_support, col_support) in zip(strategies, supports):
        assert row_strategy.dtype == np.float64, 'Incorrect dtype!'
        assert col_strategy.dtype == np.float64, 'Incorrect dtype!'
        assert row_support.dtype == np.int64, 'Incorrect dtype!'
        assert col_support.dtype == np.int64, 'Incorrect dtype!'

    assert exploitability.dtype == np.float64, 'Incorrect dtype!'

    ndarrays_regression.check(
        {
            'row_strategy': strategies[-1][0],
            'col_strategy': strategies[-1][1],
            'row_support': supports[-1][0],
            'col_support': supports[-1][1],
            'exploitability': exploitability,
        },
        f'{request.node.originalname}{request.node.callspec.indices["zero_sum_data_stream"]}',
    )
