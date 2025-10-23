# Structured Output

Get validated JSON responses using Pydantic models.

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    response_format=Person
)
```

*(More details coming soon)*
