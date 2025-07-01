import random

from .descriptor_basics import IntegerTypeDescriptor


class Integer(IntegerTypeDescriptor):
    """
    Describes an interger field for a field.
    Integers has these properties:
    - Min value (defaults to 0)
    - Max value (defaults to 9999)
    """

    def __init__(
        self,
        min_value: int = 0,
        max_value: int = 9999,
    ):
        self.max_value: int = max_value
        self.min_value: int = min_value
        if self.min_value > self.max_value:
            raise IndexError(f"{self.min_value = } is larger than {self.max_value =}")

    def get_value(self):
        return random.randint(self.min_value, self.max_value)

    def __get__(self, obj, tp):
        return self.get_value()

    def __set__(self, obj, value):
        raise AttributeError(
            "Cannot set value; this is a read-only random integer field."
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(min_value={self.min_value}, max_value={self.max_value})"
