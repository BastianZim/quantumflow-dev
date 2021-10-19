# Copyright 2021-, Gavin E. Crooks
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""
Common one qubit gates
======================

.. autoclass:: I
.. autoclass:: Ph
.. autoclass:: X
.. autoclass:: Y
.. autoclass:: Z
.. autoclass:: H
.. autoclass:: Rx
.. autoclass:: Ry
.. autoclass:: Rz
.. autoclass:: P
.. autoclass:: Rn
.. autoclass:: XPow
.. autoclass:: YPow
.. autoclass:: ZPow
.. autoclass:: HPow
.. autoclass:: V
.. autoclass:: V_H
.. autoclass:: S
.. autoclass:: S_H
.. autoclass:: SqrtY
.. autoclass:: SqrtY_H
.. autoclass:: T
.. autoclass:: T_H
"""

import sympy as sym
from sympy.abc import phi as sym_phi  # Symbolic phi
from sympy.abc import t as sym_t  # Symbolic t
from sympy.abc import theta as sym_theta  # Symbolic theta

from ..operations import OperatorStructure, QuantumStdGate, Variable
from ..states import Qubit

__all__ = (
    "H",
    "HPow",
    "I",
    "P",
    "Ph",
    "Rn",
    "Rx",
    "Ry",
    "Rz",
    "SqrtY",
    "SqrtY_H",
    "S",
    "S_H",
    "T",
    "T_H",
    "V",
    "V_H",
    "X",
    "XPow",
    "Y",
    "YPow",
    "Z",
    "ZPow",
    "PhaseShift",  # Alias for P  # DOCME
)


class H(QuantumStdGate):
    r"""
    A 1-qubit Hadamard gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#H
    """
    cv_hermitian = True
    cv_sym_operator = sym.Matrix([[1, 1], [1, -1]]) / sym.sqrt(2)

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "H_":  # See NB implementation note below
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "HPow":
        return HPow(t, *self.qubits)


# Note: H().H -> H, but the method shadows the class, so we can't
# annotate directly.
H_ = H

# End class H


class HPow(QuantumStdGate):
    r"""
    Powers of the 1-qubit Hadamard gate.

    .. math::
        {autogenerated_latex}

    Args:
        t (Variable): Exponent of Hadamard gate
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#HPow
    """
    cv_sym_operator = (
        sym.exp(sym.I * sym.pi * sym_t / 2)
        * sym.Matrix(
            [
                [
                    sym.cos(sym.pi * sym_t / 2) - (sym.I * sym.sin(sym.pi * sym_t / 2)),
                    -(sym.I * sym.sin(sym.pi * sym_t / 2)),
                ],
                [
                    -sym.I * sym.sin(sym.pi * sym_t / 2),
                    sym.cos(sym.pi * sym_t / 2) + (sym.I * sym.sin(sym.pi * sym_t / 2)),
                ],
            ]
        )
        / sym.sqrt(2)
    )

    def __init__(self, t: Variable, q0: Qubit) -> None:
        super().__init__(t, q0)

    @property
    def H(self) -> "HPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "HPow":
        return HPow(t * self.t, *self.qubits)


# End class HPow


class I(QuantumStdGate):  # noqa: E742
    r"""
    A 1-qubit identity gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#I
    """
    cv_hermitian = True
    cv_operator_structure = OperatorStructure.identity
    cv_sym_operator = sym.Matrix([[1, 0], [0, 1]])

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "I":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "I":
        return self


# end class I


class P(QuantumStdGate):
    r"""A 1-qubit parametric phase shift gate.

    Equivalent to Rz up to a global phase.

     Args:
        theta (Variable): Phase shift
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#HPow
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix([[1, 0], [0, sym.exp(sym.I * sym_theta)]])

    def __init__(self, theta: Variable, q0: Qubit) -> None:
        super().__init__(theta, q0)

    @property
    def H(self) -> "P":
        return self ** -1

    def __pow__(self, t: Variable) -> "P":
        return P(t * self.theta, *self.qubits)


# end class P

PhaseShift = P  # Alias for P


