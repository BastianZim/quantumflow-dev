# Copyright 2021-, Gavin E. Crooks
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.


"""
Common two qubit gates
======================


.. autoclass:: CX
.. autoclass:: CXPow
.. autoclass:: CY
.. autoclass:: CYPow
.. autoclass:: CZ
.. autoclass:: CZPow

"""


from ..operations import QuantumStdCtrlGate, Variable
from ..states import Qubit
from .common_gates_1q import X, XPow, Y, YPow, Z, ZPow

__all__ = (
    "CX",
    "CXPow",
    "CY",
    "CYPow",
    "CZ",
    "CZPow",
    "CNot",  # Alias for CX  # DOCME
)


class CX(QuantumStdCtrlGate):
    r"""A controlled-X gate, also called controlled-not (cnot).

    Locally equivalent to ``Can(1/2, 0, 0)``.

    .. math::
           {autogenerated_latex}

    Args:
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CX
    """
    cv_target = X

    def __init__(self, q0: Qubit, q1: Qubit) -> None:
        super().__init__(q0, q1)

    @property
    def H(self) -> "CX":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "CXPow":
        return CXPow(t, *self.qubits)


# end class CX

CNot = CX  # Alias


class CXPow(QuantumStdCtrlGate):
    r"""Powers of the controlled-X (CX, CNOT) gate.

    .. math::
        {autogenerated_latex}

    Args:
        t (Variable): Power to which the base gate is raised.
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CXPow
    """
    cv_target = XPow

    def __init__(self, t: Variable, q0: Qubit, q1: Qubit) -> None:
        super().__init__(t, q0, q1)

    @property
    def H(self) -> "CXPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "CXPow":
        return CXPow(t * self.t, *self.qubits)


# end class CXPow


class CY(QuantumStdCtrlGate):
    r"""A controlled-Y gate.

    Locally equivalent to ``Can(1/2, 0, 0)``.

    .. math::
           {autogenerated_latex}

    Args:
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CY
    """
    cv_target = Y

    def __init__(self, q0: Qubit, q1: Qubit) -> None:
        super().__init__(q0, q1)

    @property
    def H(self) -> "CY":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "CYPow":
        return CYPow(t, *self.qubits)


# end class CY


class CYPow(QuantumStdCtrlGate):
    r"""Powers of the controlled-Y (CY) gate.

    .. math::
        {autogenerated_latex}

    Attributes:
        t: Power to which the CY gate is raised.
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CYPow
    """
    cv_target = YPow

    def __init__(self, t: Variable, q0: Qubit, q1: Qubit) -> None:
        super().__init__(t, q0, q1)

    @property
    def H(self) -> "CYPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "CYPow":
        return CYPow(t * self.t, *self.qubits)


# end class CYPow


class CZ(QuantumStdCtrlGate):
    r"""A controlled-Z gate.

    Locally equivalent to ``Can(1/2, 0, 0)``.

    .. math::
           {autogenerated_latex}

    Args:
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CZ
    """
    cv_target = Z

    def __init__(self, q0: Qubit, q1: Qubit) -> None:
        super().__init__(q0, q1)

    @property
    def H(self) -> "CZ":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "CZPow":
        return CZPow(t, *self.qubits)


# end class CZ


class CZPow(QuantumStdCtrlGate):
    r"""Powers of the controlled-Z (CZ) gate.

    .. math::
        {autogenerated_latex}

    Args:
        t (Variable): Power to which the CZ gate is raised.
        q0 (Qubit): Control qubit
        q1 (Qubit): Target qubit

    [1]: https://threeplusone.com/gates#CZPow
    """
    cv_target = ZPow

    def __init__(self, t: Variable, q0: Qubit, q1: Qubit) -> None:
        super().__init__(t, q0, q1)

    @property
    def H(self) -> "CZPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "CZPow":
        return CZPow(t * self.t, *self.qubits)


# end class CZPow

# fin
