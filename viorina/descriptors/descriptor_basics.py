from typing import Protocol, Any


class ViorinaDescriptor[T](Protocol):
    def get_value(self) -> T: ...


class TextTypeDescriptor(ViorinaDescriptor[str], Protocol):
    """
    A text field.
    """

    regex_pattern: str

    def regex_generate(self) -> str: ...


class IntegerTypeDescriptor(ViorinaDescriptor[int], Protocol):
    """
    An integer field.
    """

    max_value: int
    min_value: int


class FloatTypeDescriptor(ViorinaDescriptor[float], Protocol):
    """
    A floating number field.
    """

    max_value: float
    min_value: float
    max_decimal_places: int
    min_decimal_places: int