class Ph(QuantumStdGate):
    r"""
    Apply a global phase shift of exp(i phi).

    Since this gate applies a global phase it technically doesn't need to
    specify qubits at all. But we instead anchor the gate to 1 specific
    qubit so that we can keep track of the phase as we manipulate gates and
    circuits.

    We generally don't care about the global phase, since it has no
    physical meaning, It does matter when constructing controlled gates.

    .. math::
        {autogenerated_latex}

    Args:
        phi (Variable): Global phase
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Ph
    """

    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [[sym.exp(sym.I * sym_phi), 0], [0, sym.exp(sym.I * sym_phi)]]
    )

    def __init__(self, phi: Variable, q0: Qubit) -> None:
        super().__init__(phi, q0)

    @property
    def H(self) -> "Ph":
        return self ** -1

    def __pow__(self, t: Variable) -> "Ph":
        return Ph(t * self.phi, *self.qubits)


# End class Ph


sym_nx = sym.Symbol("nx")
sym_ny = sym.Symbol("ny")
sym_nz = sym.Symbol("nz")


class Rn(QuantumStdGate):
    r"""A 1-qubit rotation of angle theta about axis (nx, ny, nz)

    .. math::
        R_n(\theta) = \cos \frac{\theta}{2} I - i \sin\frac{\theta}{2}
        (n_x X+ n_y Y + n_z Z)

    Args:
        theta (Variable): Angle of rotation on Block sphere
        (nx, ny, nz) (Variable): A three-dimensional real unit vector
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Rn
    """

    cv_sym_operator = sym.Matrix(
        [
            [
                sym.cos(sym_theta / 2) - sym.I * sym.sin(sym_theta / 2) * sym_nz,
                -sym.I * sym.sin(sym_theta / 2) * sym_nx
                - sym.sin(sym_theta / 2) * sym_ny,
            ],
            [
                -sym.I * sym.sin(sym_theta / 2) * sym_nx
                + sym.sin(sym_theta / 2) * sym_ny,
                sym.cos(sym_theta / 2) + sym.I * sym.sin(sym_theta / 2) * sym_nz,
            ],
        ]
    )

    def __init__(
        self, theta: Variable, nx: Variable, ny: Variable, nz: Variable, q0: Qubit
    ) -> None:
        super().__init__(theta, nx, ny, nz, q0)

    @property
    def H(self) -> "Rn":
        return self ** -1

    def __pow__(self, t: Variable) -> "Rn":
        return Rn(t * self.theta, self.nx, self.ny, self.nz, *self.qubits)


# end class RN


class Rx(QuantumStdGate):
    r"""A 1-qubit Pauli-X parametric rotation gate.

    .. math::
        {autogenerated_latex}

    Args:
        theta: Angle of rotation in Bloch sphere
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Rx
    """
    cv_sym_operator = sym.Matrix(
        [
            [sym.cos(sym_theta / 2), -sym.I * sym.sin(sym_theta / 2)],
            [-sym.I * sym.sin(sym_theta / 2), sym.cos(sym_theta / 2)],
        ]
    )

    def __init__(self, theta: Variable, q0: Qubit) -> None:
        super().__init__(theta, q0)

    @property
    def H(self) -> "Rx":
        return self ** -1

    def __pow__(self, t: Variable) -> "Rx":
        return Rx(self.theta * t, *self.qubits)


# end class Rx


class Ry(QuantumStdGate):
    r"""A 1-qubit Pauli-Y parametric rotation gate.

    .. math::
        {autogenerated_latex}

    Args:
        theta: Angle of rotation in Bloch sphere
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Ry
    """
    cv_sym_operator = sym.Matrix(
        [
            [sym.cos(sym_theta / 2), -sym.sin(sym_theta / 2)],
            [sym.sin(sym_theta / 2), sym.cos(sym_theta / 2)],
        ]
    )

    def __init__(self, theta: Variable, q0: Qubit) -> None:
        super().__init__(theta, q0)

    @property
    def H(self) -> "Ry":
        return self ** -1

    def __pow__(self, t: Variable) -> "Ry":
        return Ry(self.theta * t, *self.qubits)


# end class Ry


