def fake_object(attributes: dict):
    return type(
        "fake_object",
        (object,),
        attributes,
    )
