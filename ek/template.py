import re

_TEMPLATE_REGEX = re.compile(r"\{([^}]+)\}")


class MissingParameterValueError(Exception):
    pass


def populate_template(template: str, **kwargs) -> str:
    parameters = _TEMPLATE_REGEX.findall(template)
    missing_parameters = [
        parameter for parameter in parameters if parameter not in kwargs
    ]
    if missing_parameters:
        raise MissingParameterValueError(
            f"Missing parameters required in template: {missing_parameters}",
        )
    return template.format(**kwargs)
