def map_with_dtypes(annotation):
    proxy = str(annotation).lower()
    if "str" in proxy:
        return "string"
    if "int" in proxy:
        return "integer"
    if "list" in proxy:
        return "array of"
    if "dict" in proxy:
        return "object"