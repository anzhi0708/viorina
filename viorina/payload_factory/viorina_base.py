from dataclasses import dataclass
from typing import Optional
import inspect

from viorina.descriptors.descriptor_basics import ViorinaDescriptor


@dataclass
class Attribute:
    name: str
    annotation: Optional[type]
    value: ViorinaDescriptor

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "annotation": self.annotation,
            "value": self.value
        }


def viorina(cls):
    """
    Nestable node that represents a XML/JSON node.
    ```python
    from viorina.descriptors import Text
    from viorina.payload_factory import Node, Auto, List, viorina
    

    @viorina
    class root:
        OrderInfo = Auto()


    @viorina
    class Product:
        ItemName = Text(regex=r'[a-zA-Z]+')
        Price = Float(min_value=0.0, max_value=999.99, min_decimal_places=2, max_decimal_places=3)


    @viorina
    class OrderInfo:
        HblNo =  Text(regex=r'[0-9A-Z]{5,10}')
        Products: list[Product] = List(max_repeat=5)


    root.build_xml()  # or `root.build_json()`
    ```
    """
    cls._viorina_elements = []

    for name, value in cls.__dict__.items():
        if isinstance(value, ViorinaDescriptor):
            cls._viorina_elements.append(
                Attribute(
                    name = name,
                    value = value,
                    annotation = inspect.get_annotations(cls, eval_str=True).get(name)
                )
            )
            print(cls._viorina_elements)
