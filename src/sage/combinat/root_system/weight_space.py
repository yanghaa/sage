"""
Weight lattices and weight spaces
"""
#*****************************************************************************
#       Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.sets.family import Family
from sage.combinat.free_module import CombinatorialFreeModule, CombinatorialFreeModuleElement
from weight_lattice_realizations import WeightLatticeRealizations

class WeightSpace(CombinatorialFreeModule):
    r"""
    INPUT:

    - ``root_system`` -- a root system
    - ``base_ring`` -- a ring `R`
    - ``extended`` -- a boolean (default: False)

    The weight space (or lattice if ``base_ring`` is `\ZZ`) of a root
    system is the formal free module `\bigoplus_i R \Lambda_i`
    generated by the fundamental weights `(\Lambda_i)_{i\in I}` of the
    root system.

    This class is also used for coweight spaces (or lattices).

    .. seealso::

        - :meth:`RootSystem`
        - :meth:`RootSystem.weight_lattice` and :meth:`RootSystem.weight_space`
        - :meth:`~sage.combinat.root_system.weight_lattice_realizations.WeightLatticeRealizations`

    EXAMPLES::

        sage: Q = RootSystem(['A', 3]).weight_lattice(); Q
        Weight lattice of the Root system of type ['A', 3]
        sage: Q.simple_roots()
        Finite family {1: 2*Lambda[1] - Lambda[2], 2: -Lambda[1] + 2*Lambda[2] - Lambda[3], 3: -Lambda[2] + 2*Lambda[3]}

        sage: Q = RootSystem(['A', 3, 1]).weight_lattice(); Q
        Weight lattice of the Root system of type ['A', 3, 1]
        sage: Q.simple_roots()
        Finite family {0: 2*Lambda[0] -   Lambda[1]               -   Lambda[3],
                       1:  -Lambda[0] + 2*Lambda[1] -   Lambda[2],
                       2:                -Lambda[1] + 2*Lambda[2] -   Lambda[3],
                       3:  -Lambda[0]               -   Lambda[2] + 2*Lambda[3]}

    For infinite types, the Cartan matrix is singular, and therefore
    the embedding of the root lattice is not faithful::

        sage: sum(Q.simple_roots())
        0

    In particular, the null root is zero::

        sage: Q.null_root()
        0

    This can be compensated by extending the basis of the weight space
    and slightly deforming the simple roots to make them linearly
    independent, without affecting the scalar product with the
    coroots. This feature is currently only implemented for affine
    types. In that case, if ``extended`` is set, then the basis of the
    weight space is extended by an element `\delta`::

        sage: Q = RootSystem(['A', 3, 1]).weight_lattice(extended = True); Q
        Extended weight lattice of the Root system of type ['A', 3, 1]
        sage: Q.basis().keys()
        {0, 1, 2, 3, 'delta'}

    And the simple root `\alpha_0` associated to the special node is
    deformed as follows::

        sage: Q.simple_roots()
        Finite family {0: 2*Lambda[0] -   Lambda[1]               -   Lambda[3] + delta,
                       1:  -Lambda[0] + 2*Lambda[1] -   Lambda[2],
                       2:                -Lambda[1] + 2*Lambda[2] -   Lambda[3],
                       3:  -Lambda[0]               -   Lambda[2] + 2*Lambda[3]}

    Now, the null root is nonzero::

        sage: Q.null_root()
        delta

    .. warning::

        By a slight notational abuse, the extra basis element used to
        extend the fundamental weights is called ``\delta`` in the
        current implementation. However, in the literature,
        ``\delta`` usually denotes instead the null root. Most of the
        time, those two objects coincide, but not for type `BC` (aka.
        `A_{2n}^{(2)}`). Therefore we currently have::

            sage: Q = RootSystem(["A",4,2]).weight_lattice(extended=True)
            sage: Q.simple_root(0)
            2*Lambda[0] - Lambda[1] + delta
            sage: Q.null_root()
            2*delta

        whereas, with the standard notations from the literature, one
        would expect to get respectively `2\Lambda_0 -\Lambda_1 +1/2
        \delta` and `\delta`.

        Other than this notational glitch, the implementation remains
        correct for type `BC`.

        The notations may get improved in a subsequent version, which
        might require changing the index of the extra basis
        element. To guarantee backward compatibility in code not
        included in Sage, it is recommended to use the following idiom
        to get that index::

            sage: F = Q.basis_extension(); F
            Finite family {'delta': delta}
            sage: index = F.keys()[0]; index
            'delta'

        Then, for example, the coefficient of an element of the
        extended weight lattice on that basis element can be recovered
        with::

            sage: Q.null_root()[index]
            2

    TESTS::

        sage: for ct in CartanType.samples(crystalographic=True)+[CartanType(["A",2],["C",5,1])]:
        ...       TestSuite(ct.root_system().weight_lattice()).run()
        ...       TestSuite(ct.root_system().weight_space()).run()
        sage: for ct in CartanType.samples(affine=True):
        ...       if ct.is_implemented():
        ...           P = ct.root_system().weight_space(extended=True)
        ...           TestSuite(P).run()
    """

    @staticmethod
    def __classcall_private__(cls, root_system, base_ring, extended=False):
        """
        Guarantees Unique representation

        .. seealso:: :class:`UniqueRepresentation`

        TESTS::

            sage: R = RootSystem(['A',4])
            sage: from sage.combinat.root_system.weight_space import WeightSpace
            sage: WeightSpace(R, QQ) is WeightSpace(R, QQ, False)
            True
        """
        return super(WeightSpace, cls).__classcall__(cls, root_system, base_ring, extended)


    def __init__(self, root_system, base_ring, extended):
        """
        TESTS::

            sage: R = RootSystem(['A',4])
            sage: from sage.combinat.root_system.weight_space import WeightSpace
            sage: Q = WeightSpace(R, QQ); Q
            Weight space over the Rational Field of the Root system of type ['A', 4]
            sage: TestSuite(Q).run()

            sage: WeightSpace(R, QQ, extended = True)
            Traceback (most recent call last):
            ...
            AssertionError: extended weight lattices are only implemented for affine root systems
        """
        basis_keys = root_system.index_set()
        self._extended = extended
        if extended:
            assert root_system.cartan_type().is_affine(), "extended weight lattices are only implemented for affine root systems"
            basis_keys = tuple(basis_keys) + ("delta",)

        self.root_system = root_system
        CombinatorialFreeModule.__init__(self, base_ring,
                                         basis_keys,
                                         prefix = "Lambdacheck" if root_system.dual_side else "Lambda",
                                         latex_prefix = "\\Lambda^\\vee" if root_system.dual_side else "\\Lambda",
                                         category = WeightLatticeRealizations(base_ring))

        if root_system.cartan_type().is_affine() and not extended:
            # For an affine type, register the quotient map from the
            # extended weight lattice/space to the weight lattice/space
            domain = root_system.weight_space(base_ring, extended=True)
            domain.module_morphism(self.fundamental_weight,
                                   codomain = self
                                   ).register_as_coercion()

    def is_extended(self):
        """
        Returns whether this is an extended weight lattice

        .. seealso: :meth:`~sage.combinat.root_sytem.weight_lattice_realization.ParentMethods.is_extended`

        EXAMPLES::

            sage: RootSystem(["A",3,1]).weight_lattice().is_extended()
            False
            sage: RootSystem(["A",3,1]).weight_lattice(extended=True).is_extended()
            True
        """
        return self._extended

    def _repr_(self):
        """
        TESTS::

            sage: RootSystem(['A',4]).weight_lattice()    # indirect doctest
            Weight lattice of the Root system of type ['A', 4]
            sage: RootSystem(['B',4]).weight_space()
            Weight space over the Rational Field of the Root system of type ['B', 4]
            sage: RootSystem(['A',4]).coweight_lattice()
            Coweight lattice of the Root system of type ['A', 4]
            sage: RootSystem(['B',4]).coweight_space()
            Coweight space over the Rational Field of the Root system of type ['B', 4]

        """
        return self._name_string()

    def _name_string(self, capitalize=True, base_ring=True, type=True):
        """
        EXAMPLES::

            sage: RootSystem(['A',4]).weight_lattice()._name_string()
            "Weight lattice of the Root system of type ['A', 4]"
        """
        return self._name_string_helper("weight",
                                        capitalize=capitalize, base_ring=base_ring, type=type,
                                        prefix="extended " if self.is_extended() else "")

    @cached_method
    def fundamental_weight(self, i):
        """
        Returns the `i`-th fundamental weight

        INPUT:

        - ``i`` -- an element of the index set or ``"delta"``

        By a slight notational abuse, for an affine type this method
        also accepts ``"delta"`` as input, and returns the image of
        `\delta` of the extended weight lattice in this realization.

        .. seealso: :meth:`~sage.combinat.root_sytem.weight_lattice_realization.ParentMethods.fundamental_weight`

        EXAMPLES::

            sage: Q = RootSystem(["A",3]).weight_lattice()
            sage: Q.fundamental_weight(1)
            Lambda[1]

            sage: Q = RootSystem(["A",3,1]).weight_lattice(extended=True)
            sage: Q.fundamental_weight(1)
            Lambda[1]
            sage: Q.fundamental_weight("delta")
            delta
        """
        if i == "delta":
            assert self.cartan_type().is_affine()
            if self.is_extended():
                return self.monomial(i)
            else:
                return self.zero()
        else:
            assert i in self.index_set()
            return self.monomial(i)

    @cached_method
    def basis_extension(self):
        r"""
        Return the basis elements used to extend the fundamental weights

        EXAMPLES::

            sage: Q = RootSystem(["A",3,1]).weight_lattice()
            sage: Q.basis_extension()
            Family ()

            sage: Q = RootSystem(["A",3,1]).weight_lattice(extended=True)
            sage: Q.basis_extension()
            Finite family {'delta': delta}

        This method is irrelevant for finite types::

            sage: Q = RootSystem(["A",3]).weight_lattice()
            sage: Q.basis_extension()
            Family ()
        """
        if self.is_extended():
            return Family(["delta"], self.monomial)
        else:
            return Family([])


    @cached_method
    def simple_root(self, j):
        """
        Returns the `j^{th}` simple root

        TESTS::

            sage: L = RootSystem(["C",4]).weight_lattice()
            sage: L.simple_root(3)
            -Lambda[2] + 2*Lambda[3] - Lambda[4]

        Its coefficients are given by the corresponding column of the
        Cartan matrix::

            sage: L.cartan_type().cartan_matrix()[:,2]
            [ 0]
            [-1]
            [ 2]
            [-1]

            sage: L.simple_roots()
            Finite family {1: 2*Lambda[1] - Lambda[2],
                           2: -Lambda[1] + 2*Lambda[2] - Lambda[3],
                           3: -Lambda[2] + 2*Lambda[3] - Lambda[4],
                           4: -2*Lambda[3] + 2*Lambda[4]}

        For the extended weight lattice of an affine type, the simple
        root associated to the special node is deformed by `\delta`::

            sage: L = RootSystem(["C",4,1]).weight_lattice(extended=True)
            sage: L.simple_root(0)
            2*Lambda[0] - 2*Lambda[1] + delta
        """
        assert(j in self.index_set())
        result = self.sum_of_terms(self.root_system.dynkin_diagram().column(j))
        if self._extended and j == self.cartan_type().special_node():
            result = result + self.monomial("delta")
        return result

    def _repr_term(self, m):
        r"""
        Customized monomial printing for extended weight lattices

        EXAMPLES::

            sage: L = RootSystem(["C",4,1]).weight_lattice(extended=True)
            sage: L.simple_root(0)             # indirect doctest
            2*Lambda[0] - 2*Lambda[1] + delta

            sage: L = RootSystem(["C",4,1]).coweight_lattice(extended=True)
            sage: L.simple_root(0)             # indirect doctest
            2*Lambdacheck[0] - Lambdacheck[1] + deltacheck
        """
        if m == "delta":
            return "deltacheck" if self.root_system.dual_side else "delta"
        else:
            return super(WeightSpace, self)._repr_term(m)

    def _latex_term(self, m):
        r"""
        Customized monomial typesetting for extended weight lattices

        EXAMPLES::

            sage: L = RootSystem(["C",4,1]).weight_lattice(extended=True)
            sage: latex(L.simple_root(0))             # indirect doctest
            2\Lambda_{0} - 2\Lambda_{1} + \delta

            sage: L = RootSystem(["C",4,1]).coweight_lattice(extended=True)
            sage: latex(L.simple_root(0))             # indirect doctest
            2\Lambda^\vee_{0} - \Lambda^\vee_{1} + \delta^\vee
        """
        if m == "delta":
            return "\\delta^\\vee" if self.root_system.dual_side else "\\delta"
        else:
            return super(WeightSpace, self)._latex_term(m)


