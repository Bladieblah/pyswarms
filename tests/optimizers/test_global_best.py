#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest
from pyswarms.backend.velocity import VelocityUpdater

from pyswarms.single import GlobalBestPSO
from pyswarms.utils.functions.single_obj import sphere

from .abc_test_optimizer import ABCTestOptimizer


class TestGlobalBestOptimizer(ABCTestOptimizer):
    @pytest.fixture
    def optimizer(self):
        return GlobalBestPSO

    @pytest.fixture
    def optimizer_history(self, velocity_updater: VelocityUpdater):
        opt = GlobalBestPSO(10, 2, velocity_updater)
        opt.optimize(sphere, 1000)
        return opt

    @pytest.fixture
    def optimizer_reset(self, velocity_updater: VelocityUpdater):
        opt = GlobalBestPSO(10, 2, velocity_updater)
        opt.optimize(sphere, 10)
        opt.reset()
        return opt

    def test_global_correct_pos(self, velocity_updater: VelocityUpdater):
        """Test to check global optimiser returns the correct position corresponding to the best cost"""
        opt = GlobalBestPSO(n_particles=10, dimensions=2, velocity_updater=velocity_updater)
        _, pos = opt.optimize(sphere, iters=5)
        # find best pos from history
        min_cost_idx = np.argmin(opt.cost_history)
        min_pos_idx = np.argmin(sphere(opt.pos_history[min_cost_idx]))
        assert np.array_equal(opt.pos_history[min_cost_idx][min_pos_idx], pos)
