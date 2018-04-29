# -*- coding: utf-8 -*-
# Phase Plane Helper
# Python implementation

# Copyright © 2014 Aleksey Cherepanov <lyosha@openwall.com>
# Redistribution and use in source and binary forms, with or without
# modification, are permitted.

# %% Update documentation

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

# from PyQt4.QtScript import *

from math import sqrt
import sys
from string import Template
import re

from traceback import print_exc

# python drawer
from math import log, sin, cos, atan, e, tan, asin, acos
arctg = atan
# cpp drawer
from scipy import weave
import sip

# For benchmarks
import time

def conn(obj, signature, callback):
    QObject.connect(obj, SIGNAL(signature),
                    callback)

class Cmd:
    pass
cmd = Cmd()

if sys.platform == 'win32':
    cmd.erase_generated = "erasegenerated.bat"
    cmd.maxima = "maxima.bat"
    cmd.compile_tex = "compiletex.bat"
else:
    cmd.erase_generated = "./erasegenerated.sh"
    cmd.maxima = "maxima"
    # cmd.maxima = "./maxima"
    cmd.compile_tex = "./compiletex.sh"

# if __name__ == "__main__":

make_app = False
try:
    app
except:
    make_app = True
if make_app:
    app = QApplication(sys.argv)
scroll_area = QScrollArea()
# ** This one is close to term 'window' while it is not a window.
window = QWidget(scroll_area)
# %% http://qt-project.org/doc/qt-4.8/layout.html says that layout
# should be set first.
scroll_area.setWidget(window)
scroll_area.setWidgetResizable(True)
scroll_area.show()
# window.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

zenburn = True
zenburn = False

if zenburn:
    # My zenburn
    app.setStyleSheet(
        """
QWidget {
    background-color: #353535;
    color: #dcdccc;
    font-family: "Liberation Mono";
    font-size: 16px;
}
QPushButton {
    background-color: #2f2f2f;
    border: 1px solid #d48440;
}
QPushButton:hover {
    background-color: #3f3434;
}
QPushButton:pressed {
    background-color: #252525;
    color: #f4a460;
}
QLineEdit, QSpinBox, QTextEdit, QListView {
    border: 1px solid #009900;
    background-color: #2f2f2f;
    selection-background-color: #2f3f2f;
}
QLineEdit:focus, QSpinBox:focus, QTextEdit:focus, QListView:focus {
    border: 1px solid #00cc00;
}
QLineEdit:hover, QSpinBox:hover, QTextEdit:hover, QListView:hover {
    background-color: #343f34;
}
/* %% Under mouse full drop-down is green. */
QComboBox {
    background-color: #2f2f2f;
    border: 1px solid #ac7cac;
    selection-background-color: #3f343f;
}
QComboBox:focus {
    border: 1px solid #cc9ccc;
    selection-background-color: #3f343f;
}
QComboBox:hover {
    background-color: #3f343f;
}
QPushButton:focus {
    border: 1px solid #f4a460;
}
QToolTip {
    background-color: #353535;
    color: #dcdccc;
    font-family: "Liberation Mono";
    font-size: 16px;
    border: 1px solid #FFFF00;
}
    """)

if not zenburn:
    palette = scroll_area.palette()
    palette.setColor(window.backgroundRole(), QColor("white"))
    scroll_area.setPalette(palette)

g_panel = [QWidget()]

def hex_name(dot_x, dot_y):
    return QDir("tasksimages").filePath(QString(QString("\"%1\", \"%2\"").arg(dot_x).arg(dot_y).toUtf8().toHex()))
    # return QDir("tasksimages").filePath('"{0}", "{1}"'.format(dot_x, dot_y).encode('utf-8').encode('hex'))

# ** We do not use first element.
help_labels = [0]
help_swap = [0]

layout = QVBoxLayout(window)

def create_help_label(normal_text, help_text):
    n = QString.fromUtf8(normal_text)
    bg = 'lightyellow'
    if zenburn:
        bg = '#323f32'
    h = n + ' <p style="background: ' + bg + ';">' + QString.fromUtf8(help_text)
    p = "HELP"
    k = len(help_labels)
    style = ''
    if zenburn:
        style = ' style="color: #acacdc"'
    sn = QString.fromUtf8('<a href="help%1"' + style + '>(&#9658; кликните сюда для получения справки)</a>').arg(k)
    sh = QString.fromUtf8('<a href="help%1"' + style + '>(&#9660; кликните сюда для скрытия справки)</a>').arg(k)
    n = n.replace(p, sn)
    h = h.replace(p, sh)
    l = QLabel(n, window)
    conn(l, "linkActivated(const QString &)",
         handle_link)
    l.setWordWrap(True)
    l.setMaximumWidth(500)
    help_labels.append(l)
    help_swap.append(h)
    return l

