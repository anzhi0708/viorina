from typing import Optional, Any, TypedDict
import inspect

from viorina.descriptors.descriptor_basics import ViorinaDescriptor


class NodeSchema(TypedDict):
    attrs: dict[str, Any]
    children: dict[type, "NodeSchema"]


class Auto(ViorinaDescriptor):
    """

    ```python
    @app.payload
    class Node:
        name = Text(regex=...)
        ChildNode = Auto()  # class `ChildNode` will have parent node `Node`

    # A node can have multiple parent nodes
    @app.payload
    class AnotherNode:
        ChildNode = Auto()  # class `ChildNode` will add a parent node `AnotherNode`

    @app.payload
    class ChildNode:
        data = ...
    ```

    This class will provide:
    - Qualname for child node (via `self.class_name`)
    - Qualname for parent node (via `self.parent_name`)

    """

    def __init__(self) -> None:
        self.class_name: Optional[str] = None  # Attribute name
        self.class_handler: Optional[type] = None  # ???
        self.annotation_type: Optional[type] = None
        self.parent_class: Optional[type] = None

    def __set_name__(self, parent_class: type, class_name: str):
        self.parent_class = parent_class
        self.class_name = class_name
        annotation = inspect.get_annotations(self.parent_class, eval_str=True)
        self.annotation_type = annotation.get(self.class_name)

    def __get__(self, instance, owner_type) -> Optional[type]:
        app: Optional[Viorina] = getattr(self.parent_class, "__viorina_app__", None)
        if app is None:
            raise RuntimeError(
                f"{self.parent_class} is not associated with any Viorina instances"
            )
        if not self.class_name:
            raise RuntimeError("self.class_name not initialized")
        handler = app.get_type_handler_by_name(self.class_name)
        if handler is None:
            raise LookupError(
                f"Could not find child node {self.class_name!r} in registered types"
            )
        return handler


class Viorina:
    """

    ```python
    from viorina.descriptors import Text, Float
    from viorina.payload_factory import Auto, List, Viorina


    app = Viorina()

    @app.payload
    class Root:  # class name `Root` will be translated into element/node/key.
        '''
        This will generate something like:

        ```xml
        <Root>
            <OrderInfo>
                <HblNo></HblNo>
                <Products>
                    <Product></Product>
                    <Product></Product>
                </Products>
            </OrderInfo>
        </Root>
        ```

        or equivlant JSON data, depend on which method was called.
        '''
        OrderInfo = Auto()


    @app.payload
    class Product:
        ItemName = Text(regex=r'[a-zA-Z]+')
        Price = Float(min_value=0.0, max_value=999.99, min_decimal_places=2, max_decimal_places=3)


    @app.payload
    class OrderInfo:
        HblNo =  Text(regex=r'[0-9A-Z]{5,10}')
        Products: list[Product] = List(max_repeat=5)


    app.build_xml()  # or `root.build_json()`
    ```
    """

    def __init__(self) -> None:
        self.__registered_types: dict[str, type] = {}
        self.__edges: set[tuple[type, type]] = set()
        self.__pending_edges: set[tuple[type, str]] = set()

    def _resolve_edges(self) -> None:
        if not self.__pending_edges:
            return
        for parent, child_name in list(self.__pending_edges):
            child_type_handler = self.get_type_handler_by_name(child_name)
            if child_type_handler:
                self.add_edge(parent, child_type_handler)
                self.__pending_edges.remove((parent, child_name))

    def add_edge(self, parent: type, child: type) -> None:
        self.__edges.add((parent, child))

    def add_pending_edge(self, pending: tuple[type, str]) -> None:
        self.__pending_edges.add(pending)

    def build_tree(self) -> dict[type, NodeSchema]:
        self._resolve_edges()

        children_handlers = {c for _, c in self.__edges}
        root_handlers = [
            v for v in self.__registered_types.values() if v not in children_handlers
        ]

        def sub_tree(cls: type) -> NodeSchema:
            attrs: dict[str, Any] = {}
            children: dict[type, Any] = {}

            for name, val in cls.__dict__.items():

                # (1) Reference to other user-defined classes
                if isinstance(val, Auto):
                    assert val.class_name is not None
                    child_class_handler = self.__registered_types[val.class_name]
                    children[child_class_handler] = sub_tree(child_class_handler)

                # (2) Other Viorina descriptors
                elif isinstance(val, ViorinaDescriptor):
                    attrs[name] = val

                # (3) Const values
                elif not name.startswith("__") and not callable(val):
                    attrs[name] = val

            # return {"attrs": attrs, "children": children}
            return NodeSchema(attrs=attrs, children=children)

        return {r: sub_tree(r) for r in root_handlers}

    def payload(self, cls):
        self.__registered_types[cls.__name__] = cls
        cls.__viorina_app__ = self

        for name, attr in cls.__dict__.items():
            if isinstance(attr, Auto) and attr.class_name:
                self.__pending_edges.add((cls, attr.class_name))

        return cls

    def get_type_handler_by_name(self, tp_name_str: str) -> Optional[type]:
        return self.__registered_types.get(tp_name_str)

    def get_registered_types(self) -> dict[str, type]:
        return self.__registered_types
