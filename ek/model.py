from contextlib import suppress
from typing import cast

from pydantic import BaseModel

from ek.template import populate_template


class InvalidParameterError(Exception):
    pass


class EntityModel(BaseModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **dict(kwargs, **self._templated_vals(**kwargs)))

    @classmethod
    def primary_key(cls) -> dict[str, str]:
        primary_key = {"pk": cls.fill_template("pk")}
        with suppress(InvalidParameterError):
            primary_key["sk"] = cls.fill_template("sk")
        return primary_key

    @classmethod
    def fill_template(cls, parameter: str, **kwargs) -> str:
        template = cls._template_for_parameter(parameter)
        return (
            populate_template(template, **kwargs)
            if template
            else cast(str, kwargs.get(parameter))
        )

    @classmethod
    def _templated_vals(cls, **kwargs) -> dict[str, str]:
        vals = {}
        for property_ in cls.model_json_schema()["properties"]:
            if (
                cls._parameter_type(property_) == "string"
                and kwargs.get(property_) is None
            ):
                vals[property_] = cls.fill_template(property_, **kwargs)

        return vals

    @classmethod
    def _template_for_parameter(cls, parameter: str) -> str | None:
        return cls._parameter_info(parameter).get("default")

    @classmethod
    def _parameter_type(cls, parameter: str) -> str:
        return cls._parameter_info(parameter)["type"]

    @classmethod
    def _parameter_info(cls, parameter: str) -> dict:
        definition = cls.model_json_schema()["properties"].get(parameter)
        if not definition:
            raise InvalidParameterError(f"Missing parameter: {definition}")
        return definition


def get_model_name(model: type[EntityModel]) -> str:
    return model.__class__.__name__
