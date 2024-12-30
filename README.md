# polimer

**polimer** is an automated callstack synthesis framework (based on annotations)

## Basic idea

- Define annotations based on payload id (not just type id)
    - e.g. `l: 'price_list'` insead of `l: list`
- Automatically invoke argument initializers based on payload id
    - e.g. call `def get_price_list() -> 'price_list'`
- Simplify end-user code

## Quick-demo

1. Install **polimer**
```bash
pip install polimer
```

2. Annotate your methods with payload ids:

<h5 a><strong><code>prices.py</code></strong></h5>

```python
import random

def get_prices(length=10) -> 'price_list':
    return [random.random() for _ in range(length)]

def calc_avg_price(p: 'price_list'):
    return sum(p) / len(p)
```

3. Import your entrypoints via **polimer**
<h5 a><strong><code>demo.py</code></strong></h5>

```python
from prices import *
from polimer import prices

print(prices.calc_avg_price())
```
