"""Structured output examples using Pydantic."""

from pydantic import BaseModel, Field

import ullm

# Example 1: Simple structured output
print("=== Example 1: Simple Structured Output ===")


class Person(BaseModel):
    name: str
    age: int
    occupation: str


response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Extract information: John is a 35-year-old software engineer. Return as JSON with name, age, and occupation.",
        }
    ],
    response_format=Person,
    max_tokens=100,
)

print(f"Response: {response.choices[0].message.content}")
# Parse the JSON response
try:
    person_data = Person.model_validate_json(response.choices[0].message.content)
    print(f"Parsed: {person_data.name}, {person_data.age}, {person_data.occupation}\n")
except Exception:
    print(f"Note: Structured output requires manual JSON parsing. Content: {response.choices[0].message.content}\n")

# Example 2: Complex nested structure
print("=== Example 2: Complex Nested Structure ===")


class Address(BaseModel):
    street: str
    city: str
    country: str


class Employee(BaseModel):
    name: str
    department: str
    salary: float
    address: Address


response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Generate a sample employee record with name, department, salary, and address (street, city, country). Return as JSON.",
        }
    ],
    response_format=Employee,
    max_tokens=200,
)

print(f"Response: {response.choices[0].message.content}\n")

# Example 3: List of structured items
print("=== Example 3: List of Items ===")


class Product(BaseModel):
    name: str
    price: float
    in_stock: bool


class ProductList(BaseModel):
    products: list[Product]


response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Generate 3 sample products with name, price, and stock status. Return as JSON array.",
        }
    ],
    response_format=ProductList,
    max_tokens=300,
)

print(f"Response: {response.choices[0].message.content}\n")

# Example 4: Using Field for validation
print("=== Example 4: Validated Fields ===")


class UserProfile(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=18, le=120)
    bio: str = Field(max_length=500)


# Generate the JSON schema to show validation rules
schema = UserProfile.model_json_schema()
print("Schema with validation:")
print(f"- Username: {schema['properties']['username']}")
print(f"- Email: {schema['properties']['email']}")
print(f"- Age: {schema['properties']['age']}")
print(f"- Bio: {schema['properties']['bio']}\n")

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Create a user profile for Alice with a valid email, age over 18, and a short bio. Return as JSON.",
        }
    ],
    response_format=UserProfile,
    max_tokens=200,
)

print(f"Response: {response.choices[0].message.content}")
