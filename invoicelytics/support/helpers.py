from invoicelytics.entities.domain_entities import Invoice


def get_value(extracted_data_points: dict, instance: Invoice, attribute_name: str):
    try:
        dict_value = extracted_data_points.get(attribute_name)
        return dict_value if dict_value is not None else getattr(instance, attribute_name)
    except AttributeError:
        return None
