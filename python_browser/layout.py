from constants import HSTEP, VSTEP, WIDTH

# X position (right), Y position (bottom), character
DisplayListItem = tuple[float | int, float | int, str]


def layout(
    text: str, width: int = WIDTH, rtl: bool = False
) -> tuple[list[DisplayListItem], float]:
    display_list = []

    x_start = width - HSTEP if rtl else HSTEP
    x_end = HSTEP if rtl else width - HSTEP
    x_inc = -HSTEP if rtl else HSTEP

    cursor_x: float = x_start
    cursor_y: float = VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += x_inc

        x_out_of_bound = cursor_x < x_end if rtl else cursor_x > x_end
        if x_out_of_bound:
            cursor_y += VSTEP
            cursor_x = x_start

        # Ex. 2-1
        if c == "\n":
            cursor_y += VSTEP * 1.5
            cursor_x = x_start

    return display_list, cursor_y