def handle_link(link):
    t = link
    t.replace("help", "")
    help_id, ok = t.toInt()
    if not ok:
        raise BaseException("BUG: help link id with wrong number: {1}".format(t))
    # ** We use 0 for non-existent links. Do not use it!
    if help_id > 0:
        l = help_labels[help_id]
        t = l.text()
        l.setText(help_swap[help_id])
        help_swap[help_id] = t

layout.addWidget(create_help_label(
    "<b>Введите систему</b> HELP",
    """Для ввода системы можно использовать переменные (x, y), константы
(e, pi и любые числа; десятичная часть отделяется точкой), функции
(sin, cos, sqrt (корень квадратный), tan (тангенс), atan или arctg
(арктангенс), asin (арксинус), acos (арккосинус), abs (модуль), ln или
log (логарифм)), операции (+, -, *, /, ^ (возведение в степень)),
Круглые скобки для группирования. Вокруг аргумента функции надо
обязательно ставить скобки."""))

tasks = QComboBox(window)
layout.addWidget(tasks)

tasks_model = QStandardItemModel()
tasks_file = QFile("tasks.txt")

tasks_file.open(QIODevice.ReadOnly)
tasks_stream = QTextStream(tasks_file)
k = 1
while not tasks_stream.atEnd():
    row = []
    line = tasks_stream.readLine()
    t = line.mid(1, line.length() - 2).split('", "')
    def add(item_text):
        row.append(QStandardItem(item_text))
    add(t[0])
    add(t[1])
    add(QString.fromUtf8("%1)  %2").arg(k).arg(line))
    tasks_model.appendRow(row)
    tasks_model.setData(tasks_model.index(tasks_model.rowCount() - 1, 2),
                        QPixmap(hex_name(t[0], t[1])),
                        Qt.DecorationRole)
    k += 1
tasks_file.close()
tasks.setModel(tasks_model)
tasks.setModelColumn(2)
def decoration(index):
    return tasks_model.data(tasks_model.index(index, 2), Qt.DecorationRole).toPyObject()

max_width = max(
    decoration(i).width()
    for i in xrange(tasks_model.rowCount()))
v_padding = 10
h_padding = 20
max_width += h_padding
for i in xrange(tasks_model.rowCount()):
    m = decoration(i)
    n = QPixmap(max_width, m.height() + v_padding * 2)
    n.fill()
    p = QPainter(n)
    # %% A bit darker color but lighter than "grey"?
    p.setPen(QPen(QColor("lightgrey"), 1))
    p.drawLine(QLine(max_width - 1, v_padding, max_width - 1, n.height() - v_padding))
    p.drawPixmap(0, v_padding, m)
    tasks_model.setData(tasks_model.index(i, 2), n, Qt.DecorationRole)
    del p

def task_activated(task_number):
    for where, what in (dot_x_edit, 0), (dot_y_edit, 1):
        where.setText(tasks_model.data(tasks_model.index(task_number, what)).toString())

conn(tasks, "activated(int)",
     task_activated)

system = QGridLayout()
layout.addLayout(system)

# %% Картинки стоит переконвертировать при запуске с текущего dpi.
system.addWidget(QLabel("<img src='static/system.png' />", window), 0, 0, 2, 1)

if not zenburn:
    palette.setColor(window.backgroundRole(), QColor("grey"))

dot_foo_texts = ["", ""]
def set_dot_foo_text(y_or_x, text):
    dot_foo_texts[y_or_x] = text
def set_dot_x_text(text):
    set_dot_foo_text(0, text)
def set_dot_y_text(text):
    set_dot_foo_text(1, text)
dot_foo_setters = (set_dot_x_text, set_dot_y_text)

class PreSetupPainter(object):
    def __init__(self, painter, callback):
        self.painter = painter
        self.callback = callback
    def __call__(self, device):
        # return SetupPainter(self.painter, device, self.callback) if type(device) != QPixmap else SetupPainter(self.painter, device, lambda: 1)
        return SetupPainter(self.painter, device, self.callback)

class SetupPainter(object):
    def __init__(self, painter, device, callback):
        self.painter = painter
        self.device = device
        self.callback = callback
    def __enter__(self):
        self.painter.begin(self.device)
        self.callback()
    def __exit__(self, type, value, traceback):
        self.painter.end()

# def output_transform(t):
#     print t.m11(), t.m12(), t.m13()
#     print t.m21(), t.m22(), t.m23()
#     print t.m31(), t.m32(), t.m33()

# Compatibility for exec way
double = float

# %% Use 'exec' as a fallback if weave is not available
drawer = 'exec'
drawer = 'cpp'

