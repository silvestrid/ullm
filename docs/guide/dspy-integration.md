# DSPy Integration

Use ullm as a drop-in replacement for litellm in DSPy.

```python
import dspy
import ullm

# Configure DSPy to use ullm
lm = dspy.LM(model="openai/gpt-4o-mini")
dspy.configure(lm=lm)
```

*(More details coming soon)*
