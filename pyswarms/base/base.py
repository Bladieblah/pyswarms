# -*- coding: utf-8 -*-

r"""
Base class for single-objective discrete Particle Swarm Optimization
implementations.

All methods here are abstract and raises a :code:`NotImplementedError`
when not used. When defining your own swarm implementation,
create another class,

    >>> class MySwarm(DiscreteSwarmOptimizer):
    >>>     def __init__(self):
    >>>        super(MySwarm, self).__init__()

and define all the necessary methods needed.

As a guide, check the discrete PSO implementations in this package.

.. note:: Regarding :code:`options`, it is highly recommended to
    include parameters used in position and velocity updates as
    keyword arguments. For parameters that affect the topology of
    the swarm, it may be much better to have them as positional
    arguments.

See Also
--------
:mod:`pyswarms.discrete.binary`: binary PSO implementation

"""

# Import standard library
import abc
from typing import Any, Callable, List, NamedTuple, Optional, Tuple, TypedDict

# Import modules
import numpy as np
import numpy.typing as npt

# Import from pyswarms
from pyswarms.backend.swarms import Swarm
from pyswarms.utils.types import Clamp, Position, Velocity


class Options(TypedDict):
    c1: float
    c2: float
    w: float


class ToHistory(NamedTuple):
    best_cost: float
    mean_pbest_cost: float
    mean_neighbor_cost: float
    position: Position
    velocity: Velocity


class BaseSwarmOptimizer(abc.ABC):
    # Initialize history lists
    cost_history: List[float] = []
    mean_pbest_history: List[float] = []
    mean_neighbor_history: List[float] = []
    pos_history: List[Position] = []
    velocity_history: List[Velocity] = []

    swarm: Swarm

    def __init__(
        self,
        n_particles: int,
        dimensions: int,
        options: Options,
        velocity_clamp: Optional[Clamp] = None,
        init_pos: Optional[Position] = None,
        ftol: float = -np.inf,
        ftol_iter: int = 1,
        **kwargs: Any
    ):
        """Initialize the swarm.

        Creates a :code:`numpy.ndarray` of positions depending on the
        number of particles needed and the number of dimensions.
        The initial positions of the particles depends on the argument
        :code:`binary`, which governs if a binary matrix will be produced.

        Attributes
        ----------
        n_particles : int
            number of particles in the swarm.
        dimensions : int
            number of dimensions in the space.
        options : dict with keys :code:`{'c1', 'c2', 'w'}`
            a dictionary containing the parameters for the specific
            optimization technique
                * c1 : float
                    cognitive parameter
                * c2 : float
                    social parameter
                * w : float
                    inertia parameter
        velocity_clamp : tuple, optional
            a tuple of size 2 where the first entry is the minimum velocity
            and the second entry is the maximum velocity. It
            sets the limits for velocity clamping.
        ftol : float
            relative error in objective_func(best_pos) acceptable for
            convergence. Default is :code:`-np.inf`.
        ftol_iter : int
            number of iterations over which the relative error in
            objective_func(best_pos) is acceptable for convergence.
            Default is :code:`1`
        """
        # Initialize primary swarm attributes
        self.n_particles = n_particles
        self.dimensions = dimensions
        self.velocity_clamp = velocity_clamp
        self.swarm_size = (n_particles, dimensions)
        self.options = options
        self.init_pos = init_pos
        self.ftol = ftol

        assert ftol_iter > 0 and isinstance(ftol_iter, int), "ftol_iter expects an integer value greater than 0"

        self.ftol_iter = ftol_iter

        # Initialize resettable attributes
        self.reset()

    def _populate_history(self, hist: ToHistory):
        """Populate all history lists

        The :code:`cost_history`, :code:`mean_pbest_history`, and
        :code:`neighborhood_best` is expected to have a shape of
        :code:`(iters,)`,on the other hand, the :code:`pos_history`
        and :code:`velocity_history` are expected to have a shape of
        :code:`(iters, n_particles, dimensions)`

        Parameters
        ----------
        hist : collections.namedtuple
            Must be of the same type as self.ToHistory
        """
        self.cost_history.append(hist.best_cost)
        self.mean_pbest_history.append(hist.mean_pbest_cost)
        self.mean_neighbor_history.append(hist.mean_neighbor_cost)
        self.pos_history.append(hist.position)
        self.velocity_history.append(hist.velocity)

    @abc.abstractmethod
    def optimize(
        self,
        objective_func: Callable[..., npt.NDArray[Any]],
        iters: int,
        n_processes: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[float, Position]:
        """Optimize the swarm for a number of iterations

        Performs the optimization to evaluate the objective
        function :code:`objective_func` for a number of iterations
        :code:`iter.`

        Parameters
        ----------
        objective_func : callable
            objective function to be evaluated
        iters : int
            number of iterations
        n_processes : int
            number of processes to use for parallel particle evaluation
            Default is None with no parallelization
        kwargs : dict
            arguments for objective function

        Raises
        ------
        NotImplementedError
            When this method is not implemented.
        """
        raise NotImplementedError("SwarmBase::optimize()")

    @abc.abstractmethod
    def _init_swarm(self) -> None:
        """Initialise a new swarm object"""
        raise NotImplementedError("SwarmBase::init_swarm()")

    def reset(self):
        """Reset the attributes of the optimizer

        All variables/atributes that will be re-initialized when this
        method is defined here. Note that this method
        can be called twice: (1) during initialization, and (2) when
        this is called from an instance.

        It is good practice to keep the number of resettable
        attributes at a minimum. This is to prevent spamming the same
        object instance with various swarm definitions.

        Normally, swarm definitions are as atomic as possible, where
        each type of swarm is contained in its own instance. Thus, the
        following attributes are the only ones recommended to be
        resettable:

        * Swarm position matrix (self.pos)
        * Velocity matrix (self.pos)
        * Best scores and positions (gbest_cost, gbest_pos, etc.)

        Otherwise, consider using positional arguments.
        """
        # Initialize history lists
        self.cost_history = []
        self.mean_pbest_history = []
        self.mean_neighbor_history = []
        self.pos_history = []
        self.velocity_history = []

        self._init_swarm()