# exec way, no js
python_template = Template("""
def draw_half_line_ii(dif_x,
                      min_x, mid_x, max_x,
                      min_y, mid_y, max_y,
                      painter, direction,
                      x, y, colored,
                      pen1, pen2,
                      max_length, height):
    # %% Need more checks. vx & vy are not zeros at the same time.
    # output_transform(painter.transform())
    t = 1
    hd = height / dif_x
    if colored:
        p = False
        painter.setPen(pen2)
    for k in xrange(max_length):
        if min_x > x or x > max_x or min_y > y or y > max_y or not t:
            break
        vx = $dot_x
        vy = $dot_y
        if colored:
            # painter.setPen(pen1 if (mid_x - x) * vx + (mid_y - y) * vy > 0 else pen2)
            # Call setPen only if color was really changed.
            n = (mid_x - x) * vx + (mid_y - y) * vy > 0
            if n != p:
                painter.setPen(pen1 if n else pen2)
                p = n
        # %% Invert y through QPainter
        painter.drawPoint(QPointF(x, mid_y - (y - mid_y)))
        # %% What's this? I normalize vector... Why?
        t = sqrt(vx * vx + vy * vy) * hd
        if t:
            x += direction * (vx / t)
            y += direction * (vy / t)
        # C++ had this here, why?
        # For what is this? To not stuck in special points?
        # if (k > 10 && (x - rx) * (x - rx) + (y - ry) * (y - ry) < (vx * vx + vy * vy) * 25 ) { break; }
""")

# cpp way with painter.drawPoints(), i.e. with buffer
# %% Do parallelism: draw several lines in parallel. Use SSE.
# %% Try long double for computations.
cpp_template = Template('''
#define e M_E
#define pi M_PI
QPainter *painter = reinterpret_cast<QPainter *>(painter_i);
QPen pen1;
QPen pen2;
if (colored) {
    pen1 = *reinterpret_cast<QPen *>(pen1_i);
    pen2 = *reinterpret_cast<QPen *>(pen2_i);
}
double t = 1;
int p = 2;
int c = 0;
#define max 30
QPointF ps[max];
while (max_length-- && min_x < x && x < max_x && min_y < y && y < max_y && t) {
    double vx = $dot_x;
    double vy = $dot_y;
    if (colored) {
        int n = (mid_x - x) * vx + (mid_y - y) * vy > 0;
        if (n != p) {
            painter->drawPoints(ps, c);
            c = 0;
            painter->setPen(n ? pen1 : pen2);
            p = n;
        }
    }
    if (c == max) {
        painter->drawPoints(ps, max);
        c = 0;
    }
    ps[c++] = QPointF(x, mid_y - (y - mid_y));
    t = sqrt(vx * vx + vy * vy) * height_dif_x;
    if (t) {
        x += direction * (vx / t);
        y += direction * (vy / t);
    }
}
#undef max
painter->drawPoints(ps, c);
''')

