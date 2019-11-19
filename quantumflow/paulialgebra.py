
# Copyright 2019-, Gavin E. Crooks and the QuantumFlow contributors
# Copyright 2016-2018, Rigetti Computing
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""
.. contents:: :local:
.. currentmodule:: quantumflow

QuantumFlow module for working with the Pauli algebra.

.. autoclass:: Pauli
    :members:

.. autofunction:: sX
.. autofunction:: sY
.. autofunction:: sZ
.. autofunction:: sI

.. autofunction:: pauli_sum
.. autofunction:: pauli_product
.. autofunction:: pauli_pow
.. autofunction:: pauli_exp_circuit
.. autofunction:: paulis_commute
.. autofunction:: pauli_commuting_sets
.. autofunction:: paulis_close

"""

# Kudos: Adapted from PyQuil's paulis.py, original written by Nick Rubin


from typing import Tuple, Any, Iterator, List
from operator import itemgetter, mul
from functools import reduce, total_ordering
from itertools import groupby, product
import heapq
from cmath import isclose  # type: ignore
from numbers import Complex

import networkx as nx
from networkx.algorithms.approximation.steinertree import steiner_tree

from .config import TOLERANCE
from .qubits import Qubit, Qubits
from .ops import Operation
from .states import State
from .gates import NAMED_GATES, Y, X, RZ, SWAP, CNOT
from .circuits import Circuit

__all__ = ['PauliTerm', 'Pauli', 'sX', 'sY', 'sZ', 'sI',
           'pauli_sum', 'pauli_product', 'pauli_pow', 'paulis_commute',
           'pauli_commuting_sets', 'paulis_close', 'pauli_exp_circuit']

PauliTerm = Tuple[Tuple[Tuple[Qubit, str], ...], complex]

PAULI_OPS = ["X", "Y", "Z", "I"]

PAULI_PROD = {'ZZ': ('I', 1.0),
              'YY': ('I', 1.0),
              'XX': ('I', 1.0),
              'II': ('I', 1.0),
              'XY': ('Z', 1.0j),
              'XZ': ('Y', -1.0j),
              'YX': ('Z', -1.0j),
              'YZ': ('X', 1.0j),
              'ZX': ('Y', 1.0j),
              'ZY': ('X', -1.0j),
              'IX': ('X', 1.0),
              'IY': ('Y', 1.0),
              'IZ': ('Z', 1.0),
              'ZI': ('Z', 1.0),
              'YI': ('Y', 1.0),
              'XI': ('X', 1.0)}


@total_ordering
class Pauli(Operation):
    """
    An element of the Pauli algebra.

    An element of the Pauli algebra is a sequence of terms, such as

        Y(1) - 0.5 Z(1) X(2) Y(4)

    where X, Y, Z and I are the 1-qubit Pauli operators.

    """

    # Internally, each term is a tuple of a complex coefficient, and a sequence
    # of single qubit Pauli operators. (The coefficient goes last so that the
    # terms sort on the operators).
    #
    # PauliTerm = Tuple[Tuple[Tuple[Qubit, str], ...], complex]
    #
    # Each Pauli operator consists of a tuple of
    # qubits e.g. (0, 1, 3), a tuple of Pauli operators e.g. ('X', 'Y', 'Z').
    # Qubits and Pauli terms are kept in sorted order. This ensures that a
    # Pauli element has a unique representation, and makes summation and
    # simplification efficient. We use Tuples (and not lists) because they are
    # immutable and hashable.

    terms: Tuple[PauliTerm, ...]

    def __init__(self, terms: Tuple[PauliTerm, ...]) -> None:
        self.terms = terms

    @classmethod
    def term(cls, qubits: Qubits, ops: str,
             coefficient: complex = 1.0) -> 'Pauli':
        """
        Create an element of the Pauli algebra from a sequence of qubits
        and operators. Qubits must be unique and sortable
        """
        if not all(op in PAULI_OPS for op in ops):
            raise ValueError("Valid Pauli operators are I, X, Y, and Z")

        coeff = complex(coefficient)

        terms = ()  # type: Tuple[PauliTerm, ...]
        if isclose(coeff, 0.0):
            terms = ()
        else:
            qops = zip(qubits, ops)
            qops = filter(lambda x: x[1] != 'I', qops)
            terms = ((tuple(sorted(qops)), coeff),)

        return cls(terms)

    @classmethod
    def sigma(cls, qubit: Qubit, operator: str,
              coefficient: complex = 1.0) -> 'Pauli':
        """Returns a Pauli operator ('I', 'X', 'Y', or 'Z') acting
        on the given qubit"""
        if operator == 'I':
            return cls.scalar(coefficient)
        return cls.term([qubit], operator, coefficient)

    @classmethod
    def scalar(cls, coefficient: complex) -> 'Pauli':
        """Return a scalar multiple of the Pauli identity element."""
        return cls.term((), '', coefficient)

    def is_scalar(self) -> bool:
        """Returns true if this object is a scalar multiple of the Pauli
        identity element"""
        if len(self.terms) > 1:
            return False
        if len(self.terms) == 0:
            return True  # Zero element
        if self.terms[0][0] == ():
            return True
        return False

    @classmethod
    def identity(cls) -> 'Pauli':
        """Return the identity element of the Pauli algebra"""
        return cls.scalar(1.0)

    def is_identity(self) -> bool:
        """Returns True if this object is identity Pauli element."""

        if len(self) != 1:
            return False
        if self.terms[0][0] != ():
            return False
        return isclose(self.terms[0][1], 1.0)

    @classmethod
    def zero(cls) -> 'Pauli':
        """Return the zero element of the Pauli algebra"""
        return cls(())

    def is_zero(self) -> bool:
        """Return True if this object is the zero Pauli element."""
        return len(self.terms) == 0

    @property
    def qubits(self) -> Qubits:
        """Return a list of qubits acted upon by the Pauli element"""
        return list({q for term, _ in self.terms
                     for q, _ in term})  # type: ignore

    def __repr__(self) -> str:
        return 'Pauli(' + str(self.terms) + ')'

    def __str__(self) -> str:
        out = []
        for term in self.terms:
            out.append(f'+ {term[1]:+}')

            for q, op in term[0]:
                out.append(f'{op}({q})')

        return ' '.join(out)

    def __iter__(self) -> Iterator[PauliTerm]:
        return iter(self.terms)

    def __len__(self) -> int:
        return len(self.terms)

    def __add__(self, other: Any) -> 'Pauli':
        if isinstance(other, Complex):
            other = Pauli.scalar(complex(other))
        return pauli_sum(self, other)

    def __radd__(self, other: Any) -> 'Pauli':
        return self.__add__(other)

    def __mul__(self, other: Any) -> 'Pauli':
        if isinstance(other, Complex):
            other = Pauli.scalar(complex(other))
        return pauli_product(self, other)

    def __rmul__(self, other: Any) -> 'Pauli':
        return self.__mul__(other)

    def __sub__(self, other: Any) -> 'Pauli':
        return self + -1. * other

    def __rsub__(self, other: Any) -> 'Pauli':
        return other + -1. * self

    def __neg__(self) -> 'Pauli':
        return self * -1

    def __pos__(self) -> 'Pauli':
        return self

    def __pow__(self, exponent: int) -> 'Pauli':
        return pauli_pow(self, exponent)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Pauli):
            return NotImplemented
        return self.terms < other.terms

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Pauli):
            return NotImplemented
        return self.terms == other.terms

    def __hash__(self) -> int:
        return hash(self.terms)

    # TESTME
    def run(self, ket: State) -> State:
        resultants = []
        for term, coeff in self.terms:
            res = State(ket.tensor * coeff, ket.qubits)
            for qubit, op in term:
                res = NAMED_GATES[op](qubit).run(res)
            resultants.append(res.tensor)

        out = State(sum(resultants), ket.qubits)
        return out

# End class Pauli


def sX(qubit: Qubit, coefficient: complex = 1.0) -> Pauli:
    """Return the Pauli sigma_X operator acting on the given qubit"""
    return Pauli.sigma(qubit, 'X', coefficient)


def sY(qubit: Qubit, coefficient: complex = 1.0) -> Pauli:
    """Return the Pauli sigma_Y operator acting on the given qubit"""
    return Pauli.sigma(qubit, 'Y', coefficient)


def sZ(qubit: Qubit, coefficient: complex = 1.0) -> Pauli:
    """Return the Pauli sigma_Z operator acting on the given qubit"""
    return Pauli.sigma(qubit, 'Z', coefficient)


def sI(qubit: Qubit, coefficient: complex = 1.0) -> Pauli:
    """Return the Pauli sigma_I (identity) operator. The qubit is irrelevant,
    but kept as an  argument for consistency"""
    return Pauli.sigma(qubit, 'I', coefficient)


def pauli_sum(*elements: Pauli) -> Pauli:
    """Return the sum of elements of the Pauli algebra"""
    terms = []

    key = itemgetter(0)
    for term, grp in groupby(heapq.merge(*elements, key=key), key=key):
        coeff = sum(g[1] for g in grp)
        if not isclose(coeff, 0.0):
            terms.append((term, coeff))

    return Pauli(tuple(terms))


def pauli_product(*elements: Pauli) -> Pauli:
    """Return the product of elements of the Pauli algebra"""
    result_terms = []

    for terms in product(*elements):
        coeff = reduce(mul, [term[1] for term in terms])
        ops = (term[0] for term in terms)
        out = []
        key = itemgetter(0)
        for qubit, qops in groupby(heapq.merge(*ops, key=key), key=key):
            res = next(qops)[1]  # Operator: X Y Z
            for op in qops:
                pair = res + op[1]
                res, rescoeff = PAULI_PROD[pair]
                coeff *= rescoeff
            if res != 'I':
                out.append((qubit, res))

        p = Pauli(((tuple(out), coeff),))
        result_terms.append(p)

    return pauli_sum(*result_terms)


def pauli_pow(pauli: Pauli, exponent: int) -> Pauli:
    """
    Raise an element of the Pauli algebra to a non-negative integer power.
    """

    if not isinstance(exponent, int) or exponent < 0:
        raise ValueError("The exponent must be a non-negative integer.")

    if exponent == 0:
        return Pauli.identity()

    if exponent == 1:
        return pauli

    # https://en.wikipedia.org/wiki/Exponentiation_by_squaring
    y = Pauli.identity()
    x = pauli
    n = exponent
    while n > 1:
        if n % 2 == 0:  # Even
            x = x * x
            n = n // 2
        else:           # Odd
            y = x * y
            x = x * x
            n = (n - 1) // 2
    return x * y


def paulis_close(pauli0: Pauli, pauli1: Pauli, tolerance: float = TOLERANCE) \
        -> bool:
    """Returns: True if Pauli elements are almost identical."""
    pauli = pauli0 - pauli1
    d = sum(abs(coeff)**2 for _, coeff in pauli.terms)
    return d <= tolerance


def paulis_commute(element0: Pauli, element1: Pauli) -> bool:
    """
    Return true if the two elements of the Pauli algebra commute.
    i.e. if element0 * element1 == element1 * element0

    Derivation similar to arXiv:1405.5749v2 for the check_commutation step in
    the Raesi, Wiebe, Sanders algorithm (arXiv:1108.4318, 2011).
    """

    def _coincident_parity(term0: PauliTerm, term1: PauliTerm) -> bool:
        non_similar = 0
        key = itemgetter(0)

        op0 = term0[0]
        op1 = term1[0]
        for _, qops in groupby(heapq.merge(op0, op1, key=key), key=key):

            listqops = list(qops)
            if len(listqops) == 2 and listqops[0][1] != listqops[1][1]:
                non_similar += 1
        return non_similar % 2 == 0

    for term0, term1 in product(element0, element1):
        if not _coincident_parity(term0, term1):
            return False

    return True


def pauli_commuting_sets(element: Pauli) -> Tuple[Pauli, ...]:
    """Gather the terms of a Pauli polynomial into commuting sets.

    Uses the algorithm defined in (Raeisi, Wiebe, Sanders,
    arXiv:1108.4318, 2011) to find commuting sets. Except uses commutation
    check from arXiv:1405.5749v2
    """
    if len(element) < 2:
        return (element,)

    groups: List[Pauli] = []  # typing: List[Pauli]

    for term in element:
        pterm = Pauli((term,))

        assigned = False
        for i, grp in enumerate(groups):
            if paulis_commute(grp, pterm):
                groups[i] = grp + pterm
                assigned = True
                break
        if not assigned:
            groups.append(pterm)

    return tuple(groups)


# Adpated from pyquil. THe topoplogical CNOT network is new.
# GEC (2019)
def pauli_exp_circuit(
        element: Pauli,
        alpha: float,
        topology: nx.Graph = None
        ) -> Circuit:
    """
    Returns a Circuit corresponding to the exponential of
    the Pauli algebra element object, i.e. exp[-1.0j * param * element]

    If a qubit topology is provided then the returned circuit will
    respect the qubit connectivity, adding swaps as necessary.
    """
    circ = Circuit()

    if element.is_identity() or element.is_zero():
        return circ

    for term, coeff in element:
        if not isclose(complex(coeff).imag, 0.0):
            raise ValueError("Pauli term coefficients must be real")
        theta = complex(coeff).real * alpha

        active_qubits = set()

        change_to_z_basis = Circuit()
        for qubit, op in term:
            active_qubits.add(qubit)
            if op == 'X':
                change_to_z_basis += Y(qubit)**0.5
            elif op == 'Y':
                change_to_z_basis += X(qubit)**0.5

        if topology is None:
            topology = nx.DiGraph()
            nx.add_path(topology, list(active_qubits))
        elif not nx.is_directed(topology) or not nx.is_arborescence(topology):
            # An 'arborescence' is a directed tree
            topology = steiner_tree(topology, active_qubits)
            center = nx.center(topology)[0]
            topology = nx.dfs_tree(topology, center)

        order = list(reversed(list(nx.topological_sort(topology))))

        cnot_seq = Circuit()
        for q0 in order[:-1]:
            q1 = list(topology.pred[q0])[0]

            if q1 not in active_qubits:
                cnot_seq += SWAP(q0, q1)
                active_qubits.add(q1)
            else:
                cnot_seq += CNOT(q0, q1)

        circ += change_to_z_basis
        circ += cnot_seq
        circ += RZ(2*theta, order[-1])
        circ += cnot_seq.H
        circ += change_to_z_basis.H
        # end term loop
    return circ

# fin