class WeightSpaceElement(CombinatorialFreeModuleElement):

    def scalar(self, lambdacheck):
        """
        The canonical scalar product between the weight lattice and
        the coroot lattice.

        .. todo::

            - merge with_apply_multi_module_morphism
            - allow for any root space / lattice
            - define properly the return type (depends on the base rings of the two spaces)
            - make this robust for extended weight lattices (`i` might be "delta")

        EXAMPLES::

            sage: L = RootSystem(["C",4,1]).weight_lattice()
            sage: Lambda     = L.fundamental_weights()
            sage: alphacheck = L.simple_coroots()
            sage: Lambda[1].scalar(alphacheck[1])
            1
            sage: Lambda[1].scalar(alphacheck[2])
            0

        The fundamental weights and the simple coroots are dual bases:

            sage: matrix([ [ Lambda[i].scalar(alphacheck[j])
            ...              for i in L.index_set() ]
            ...            for j in L.index_set() ])
            [1 0 0 0 0]
            [0 1 0 0 0]
            [0 0 1 0 0]
            [0 0 0 1 0]
            [0 0 0 0 1]

        Note that the scalar product is not yet implemented between
        the weight space and the coweight space; in any cases, that
        won't be the job of this method::

            sage: R = RootSystem(["A",3])
            sage: alpha = R.weight_space().roots()
            sage: alphacheck = R.coweight_space().roots()
            sage: alpha[1].scalar(alphacheck[1])
            Traceback (most recent call last):
              ...
              assert lambdacheck in self.parent().coroot_lattice() or lambdacheck in self.parent().coroot_space()
            AssertionError
        """
        # TODO: Find some better test
        assert lambdacheck in self.parent().coroot_lattice() or lambdacheck in self.parent().coroot_space()
        zero = self.parent().base_ring().zero()
        if len(self) < len(lambdacheck):
            return sum( (lambdacheck[i]*c for (i,c) in self), zero)
        else:
            return sum( (self[i]*c for (i,c) in lambdacheck), zero)

    def is_dominant(self):
        """
        Checks whether an element in the weight space lies in the positive cone spanned
        by the basis elements (fundamental weights).

        EXAMPLES::

            sage: W=RootSystem(['A',3]).weight_space()
            sage: Lambda=W.basis()
            sage: w=Lambda[1]+Lambda[3]
            sage: w.is_dominant()
            True
            sage: w=Lambda[1]-Lambda[2]
            sage: w.is_dominant()
            False
        """
        return all(c >= 0 for c in self.coefficients())

WeightSpace.Element = WeightSpaceElement