class Canvas(QWidget):
    def sizeHint(self):
        return QSize(self._width, self._height)
    def minimumSizeHint(self):
        return QSize(self._width, self._height)
    def __init__(self, xs, ys, texts, width, height, parent = None):
        self._width, self._height = width, height
        super(QWidget, self).__init__(parent)
        # self.setMinimumSize(QSize(width, height))
        # self.setMaximumSize(QSize(width, height))
        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if len(xs) == 0:
            xs.append(0)
            ys.append(0)
        single = len(xs) == 1
        # %% Why doesn't pad = 1.0 work with cpp way?
        pad = 1.00000001
        min_x, min_y, max_x, max_y = (
            f(v) for f in (lambda l: min(l) - pad, lambda l: max(l) + pad)
                 for v in (xs, ys))
        # Expand to square
        # ** After expansion assumption is used: max_x - min_x == max_y - min_y
        c_width = max_x - min_x
        c_height = max_y - min_y
        half_dif = abs(c_width - c_height) / 2.0
        if c_width > c_height:
            min_y -= half_dif
            max_y += half_dif
        else:
            min_x -= half_dif
            max_y += half_dif
        (mid_x, dif_x), (mid_y, dif_y) = (((float(a) + b) / 2.0, float(b) - a)
            for (a, b) in ((min_x, max_x),
                           (min_y, max_y)))
        height_dif_x = float(height) / dif_x
        self.setMouseTracking(True)
        self.mouse = False
        self.mouse_x, self.mouse_y = 0, 0
        # for fun in "pow sin cos tan atan asin acos sqrt abs log".split(' '):
        #     eng.evaluate(fun + " = Math." + fun)
        # for exp in "e = Math.E", "pi = Math.PI", "arctg = Math.atan":
        #     eng.evaluate(exp)
        # Painter setup
        def create_pen(color_name, thickness):
            pen = QPen(QColor(color_name), thickness)
            pen.setCosmetic(True)
            return pen
        colors = (("dark magenta", 1),
                  ("green", 1),
                  ("red", 4),
                  ("blue", 4),
                  ("lightgrey", 1),
                  ("violet", 1),
                  ("#dcdccc" if zenburn else "black", 1))
        fg_pen, fg2_pen, red_pen, blue_pen, grid_pen, axis_pen, black_pen = (
            create_pen(color, thickness)
            for color, thickness in colors)
        p = QPainter()
        self.painter = p
        def scale_and_translate():
            # %% Не высота, а меньшее из высоты и ширины.
            p.scale(float(height) / dif_x, float(height) / dif_y)
            p.translate(QPointF(- min_x, - min_y))
            # %% Invert Y not manually.
            # p.scale(1, -1)
        setup_painter = PreSetupPainter(p, scale_and_translate)
        # Wrappers to keep named parameters in python part.
        # Also avoids closure to {min,mid,max}_{x,y}, dif_x.

        # 1/2 in JS is 0.5, 1/2 in C++ and python is 0. It makes all
        # sqrt things fail due transform into pow(..., 1/2).
        # %% Leave sqrt as is for performance reasons.
        for i in 0, 1:
            # %% It could break log2() .
            # %% It breaks 1e... notation.
            texts[i] = re.sub(r'(\d+(?:\.?\d+)?)', r'double(\1)', str(texts[i]))

        if drawer == 'cpp':
            # cpp way with painter
            def draw_half_line(painter, direction,
                               x, y, painter_setup, colored,
                               pen, pen1, pen2,
                               max_length, height):
                with painter_setup:
                    if pen:
                        painter.setPen(pen)
                    code = cpp_template.substitute(
                        dot_x = texts[0], dot_y = texts[1])
                    painter_i, pen1_i, pen2_i = [
                        # %% Use sipConvertToType in C++ part instead
                        # of unwrapinstance here. It should be more
                        # portable.
                        sip.unwrapinstance(o) if o else 0
                        for o in painter, pen1, pen2]
                    # %% Try to insert max_length and other persistent
                    # params into the code as constants.
                    # %% Direction and colored could be promoted to
                    # python code using several variants of the code.
                    d = {
                        "min_x": float(min_x),
                        "mid_x": float(mid_x),
                        "max_x": float(max_x),
                        "min_y": float(min_y),
                        "mid_y": float(mid_y),
                        "max_y": float(max_y),
                        "direction": float(direction),
                        "x": float(x),
                        "y": float(y),
                        "colored": int(colored),
                        "max_length": int(max_length),
                        # "height": float(height),
                        # "dif_x": float(dif_x),
                        "height_dif_x": float(height_dif_x),
                        "painter_i": painter_i,
                        # "painter_o": painter,
                        "pen1_i": pen1_i,
                        "pen2_i": pen2_i
                    }
                    weave.inline(
                        str(code), d.keys(), d,
                        # support_code = "#include <QPainter>\n#include <sip.h>",
                        support_code = (
                            "#include <QPainter>\n"
                            + "#define NPY_NO_DEPRECATED_API\n"
                            + "#define NPY_1_7_API_VERSION\n"),
                        # %% From qt's Makefile, differs from system
                        # to system.
                        include_dirs = [
                            '/usr/share/qt4/mkspecs/linux-g++-64',
                            '/usr/include/qt4/QtCore',
                            '/usr/include/qt4/QtGui',
                            '/usr/include/qt4',
                            '/usr/include/qt'
                            ],
                        library_dirs = [
                            '/usr/lib/x86_64-linux-gnu'
                            ],
                        # extra_compile_args = ['-O3'],
                        libraries = [
                            'QtGui',
                            'QtCore',
                            'pthread'
                            ])

        if drawer == 'exec':
            # Exec way
            exec python_template.substitute(
                dot_x = texts[0], dot_y = texts[1]) in globals(), locals()
            draw_half_line_i = draw_half_line_ii
            def draw_half_line(painter, direction,
                               x, y, painter_setup, colored,
                               pen, pen1, pen2,
                               max_length, height):
                with painter_setup:
                    if pen:
                        painter.setPen(pen)
                    draw_half_line_i(dif_x,
                                     min_x, mid_x, max_x,
                                     min_y, mid_y, max_y,
                                     painter, direction,
                                     x, y, colored,
                                     pen1, pen2,
                                     max_length, height)

        # Sample way with JS
        # def draw_half_line(painter, direction,
        #                    x, y, painter_setup, colored,
        #                    pen, pen1, pen2,
        #                    max_length, height):
        #     with painter_setup:
        #         if pen:
        #             painter.setPen(pen)
        #         t = 1
        #         eng = QScriptEngine()
        #         for fun in "pow sin cos tan atan asin acos sqrt abs log".split(' '):
        #             eng.evaluate(fun + " = Math." + fun)
        #         for exp in "e = Math.E", "pi = Math.PI", "arctg = Math.atan":
        #             eng.evaluate(exp)
        #         funcs = [eng.evaluate(QString("(function (x, y) { return %1; })").arg(t))
        #                  for t in texts]
        #         for k in xrange(max_length):
        #             if not (min_x <= x <= max_x
        #                     and min_y <= y <= max_y
        #                     and t):
        #                 break
        #             # vx = eval(str(texts[0]))
        #             # vy = eval(str(texts[1]))
        #             args = [QScriptValue(x), QScriptValue(y)]
        #             vx = funcs[0].call(QScriptValue(), args).toNumber()
        #             vy = funcs[1].call(QScriptValue(), args).toNumber()
        #             if colored:
        #                 painter.setPen(
        #                     pen1 if (mid_x - x) * vx + (mid_y - y) * vy > 0 else pen2)
        #             painter.drawPoint(QPointF(x, mid_y - (y - mid_y)))
        #             t = sqrt(vx * vx + vy * vy) * height / dif_x
        #             if t:
        #                 vx /= t
        #                 vy /= t
        #             x += direction * vx
        #             y += direction * vy

        self.pixmap = QPixmap(width, height)
        self.pixmap.fill(QColor("#353535") if zenburn else Qt.white)

        # Initial lines
        # %% хочу заменить на цикл по точкам как в canvasfull.cpp
        for px, py in zip(xs, ys):
            # %% Magic number, it is about random.
            parts = int(30 / len(xs))
            for i in xrange(parts + 1):
                for x, y in ((px - 1 + i * 2.0 / parts, py - 1),
                             (px - 1, py - 1 + i * 2.0 / parts),
                             (px - 1 + i * 2.0 / parts, py + 1),
                             (px + 1, py - 1 + i * 2.0 / parts)):
                    for direction in 1, -1:
                        draw_half_line(p, direction, x, y,
                                       painter_setup = setup_painter(self.pixmap),
                                       colored = single,
                                       pen = black_pen, pen1 = fg_pen, pen2 = fg2_pen,
                                       max_length = height * 10,
                                       height = height)

        # Grid
        # %% Grid over initial lines?
        with setup_painter(self.pixmap):
            def invert(y):
                return mid_y - (y - mid_y)
            for i in xrange(int(min_x - 1), int(max_x + 1)):
                p.setPen(grid_pen if i else axis_pen)
                p.drawLine(QLineF(i, invert(min_y - 1), i, invert(max_y + 1)))
            for i in xrange(int(min_y - 1), int(max_y + 1)):
                p.setPen(grid_pen if i else axis_pen)
                p.drawLine(QLineF(min_x - 1, invert(i), max_x + 1, invert(i)))

        # Event handlers
        def translate_back_from_event(event):
            # %% Auto translation
            mouse_x = event.pos().x()
            mouse_y = event.pos().y()
            return (float(mouse_x) * dif_x / height + min_x,
                    float(height - mouse_y) * dif_y / height + min_y)
        def mouse_press_event(event):
            if event.button() & (Qt.LeftButton | Qt.MiddleButton):
                l = mnewton if event.button() & Qt.LeftButton else specials
                t = l.text()
                l.setText(t
                          + (", " if t.indexOf("]") > -1 else "")
                          + "[x = {0}, y = {1}]".format(*translate_back_from_event(event)))
                # %% Remember the system (texts) at start and reset back here.
                start()
        def enter_event(event):
            self.mouse = True
        def mouse_move_event(event):
            if height == 0:
                return
            x, y = translate_back_from_event(event)
            QToolTip.showText(
                    self.mapToGlobal(QPoint()),
                    QString("(%1, %2)").arg(x).arg(y))
            self.mouse_x = x
            self.mouse_y = y
            self.repaint()
        def leave_event(event):
            self.mouse = False
            self.repaint()
        def paint_event(event):
            # QWidget.paintEvent(self, event)
            if self.size() != self.minimumSize():
                return
            # No scale and translation here.
            p.begin(self)
            p.drawPixmap(QPoint(0, 0), self.pixmap)
            p.end()
            if self.mouse:
                x, y = self.mouse_x, self.mouse_y
                for direction in 1, -1:
                    pen = red_pen if direction == 1 else blue_pen
                    draw_half_line(p, direction, x, y,
                                   painter_setup = setup_painter(self),
                                   colored = False,
                                   pen = pen, pen1 = None, pen2 = None,
                                   max_length = height * 10, height = height)
        self.enterEvent = enter_event
        self.paintEvent = paint_event
        self.leaveEvent = leave_event
        self.mouseMoveEvent = mouse_move_event
        self.mousePressEvent = mouse_press_event

