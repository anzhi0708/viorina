```plaintext
  _     _ _             _             
(_)   (_|_)           (_)            
 _     _ _  ___   ____ _ ____  _____ 
| |   | | |/ _ \ / ___) |  _ \(____ |
 \ \ / /| | |_| | |   | | | | / ___ |
  \___/ |_|\___/|_|   |_|_| |_\_____|
                                     
Light-weight minimal API Fuzzer in Python
```

# Examples
- `Viorina.build_dict()`
```pycon
>>> import viorina
>>> from viorina import Auto
>>>
>>> app = viorina.Viorina()
>>>
>>> @app.payload
... class Root:
...     BranchA = Auto()
...     Name = "Anji"
...     
>>> @app.payload
... class BranchA:
...     Age = 233
...     
>>> app.build_dict()
{'Root': {'Name': 'Anji', 'BranchA': {'Age': 233}}}
>>> 
```
- Using `Text`, `Integer`, `Auto` descriptors to generate random mocking values
```python
from viorina import Text, Integer, Auto, Viorina


app = Viorina()


@app.payload
class Root:
    SomeNode = Auto()
    RandomValue = Integer(min_value=233, max_value=235)

@app.payload
class SomeNode:
    RandomName = Text(regex=r'[AEIOU][aeiou][rnmlv][aeiou]{2}')
    ChildNode = Auto()  # class `ChildNode` will have parent node `Node`
    RandomValue = Integer(min_value=0, max_value=9)

@app.payload
class ChildNode:
    ConstValue: int = 233

if __name__ == "__main__":
    import pprint
    
    for _ in range(3):
        pprint.pp(app.build_dict())
        
# Output:
        
# {'Root': {'RandomValue': 235,
#           'SomeNode': {'RandomName': 'Eolee',
#                        'RandomValue': 5,
#                        'ChildNode': {'ConstValue': 233}}}}
# {'Root': {'RandomValue': 235,
#           'SomeNode': {'RandomName': 'Aarei',
#                        'RandomValue': 7,
#                        'ChildNode': {'ConstValue': 233}}}}
# {'Root': {'RandomValue': 234,
#           'SomeNode': {'RandomName': 'Uovai',
#                        'RandomValue': 1,
#                        'ChildNode': {'ConstValue': 233}}}}
```
