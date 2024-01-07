# Ek

A python library for DynamoDB single table designs.

## Key Features

## Installation

## Usage

> _Warning_ WIP

```python
import boto3
from ek import EntityModel, Table

class User(EntityModel):
    pk: str = "CM#{company_id}"
    sk: str = "US#{user_id}
    user_id: str
    company_id: str

class Company(EntityModel):
    pk: str = "CM#{company_id}"
    sk: str = "CM#{company_id}"
    company_id: str
    description: str

table = Table(boto3.resource(...), "MyTable", EntityClientSync)
user_client = table.register_model(UserModel)
company_client = table.register_model(Company)

user = User(user_id="123", company_id="345")
user_client.put_item(user)

retrieved_user = user_client.get_item(user_id="123", company_id="345")
```
