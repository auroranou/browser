class Text:
    def __init__(self, text: str):
        self.text = text


class Tag:
    def __init__(self, tag: str):
        self.tag = tag


ENTITIES = {"&lt;": "<", "&gt;": ">"}


def lex(body: str):
    out: list[Tag | Text] = []
    buffer: str = ""
    in_tag = False

    # Ex. 1-4
    in_entity = False
    maybe_entity_str = ""

    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        elif c == "&":
            in_entity = True
            maybe_entity_str += c
        elif in_entity:
            maybe_entity_str += c

            if len(maybe_entity_str) == 4:
                entity = ENTITIES.get(maybe_entity_str)

                if entity is not None:
                    buffer += entity
                else:
                    buffer += maybe_entity_str

                in_entity = False
                maybe_entity_str = ""
        else:
            buffer += c

    if not in_tag and buffer:
        out.append(Text(buffer))

    return out


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