# %% Use of @pyqtSlot() ?
# Wrapper to be connected as slot. It is needed to redefine the
# function without full restart.
def start():
    start_i()

# Wrapper to catch exceptions
def start_i():
    try:
        start_ii()
    except Exception, exc:
        print_exc()
        g_panel[0].layout().addWidget(
            # %% Better message?
            QLabel("<h1>Error</h1><pre>{0}</pre>".format(exc)))

def start_ii():
    start_button.setEnabled(False)
    if g_panel[0]:
        g_panel[0].setParent(None)
        del g_panel[0]
    g_panel.append(QWidget(window))
    layout.insertWidget(layout.count() - 1, g_panel[0])
    subl = QVBoxLayout(g_panel[0])

    postponed_labels = []

    QProcess.execute(cmd.erase_generated)

    maxima = QProcess()
    maxima.start(cmd.maxima, ["--very-quiet"])
    script = QFile("solve.mac")
    script.open(QIODevice.ReadOnly)

    # ** Here is a preamble for maxima. Make a separate script if it is too big.
    # %% Use subst in maxima for that.
    maxima.write("e : %e$ pi : %pi$ ln : log$ arctg : atan$\n")

    print >> sys.stderr, '"{0}", "{1}"'.format(*dot_foo_texts)
    maxima.write(QString("dotx : %1$ doty : %2$\n").arg(dot_foo_texts[0]).arg(dot_foo_texts[1]).toUtf8())
    # %% Should we use variable to track specials.text() like dot_foo_texts?
    maxima.write(QString("specials : [%1]$\n").arg(specials.text()).toUtf8());
    maxima.write(QString("mnewtons : [%1]$\n").arg(mnewton.text()).toUtf8());
    maxima.write(script.readAll());
    maxima.closeWriteChannel();
    maxima.waitForFinished();
    output_stream = QTextStream(maxima)
    output = []
    # maxima режет слишком длинные строки при выводе TeX'а, поэтому
    # мы склеиваем строки, когда первая начинается с долларов, но не
    # заканчивается ими, до тех пор, пока не найдём строку,
    # заканчивающуюся долларами.
    while not output_stream.atEnd():
        t = output_stream.readLine()
        # qDebug(t)
        # %% было бы неплохо показывать предупреждения в gui
        if not t.isEmpty():
            # %% Do that in maxima.
            if t.startsWith("algsys: tried"):
                qDebug("WARNING: algsys error was skipped")
            elif t.startsWith("log: encountered log(0)"):
                qDebug("WARNING: log(0) error was skipped")
            elif t.startsWith("rat: replaced"):
                qDebug("WARNING: rat replaced something")
            elif t.indexOf(":") > -1:
                # ** Unspecified line skipper.
                # %% Do that after concatenation.
                qDebug(QString("WARNING: we skipped a line due to a colon: %1").arg(t))
            else:
                if t.startsWith(" "):
                    output[-1] += t
                else:
                    output.append(t)
    # %% Proper names.
    lines_per_point = 29
    lines_preamble = 7 + 1
    # for i in xrange(len(output)):
    #     qDebug(QString("maxima %1 (+%2): %3").arg(i).arg((i - lines_preamble) % lines_per_point).arg(output[i]))
    qDebug(QString("maxima's output length: %1").arg(len(output)))

    # subl.addWidget(QLabel("DEBUG " + str(tasks.my)))

    tex_strings = []
    tex_labels = []
    subl.addWidget(create_help_label(
        "<b>Исследуемая система</b> HELP",
        "Здесь Вы видите запись системы в виде, близком к рукописному. Проверьте его."))
    tex_x, tex_y = output[4:6]
    for s in tex_x, tex_y:
        s.replace('$$', '')
    tex_system = QString(
        """$$\\left\\{\\begin{aligned}
             \\dot{x} &= %1 \\\\
             \\dot{y} &= %2 \\\\
             \\end{aligned}\\right.$$""")
    tex_strings.append(tex_system.arg(tex_x).arg(tex_y))
    system_label = QLabel(window)
    postponed_labels.append(
        (system_label,
         QString('<img src="generated/pp%1.png" />').arg(len(tex_strings))))
    subl.addWidget(system_label)
    tex_labels.append(system_label)

    subl.addWidget(create_help_label(
        "<b>Особые точки</b> HELP",
        """В таблице ниже приведены особые точки системы и фазовые портреты их
окрестностей (квадрате размера со стороной 2 и центром в исследуемой
особой точке). Фиолетовым цветом на данных фазовых портретах показаны
точки, вектор скорости которых направлен к особой точке, зелёным - от
особой точки. При наведении мыши на фазовый портрет на нём строится
дополнительная фазовая кривая, раскрашенная в два цвета: красная часть
показывает положительное направление движения точки по фазовой кривой
из положения указателя (увеличение времени), синяя - отрицательное
направление (уменьшение времени)."""))
    # wid = QWidget(window)
    # wid.setFixedHeight(340 * 2 + 200)
    # grid = QGridLayout(wid)
    # subl.addWidget(wid)
    grid = QGridLayout()
    # grid.setSizeConstraint(QLayout.SetFixedSize)
    grid.setSpacing(0)
    def grid_add_widget(widget, row, col):
        app.processEvents()
        grid.addWidget(wrap_with_border(widget, row != 0), row, col)
    subl.addLayout(grid)
    headers = (
        "№",
        "Координаты",
        "Корни<br>характеристического<br>уравнения",
        "Точка покоя",
        "Фазовый портрет<br>в окрестности точки",
        "Устойчивость<br>(неустойчивость)<br>тривиального<br>решения")
    pos = 0
    for s in headers:
        l = QLabel(QString.fromUtf8("<b>" + s + "</b>"), window)
        l.setAlignment(Qt.AlignHCenter)
        grid_add_widget(l, 0, pos)
        pos += 1

    x_list, y_list = [], []
    dot_foo_js_texts = output[2:4]
    for s in dot_foo_js_texts:
        s.replace('%', '')
    special_points_count, ok = output[7].toInt()
    print ">> special points: ", special_points_count
    # return
    for idx in xrange(1, special_points_count + 1):
        grid_add_widget(QLabel(QString("%1").arg(idx), window), idx, 0)

        # Номер строки начала вывода о текущей особой точке.
        o = lines_preamble + (idx - 1) * lines_per_point
        # Запоминаем значения для построения графика.
        for i, s in (0, "x = "), (1, "y = "):
            output[o + i].replace(s, '')
        # Запоминаем значения для компиляции теха.
        for i, x, xr, j, y, yr, s, pos in ((2, "x=", "",
                                            3, "y=", "",
                                            "$$(%1, %2)$$",
                                            1),
                                           (19, "lambda", "lambda_1",
                                            20, "lambda", "lambda_2",
                                            "$$%1, %2$$",
                                            2)):
            for t in i, j:
                output[o + t].replace('$$', '')
            for t, tx, tr in (i, x, xr), (j, y, yr):
                output[o + t].replace(tx, tr)
            print ">out>", QString(s).arg(output[o + i]).arg(output[o + j])
            tex_strings.append(QString(s).arg(output[o + i]).arg(output[o + j]))
            l = QLabel(window)
            postponed_labels.append((l, QString('<img src="generated/pp%1.png" />').arg(len(tex_strings))))
            tex_labels.append(l)
            grid_add_widget(l, idx, pos)
        (x, _), (y, _) = (s.toDouble() for s in output[o:o + 2])

        # Строим график.
        # Рисуем фазовый портрет окрестности особой точки.
        x_list.append(x)
        y_list.append(y)
        grid_add_widget(Canvas([x], [y], dot_foo_js_texts, 300, 300, window), idx, 4)

        # Показываем тип точки.
        type_string = output[o + 28]
        type_string.replace('type = ', '')
        type, ok = type_string.toInt()
        if type < 0:
            type = 0
        types = (
            "Особая точка\nне допускает\nлинеаризацию",
            "Неустойчивый узел",
            "Устойчивый узел",
            "Седло",
            "Центр",
            "Неустойчивый фокус",
            "Устойчивый фокус",
            "Неустойчивый вырожденный узел",
            "Устойчивый вырожденный узел",
            # ** 7а и 8а идут не по порядку, после всех.
            "Неустойчивый дикритический узел",
            "Устойчивый дикритический узел")
        u = "Неустойчиво"
        a = "Асимптотически устойчиво"
        l = "Устойчиво по Ляпунову"
        stabilities = (
            "Особая точка\nне допускает\nлинеаризацию",
            u,
            a,
            u,
            l,
            u,
            a,
            u,
            a,
            u,
            a)
        # Тип точки
        grid_add_widget(QLabel(QString.fromUtf8(types[type])), idx, 3)
        print ">type>", types[type]
        # Устойчивость
        grid_add_widget(QLabel(QString.fromUtf8(stabilities[type])), idx, 5)
        print ">stability>", stabilities[type]

        grid.addItem(QSpacerItem(0, 0), idx, 6)
    grid.setColumnStretch(6, 1)

    # Вызываем тех.
    for s in tex_strings:
        s.replace('\\%', '')
    tex = ("""\\documentclass[a4paper,12pt]{article}
              \\usepackage[utf8]{inputenc}
              \\usepackage{amsmath}
              \\usepackage{amssymb}
              \\usepackage{geometry}
              \\usepackage{latexsym}
              \\usepackage[russian]{babel}"""
              + ("""\\usepackage{color}
                    \\definecolor{my1}{RGB}{220,220,204}
                    \\definecolor{my2}{RGB}{53,53,53}
                    \\color{my1}
                    \\pagecolor{my2}
                 """ if zenburn else "")
              + """\\pagestyle{empty}
                   \\begin{document}"""
              + ("\n\\clearpage\n".join(str(s) for s in tex_strings))
              + "\\end{document}")
    tex = QString(tex)
    tex_generated = QFile("generated/pp.tex")
    tex_generated.open(QIODevice.WriteOnly)
    tex_generated.write(tex.toUtf8())
    tex_generated.close()
    QProcess.execute(cmd.compile_tex)
    for l, s in postponed_labels:
        l.setText(s)
    app.processEvents()
    # ** Тут может быть необходимо вызывать обновление картинок, но пока это не нужно.

    # # ** Image saving for task images autogeneration.
    # # %% Check return code.
    # # %% Slashes on Windows?
    # # %% Filename size.
    # QFile(QDir("generated").filePath("pp1.png")).copy(hex_name(m_dotFooTexts[0], m_dotFooTexts[1]))

    if special_points_count == 0:
        x_list.append(0)
        y_list.append(0)
        subl.addWidget(QLabel(QString.fromUtf8("Особые точки не найдены")))

    # Добавляем полный фазовый портрет
    subl.addWidget(create_help_label(
        "<b>Общий фазовый портрет</b> HELP",
        """Ниже приведён общий фазовый портрет системы. На нём представлены
           все особые точки системы плюс окрестность шириной 1. Все
           лини чёрные. При наведении мыши так же проводится
           дополнительная фазовая кривая."""))
    h_layout = QHBoxLayout()
    subl.addLayout(h_layout)
    h_layout.addWidget(wrap_with_border(Canvas(x_list, y_list, dot_foo_js_texts, 600, 600, window)))
    h_layout.addStretch()
    start_button.setEnabled(True)

