import pytest

from ek.model import EntityModel
from ek.template import InvalidParamsError


def test_entity_model():
    class EntityUnderTest(EntityModel):
        string: str
        template: str = "#{string}#"
        big_template: str = "#{number}#{string}#"
        empty_template: str = "empty"
        number: int
        number_default: int = 1

    entity = EntityUnderTest(string="string", number=2)
    assert entity.string == "string"
    assert entity.template == "#string#"
    assert entity.empty_template == "empty"
    assert entity.big_template == "#2#string#"
    assert entity.number == 2
    assert entity.number_default == 1


def test_entity_model_with_invalid_template():
    class EntityUnderTest(EntityModel):
        string: str
        template: str = "#{invalid}#"

    with pytest.raises(InvalidParamsError) as excinfo:
        EntityUnderTest(string="string")
    excinfo.match("invalid")


def test_entity_model_with_nested_template():
    class EntityUnderTest(EntityModel):
        string: str
        template: str = "#{invalid}#"
        nested_template: str = "{template}"

    with pytest.raises(InvalidParamsError) as excinfo:
        EntityUnderTest(string="string")
    excinfo.match("template")
