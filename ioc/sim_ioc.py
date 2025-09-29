from textwrap import dedent

from caproto.server import PVGroup, ioc_arg_parser, pvproperty, run


class SimpleIOC(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs.

    Scalar PVs
    ----------
    A (int)
    B (float)

    Array PVs
    ---------
    C (array of int)
    """

    A = pvproperty(value=1.0, doc="Value A")
    B = pvproperty(value=1.0, doc="Value B")
    C = pvproperty(value=1.0, doc="Value C")
    D = pvproperty(value=1.0, doc="Value D")
    E = pvproperty(value=1.0, doc="Value E")
    F = pvproperty(value=1.0, doc="Value F")
    G = pvproperty(value=1.0, doc="Value G")
    H = pvproperty(value=1.0, doc="Value H")
    I = pvproperty(value=1.0, doc="Value I")  # noqa:E741
    J = pvproperty(value=1.0, doc="Value J")


if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(default_prefix="simulated:", desc=dedent(SimpleIOC.__doc__))
    ioc = SimpleIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