def wrap_with_border(widget, fix_size = False):
    w = QWidget(window)
    # if fix_size:
    #     # ** This is workaround to add some space below drawing when there
    #     # more than 1 drawing in the grid.
    #     # %% Try size policy or something like that instead. Or maybe
    #     # other way to form a table.
    #     w.setFixedHeight(340)
    #     # w.setMinimumHeight(widget.minimumHeight() + 20)
    color = "black"
    if zenburn:
        color = "#dcdccc"
    w.setStyleSheet(".QWidget { border: 1px solid " + color + " }")
    QVBoxLayout(w).addWidget(widget)
    return w

dot_foo_edits = [None, None]
for i in 0, 1:
    edit = QLineEdit(window)
    dot_foo_edits[i] = edit
    if not zenburn:
        # Set grey "background" to make grey bottom and right borders.
        # "Real" background stays white.
        edit.setPalette(palette)
    system.addWidget(edit, i, 1)
    conn(edit, "textChanged(const QString &)",
         dot_foo_setters[i])
    # ** It may be better to move focus to next line edit if it first line.
    conn(edit, "returnPressed()",
         start)
dot_x_edit, dot_y_edit = dot_foo_edits

layout.addWidget(create_help_label(
    "Точки для поиска решения методом Ньютона HELP",
    """Из этих точек будет начат поиск решений методом Ньютона. Формат
    описания такой же, как у дополнительных точек исследования."""))
