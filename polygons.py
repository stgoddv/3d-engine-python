import tkinter

HEIGHT = 240 * 2
WIDTH = 256 * 2

top = tkinter.Tk()
top.title('Ejemplo de aplicación 3d')
C = tkinter.Canvas(top, bg="black", height=HEIGHT, width=WIDTH)


def draw_pixel(x, y, *options):
    C.create_rectangle((x, y) * 2, *options)


def plotLineLow(x0, y0, x1, y1, *options):
    border = []
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = 2 * dy - dx
    y = y0
    for x in range(x0, x1):
        draw_pixel(x, y, *options)
        border.append((x, y))
        if D > 0:
            y = y + yi
            D = D - 2 * dx
        D = D + 2 * dy
    return border


def plotLineHigh(x0, y0, x1, y1, *options):
    border = []
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = 2 * dx - dy
    x = x0
    for y in range(y0, y1):
        draw_pixel(x, y, *options)
        border.append((x, y))
        if D > 0:
            x = x + xi
            D = D - 2 * dy
        D = D + 2 * dx
    return border


def draw_line(x0, y0, x1, y1, *options):
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            return plotLineLow(x1, y1, x0, y0, *options)
        else:
            return plotLineLow(x0, y0, x1, y1, *options)
    else:
        if y0 > y1:
            return plotLineHigh(x1, y1, x0, y0, *options)
        else:
            return plotLineHigh(x0, y0, x1, y1, *options)

def flood_fill(x, y, border, color):
    vCanvas = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]
    for pos in border:
        vCanvas[pos[0]][pos[1]] = 1
    if vCanvas[x][y]:
        return
    draw_pixel(x,y, {'fill':color, 'outline': '' })
    Q = []
    Q.append((x, y))
    while len(Q) != 0:
        n = Q.pop(0)
        x, y = n
        if not vCanvas[x-1][y]:
            draw_pixel(x-1, y, {'fill': color, 'outline': ''})
            Q.append((x-1, y))
            vCanvas[x-1][y] = 1
        if not vCanvas[x+1][y]:
            draw_pixel(x+1, y, {'fill': color, 'outline': ''})
            Q.append((x+1, y))
            vCanvas[x+1][y] = 1
        if not vCanvas[x][y-1]:
            draw_pixel(x, y-1, {'fill': color, 'outline': ''})
            Q.append((x, y-1))
            vCanvas[x][y-1] = 1
        if not vCanvas[x][y+1]:
            draw_pixel(x, y+1, {'fill': color, 'outline': ''})
            Q.append((x, y+1))
            vCanvas[x][y+1] = 1
    return

def draw_triangle(x0, y0, x1, y1, x2, y2, options):
    # Draw perimeter
    border_color = options.get('border', '#fff')
    border = draw_line(x0, y0, x1, y1, {'fill': border_color, 'outline': ''}) + \
             draw_line(x0, y0, x2, y2, {'fill': border_color, 'outline': ''}) + \
             draw_line(x1, y1, x2, y2, {'fill': border_color, 'outline': ''})
    # Fill triangle
    fill_color = options.get('fill', '#fff')
    x_m = int((x0 + x1 + x2) / 3)
    y_m = int((y0 + y1 + y2) / 3)
    flood_fill(x_m, y_m, border, fill_color)
    return None

draw_triangle(0, 20, 50, 70, 120, 240, {'border':'#fff', 'fill': '#2e8'})

C.pack()
top.mainloop()