class Rz(QuantumStdGate):
    r"""A 1-qubit Pauli-Z parametric rotation gate.

    .. math::
        {autogenerated_latex}

    Args:
        theta: Angle of rotation in Bloch sphere
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Rz
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [sym.exp(-sym.I * sym_theta / 2), 0],
            [0, sym.exp(+sym.I * sym_theta / 2)],
        ]
    )

    def __init__(self, theta: Variable, q0: Qubit) -> None:
        super().__init__(theta, q0)

    @property
    def H(self) -> "Rz":
        return self ** -1

    def __pow__(self, t: Variable) -> "Rz":
        return Rz(self.theta * t, *self.qubits)


# end class Rx


class S(QuantumStdGate):
    r"""
    A 1-qubit phase S gate, equivalent to ``Z ** (1/2)``. The square root
    of the Z gate. Also sometimes denoted as the P gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#S
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [1, 0],
            [0, sym.I],
        ]
    )

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "S_H":
        return S_H(*self.qubits)

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(t / 2, *self.qubits)


# end class S


class S_H(QuantumStdGate):
    r"""
    The inverse of the 1-qubit phase S gate, equivalent to
    ``Z ** -1/2``.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#S_H
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [1, 0],
            [0, -sym.I],
        ]
    )

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "S":
        return S(*self.qubits)

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(-t / 2, *self.qubits)


# end class S_H


class SqrtY(QuantumStdGate):
    r"""
    Principal square root of the Y gate.


    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#SqrtY
    """
    cv_sym_operator = sym.Matrix([[1, -1], [1, 1]]) * (1 + sym.I) / 2

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "SqrtY_H":
        return SqrtY_H(*self.qubits)

    def __pow__(self, t: Variable) -> "YPow":
        return YPow(t / 2, *self.qubits)


# end class SqrtY


class SqrtY_H(QuantumStdGate):
    r"""
    Complex conjugate of the np.sqrtY gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#SqrtY_H
    """
    cv_sym_operator = sym.Matrix([[1, 1], [-1, 1]]) * (1 - sym.I) / 2

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "SqrtY":
        return SqrtY(*self.qubits)

    def __pow__(self, t: Variable) -> "YPow":
        return YPow(-t / 2, *self.qubits)


# end class SqrtY_H


class T(QuantumStdGate):
    r"""
    A 1-qubit T (pi/8) gate, equivalent to ``X ** (1/4)``.

    The forth root of the Z gate (up to global phase).


    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#T
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [1, 0],
            [0, sym.exp(sym.I * sym.pi / 4)],
        ]
    )

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "T_H":
        return T_H(*self.qubits)

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(t / 4, *self.qubits)


# end class T