mnewton = QLineEdit(window)
layout.addWidget(mnewton)
conn(mnewton, "returnPressed()",
     start)

layout.addWidget(create_help_label(
    "Дополнительные точки исследования HELP",
    """Это поле позволяет вручную ввести список точек для исследования.
Они будут добавлены к списку особых точек, найденных программой, и
будут исследованы как особые точки, даже если не являются таковыми.
Это поле стоит использовать, <b>если программа не может найти особые
точки</b>, находит не все особые точки и для управления границами
построения общего фазового портрета. Изменение границ общего фазового
портрета возможно, потому что все исследуемые точки (плюс окрестность
радиуса 1) отображаются на общем фазовом портрете. Каждая точка
вводится формате <b>[x=значение, y=значение]</b>. Список разделён
запятыми. Например, чтобы получить фазовый портрет ширины и высоты 10
с центром в начале координат (при условии отсутствия точек за
пределами этого квадрата), надо ввести: <b>[x=-5, y=-5], [x=5,
y=5]</b> или [x=5, y=-5], [x=-5, y=5]."""))
specials = QLineEdit(window)
layout.addWidget(specials)
conn(specials, "returnPressed()",
     start)

start_button = QPushButton(QString.fromUtf8("Исследовать и построить!"), window)
layout.addWidget(start_button)
conn(start_button, "clicked()",
     start)
start_button.setAutoDefault(True)

layout.addStretch()

# for i in 2, 6, 27: # range(0, 31):
#     print ">> spe num ", i
#     task_activated(i)
#     start()

# for i in range(0, 31):
#     print ">> spe num ", i
#     task_activated(i)
#     start()

task_activated(0)
# dot_x_edit.setText(QString("(x + y)^2 - 1"))
# dot_y_edit.setText(QString("- y^2 - x + 1"))
# dot_x_edit.setText(QString("-3*x*y"))
# dot_y_edit.setText(QString("-y^2-1+x^(4/3)-2*1/10*x"))

# # %% Debug
# clock = time.clock()
# start()
# print 'start() time is ', time.clock() - clock

# # Show all at once
# for i in range(1, 31):
#     # if i == 13 or i == 24:
#     #     continue
#     task_activated(i - 1)
#     tasks.my = i
#     start_ii()
#     g_panel[0] = QWidget()

# We don't enter main loop under ipython to allow interactive
# manipulations.
if not vars().has_key('get_ipython'):
    sys.exit(app.exec_())

