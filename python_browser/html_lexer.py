ENTITIES = {"&gt;": ">", "&lt;": "<"}


def lex(body: str):
    text = ""
    in_tag = False

    # Ex. 1-4
    in_entity = False
    maybe_entity_str = ""

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif c == "&":
            in_entity = True
            maybe_entity_str += c
        elif in_entity:
            maybe_entity_str += c

            if len(maybe_entity_str) == 4:
                entity = ENTITIES.get(maybe_entity_str)

                if entity is not None:
                    text += entity
                else:
                    text += maybe_entity_str

                in_entity = False
                maybe_entity_str = ""
        elif not in_tag:
            text += c

    return text


# Ex. 1-5
def transform(body: str):
    text = ""

    for c in body:
        if c == "<":
            text += "&lt;"
        elif c == ">":
            text += "&gt;"
        else:
            text += c

    return text