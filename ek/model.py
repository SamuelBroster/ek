from typing import cast

from pydantic import BaseModel

from ek.template import populate_template


class InvalidModelError(Exception):
    pass


class EntityModel(BaseModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **dict(kwargs, **self._templated_vals(**kwargs)))

    def _fill_template(self, parameter: str, **kwargs) -> str:
        template = self._template_for_parameter(parameter)
        return (
            populate_template(template, **kwargs)
            if template
            else cast(str, kwargs.get(parameter))
        )

    def _templated_vals(self, **kwargs) -> dict[str, str]:
        vals = {}
        for property_ in self.model_json_schema()["properties"]:
            if (
                self._parameter_type(property_) == "string"
                and kwargs.get(property_) is None
            ):
                vals[property_] = self._fill_template(property_, **kwargs)

        return vals

    def _template_for_parameter(self, parameter: str) -> str | None:
        return self._parameter_info(parameter).get("default")

    def _parameter_type(self, parameter: str) -> str:
        return self._parameter_info(parameter)["type"]

    def _parameter_info(self, parameter: str) -> dict:
        definition = self.model_json_schema()["properties"].get(parameter)
        if not definition:
            raise InvalidModelError(f"Missing parameter: {definition}")
        return definition
