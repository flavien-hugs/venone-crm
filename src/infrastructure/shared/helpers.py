def formatted_number(obj):
    if obj is None:
        obj = 0.0
    try:
        number = "{:,.2f}".format(float(obj))
        return number.replace(",", " ")
    except (ValueError, TypeError):
        return str(obj)
