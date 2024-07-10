# Ex. 1-1
def make_headers(headers: dict[str, str]):
    headers_str = ""
    for key, value in headers.items():
        headers_str += f"{key}: {value}\r\n"
    return headers_str


def parse_cache_control_header(cache_control: str | None) -> dict[str, str | bool]:
    directives = {}

    if not cache_control or len(cache_control) == 0:
        return directives

    directives_arr = [x.strip() for x in cache_control.split(",")]
    for item in directives_arr:
        if "=" in item:
            key, value = item.split("=", 1)
            directives[key] = value
        else:
            directives[key] = True
    return directives
