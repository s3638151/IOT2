#!/usr/bin/python
# -*- coding: UTF-8 -*-

class Const:
    """Define a constant class to implement the constant function

    Define the __setattr()__function and an exception ConstErr class, ConstErro class inherits TypeError class.
    Use self's __dict__ to check the constant. If the constant exists, throw rebind exception, or create the it.
    And register this Const class to the sys.modules dictionary.

    Ver 1.0

    """
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.get(name) is not None:
            raise self.ConstError("Can't rebind const(%s)" %name)

        self.__dict__[name] = value