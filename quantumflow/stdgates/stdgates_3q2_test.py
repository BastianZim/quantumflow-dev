# Copyright 2020-, Gavin E. Crooks and contributors
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.


import numpy as np

import quantumflow as qf


def test_CCX() -> None:
    ket = qf.zero_state(range(3))
    ket = qf.CCX(0, 1, 2).run(ket)
    assert ket.tensor[0, 0, 0] == 1.0

    ket = qf.X(1).run(ket)
    ket = qf.CCX(0, 1, 2).run(ket)
    assert ket.tensor[0, 1, 0] == 1.0

    ket = qf.X(0).run(ket)
    ket = qf.CCNot(0, 1, 2).run(ket)
    assert ket.tensor[1, 1, 1] == 1.0

    assert qf.CXX(0, 1, 2).target.qubit_nb == 1


def test_CSwap() -> None:
    ket = qf.zero_state(range(3))
    ket = qf.X(1).run(ket)
    ket = qf.CSwap(0, 1, 2).run(ket)
    assert ket.tensor[0, 1, 0] == 1.0

    ket = qf.X(0).run(ket)
    ket = qf.CSwap(0, 1, 2).run(ket)
    assert ket.tensor[1, 0, 1] == 1.0

    assert qf.CSwap(0, 1, 2).target.qubit_nb == 2


def test_CCZ() -> None:
    ket = qf.zero_state(range(3))
    ket = qf.X(0).run(ket)
    ket = qf.X(1).run(ket)
    ket = qf.H(2).run(ket)
    ket = qf.CCZ(0, 1, 2).run(ket)
    ket = qf.H(2).run(ket)
    qf.print_state(ket)
    assert np.isclose(ket.tensor[1, 1, 1], 1.0)

    gate0 = qf.CCZ(0, 1, 2)
    assert gate0.H is gate0


def test_deutsch() -> None:
    gate0 = qf.Deutsch(5 * np.pi / 2, 0, 1, 2)
    gate1 = qf.CCX(0, 1, 2)
    assert qf.gates_close(gate0, gate1)


# fin
