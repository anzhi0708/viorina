from typing import Protocol, runtime_checkable


@runtime_checkable
class ViorinaDescriptor[T](Protocol):
    def get_value(self) -> T: ...
    def __repr__(self) -> str: ...


@runtime_checkable
class TextTypeDescriptor(ViorinaDescriptor[str], Protocol):
    """
    A text field.
    """

    regex_pattern: str

    def regex_generate(self) -> str: ...


@runtime_checkable
class IntegerTypeDescriptor(ViorinaDescriptor[int], Protocol):
    """
    An integer field.
    """

    max_value: int
    min_value: int


@runtime_checkable
class FloatTypeDescriptor(ViorinaDescriptor[float], Protocol):
    """
    A floating number field.
    """

    max_value: float
    min_value: float
    max_decimal_places: int
    min_decimal_places: int
