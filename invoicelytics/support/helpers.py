import json

from invoicelytics.entities.domain_entities import Invoice


def get_value(extracted_data_points: dict, instance: Invoice, attribute_name: str):
    try:
        dict_value = extracted_data_points.get(attribute_name)
        return dict_value if dict_value is not None else getattr(instance, attribute_name)
    except AttributeError:
        return None


def to_json_bytes(d: dict) -> bytes:
    """
    Convert an array of dictionaries to its bytes representation using JSON.

    Args:
        d (dict): dictionary to be converted.

    Returns:
        bytes: Bytes representation of the input dict.
    """
    # Convert dict to JSON string and then encode to bytes
    json_str = json.dumps(d)
    return json_str.encode("utf-8")
