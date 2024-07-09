from constants import HSTEP, VSTEP, WIDTH

# X position (right), Y position (bottom), character
DisplayListItem = tuple[int, int, str]


def layout(text: str, width: int = WIDTH) -> tuple[list[DisplayListItem], int]:
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x >= width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

        if c == "\n":
            cursor_y += VSTEP * 2
            cursor_x = HSTEP

    return display_list, cursor_y
