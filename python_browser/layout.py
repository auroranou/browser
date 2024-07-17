from constants import HSTEP, VSTEP, WIDTH

# X position (right), Y position (bottom), character
DisplayListItem = tuple[float | int, float | int, str]


def layout(text: str, width: int = WIDTH) -> tuple[list[DisplayListItem], float]:
    display_list = []
    cursor_x: float = HSTEP
    cursor_y: float = VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x >= width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

        # Ex. 2-1
        if c == "\n":
            cursor_y += VSTEP * 1.5
            cursor_x = HSTEP

    return display_list, cursor_y