class T_H(QuantumStdGate):
    r"""
    The inverse (complex conjugate) of the 1-qubit T (pi/8) gate, equivalent
    to ``Z ** -1/4``.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#T_H
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [1, 0],
            [0, sym.exp(-sym.I * sym.pi / 4)],
        ]
    )

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "T":
        return T(*self.qubits)

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(-t / 4, *self.qubits)


# end class T_H


class V(QuantumStdGate):
    r"""
    Principal square root of the X gate, X-PLUS-90 gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#V
    """
    cv_sym_operator = sym.Matrix([[1 + sym.I, 1 - sym.I], [1 - sym.I, 1 + sym.I]]) / 2

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "V_H":
        return V_H(*self.qubits)

    def __pow__(self, t: Variable) -> "XPow":
        return XPow(t / 2, *self.qubits)


# end class V


class V_H(QuantumStdGate):
    r"""
    Complex conjugate of the V gate, X-MINUS-90 gate.


    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#V_H
    """
    cv_sym_operator = sym.Matrix([[1 - sym.I, 1 + sym.I], [1 + sym.I, 1 - sym.I]]) / 2

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "V":
        return V(*self.qubits)

    def __pow__(self, t: Variable) -> "XPow":
        return XPow(-t / 2, *self.qubits)


# end class V_H


class X(QuantumStdGate):
    r"""
    A 1-qubit Pauli-X gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#X
    """
    cv_hermitian = True
    cv_operator_structure = OperatorStructure.permutation
    cv_sym_operator = sym.Matrix([[0, 1], [1, 0]])

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "X":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "XPow":
        return XPow(t, *self.qubits)


# end class X


class XPow(QuantumStdGate):
    r"""Powers of the 1-qubit Pauli-X gate.

    .. math::
        \text{XPow}(t) = X^t = e^{i \pi t/2} R_x(\pi t)

    .. math::
        {autogenerated_latex}

    Args:
        t: Number of half turns (quarter cycles) in the Block sphere
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#XPow
    """
    cv_sym_operator = sym.exp(sym.I * sym.pi * sym_t / 2) * sym.Matrix(
        [
            [sym.cos(sym.pi * sym_t / 2), -sym.I * sym.sin(sym.pi * sym_t / 2)],
            [-sym.I * sym.sin(sym.pi * sym_t / 2), sym.cos(sym.pi * sym_t / 2)],
        ]
    )

    def __init__(self, t: Variable, q0: Qubit) -> None:
        super().__init__(t, q0)

    @property
    def H(self) -> "XPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "XPow":
        return XPow(t * self.t, *self.qubits)


# end class XPow


class Y(QuantumStdGate):
    r"""
    A 1-qubit Pauli-Y gate.

    .. math::
        {autogenerated_latex}

    mnemonic: "Minus eye high".

    Args:
        q0 (Qubit): Gate's qubit.

    [1]: https://threeplusone.com/gates#Y
    """
    cv_hermitian = True
    cv_operator_structure = OperatorStructure.monomial
    cv_sym_operator = sym.Matrix([[0, -sym.I], [sym.I, 0]])

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "Y":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "YPow":
        return YPow(t, *self.qubits)


# end class Y


class YPow(QuantumStdGate):
    r"""Powers of the 1-qubit Pauli-Y gate.

    .. math::
        \text{YPow}(t) = Y^t = e^{i \pi t/2} R_y(\pi t)

    .. math::
        {autogenerated_latex}

    Args:
        t (Variable): Number of half turns (quarter cycles) in the Block sphere
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#YPow
    """
    cv_sym_operator = sym.exp(sym.I * sym.pi * sym_t / 2) * sym.Matrix(
        [
            [sym.cos(sym.pi * sym_t / 2), -sym.sin(sym.pi * sym_t / 2)],
            [sym.sin(sym.pi * sym_t / 2), sym.cos(sym.pi * sym_t / 2)],
        ]
    )

    def __init__(self, t: Variable, q0: Qubit) -> None:
        super().__init__(t, q0)

    @property
    def H(self) -> "YPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "YPow":
        return YPow(t * self.t, *self.qubits)


# end class YPow


class Z(QuantumStdGate):
    r"""
    A 1-qubit Pauli-Z gate.

    .. math::
        {autogenerated_latex}

    Args:
        q0 (Qubit): Gate qubit.

    [1]: https://threeplusone.com/gates#Z
    """
    cv_hermitian = True
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix([[1, 0], [0, -1]])

    def __init__(self, q0: Qubit) -> None:
        super().__init__(q0)

    @property
    def H(self) -> "Z":
        return self  # Hermitian

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(t, *self.qubits)


# end class Z


class ZPow(QuantumStdGate):
    r"""Powers of the 1-qubit Pauli-Z gate.

    .. math::
        \text{ZPow}(t) = Z^t = e^{i \pi t/2} R_z(\pi t)

    .. math::
        {autogenerated_latex}

    Args:
        t (Variable): Number of half turns (quarter cycles) in the Block sphere
        q0 (Qubit): Gate qubit

    [1]: https://threeplusone.com/gates#ZPow
    """
    cv_operator_structure = OperatorStructure.diagonal
    cv_sym_operator = sym.Matrix(
        [
            [1, 0],
            [0, sym.exp(sym.I * sym.pi * sym_t)],
        ]
    )

    def __init__(self, t: Variable, q0: Qubit) -> None:
        super().__init__(t, q0)

    @property
    def H(self) -> "ZPow":
        return self ** -1

    def __pow__(self, t: Variable) -> "ZPow":
        return ZPow(t * self.t, *self.qubits)


# end class ZPow


# fin
