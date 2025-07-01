from typing import Protocol


class ViorinaDescriptor(Protocol):
    pass


class TextTypeDescriptor(ViorinaDescriptor):
    """
    A text field.
    """
    regex_pattern: str

    def regex_generate(self): pass


class IntegerTypeDescriptor(ViorinaDescriptor):
    """
    An integer field.
    """
    max_value: int
    min_value: int


class FloatTypeDescriptor(ViorinaDescriptor):
    """
    A floating number field.
    """
    max_value: int
    min_value: int
    max_decimal_places: int
    min_decimal_places: int
