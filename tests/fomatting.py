from typing import List

from TelgramWrapper.prompts import _get_variable_names, _has_formatting


def _test_format_message(message_text: str, variables: List[str], input_dict: dict) -> str:
    result_message = message_text
    for var in variables:
        result_message = result_message.replace(f"{{{var}}}", str(input_dict.get(var, "")))
    return result_message


if __name__ == "__main__":
    print(_has_formatting("hi {name} aaaa"))
    test_text = "{name} {surname} is {name}, age {age}"
    test_vars = _get_variable_names(test_text)
    test_context = {
        "name": "Giuseppe",
        "surname": "Sborretti",
        "age": 98
    }
    print(
        _test_format_message(
            test_text,
            test_vars,
            test_context
        )
    )