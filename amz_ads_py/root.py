#python 3.11.15
class Root(object):
    """'SuperClass' or 'SuperObject' that all other classes 
    are connected. Only this class is liked with 'object'.
    """

    def __init__(self, **kwargs):
        mro = type(self).__mro__
        assert mro[-1] is object
        if mro[-2] is not Root:
            raise TypeError(
                "all top-level classes in this hierarchy must inherit from 'Root' SuperObject",
                "the last class in the MRO should be SuperObject",
                f"mro={[cls.__name__ for cls in mro]}"
            )

        # super().__init__ is guaranteed to be object.__init__
        init = super().__init__
        init()