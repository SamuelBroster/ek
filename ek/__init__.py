from ek.model import EntityModel
from ek.table import Table


class User(EntityModel):
    pk: str = "CO#{company}"
    sk: str = "US#{name}"
    company: str
    name: str


table = Table()
UserCollection = table.register_model(User)
user = UserCollection.get(company="myCompany", name="myName")
print(user.pk, user.company)
