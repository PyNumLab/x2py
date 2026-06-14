"""Module containing metaclasses which are useful for the rest of x2py"""

from inspect import signature

__all__ = ("Singleton",)


class Singleton(type):
    """
    Metaclass indicating that there is only one instance of the class.

    A metaclass which ensures that only one instance of the class is ever
    created. Trying to create a second instance will result in accessing
    the first.

    Parameters
    ----------
    name : str
        The name of the class.
    bases : tuple[class,...]
        A tuple of the superclasses of the class.
    dct : dict
        A dictionary of the class attributes.
    """

    def __init__(cls, name, bases, dct):
        cls._instance = None
        # Trick inspect.signature into seeing the signature of
        # cls.__init__ so numpydoc checks the correct signature
        cls.__signature__ = signature(cls.__init__)
        super().__init__(name, bases, dct)

    def __call__(cls):
        existing_instance = cls._instance
        if existing_instance is None:
            new_instance = super().__call__()
            cls._instance = new_instance
            return new_instance
        return existing_instance
