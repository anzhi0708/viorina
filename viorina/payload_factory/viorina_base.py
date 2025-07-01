class Node:
    """
    Nestable node that represents a XML/JSON node.
    ```python
    from viorina.descriptors import Text
    from viorina.payload_factory import Node, Auto, List, viorina_node
    

    @viorina
    class root(Node):
        OrderInfo: Node = Auto()


    @viorina
    class Product(Node):
        ItemName = Text(regex=r'[a-zA-Z]+')
        Price = Float(min_value=0.0, max_value=999.99, min_decimal_places=2, max_decimal_places=3)


    @viorina
    class OrderInfo:
        HblNo =  Text(regex=r'[0-9A-Z]{5,10}')
        Products: list[Product] = List(max_count=5)


    root.build_xml()  # or `root.build_json()`
    ```
    """
    
