```plaintext
  _     _ _             _             
(_)   (_|_)           (_)            
 _     _ _  ___   ____ _ ____  _____ 
| |   | | |/ _ \ / ___) |  _ \(____ |
 \ \ / /| | |_| | |   | | | | / ___ |
  \___/ |_|\___/|_|   |_|_| |_\_____|
                                     
Light-weight minimal API Fuzzer in Python
```

**Viorina** is a minimalist, lightweight API-fuzzing tool.  
Describe your payload once—Viorina generates compliant, random test data for you.

#### It stays tiny

* **Declarative schemas** – Register any model with `@Viorina.payload` (FastAPI-style, zero boiler-plate).  
* **Descriptor magic** – Python’s descriptor protocol auto-wires parent/child fields, so you don’t have to.  
* **Accurate text fuzzing** – Uses the Rust crate **`regex-generate`** to create strings that match your exact pattern.

# Examples
#### Use `@app.payload` to register
- Describe your payload structure and call `Viorina.build_dict()` at the end
```python
import viorina            # For `app = viorina.Viorina()`
from viorina import Auto  # For describing schema


app = viorina.Viorina()


# Use `app.payload` to register
@app.payload
class Root:           # ... its child node `BranchA` not defined yet ...
    BranchA = Auto()  # => {"Root": { "BranchA": { ... } } }
    Name = "Anji"     # => {"Root": { "Name": "Anji", "BranchA": { ... } } }
    

@app.payload
class BranchA:        # ... the node `BranchA` defined later ...
    Age = 233         # => { "BranchA": { "Age": 233 } }
    

p = app.build_dict()  # ... build payload

# 
# {'Root': 
#     {'Name': 'Anji', 
#      'BranchA': {'Age': 233}
#     }
# }
```
#### Use descriptors to generate random data for fuzz testing
- Use `Text`, `Integer`, `Auto` descriptors to generate **random** mock values
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
    ChildNode = Auto()
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
