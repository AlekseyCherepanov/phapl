# -*- coding: utf-8 -*-
# Phase Plane Helper
# Python implementation

# Drawing method
# %% Use 'exec' as a fallback if weave is not available
drawer = 'exec'
drawer = 'cpp'

# %% Update documentation

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

# from PyQt4.QtScript import *

import math
from math import sqrt
import sys
from string import Template
import re

import fractions
import random

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
    cmd.maxima = "maxima.bat"
else:
    cmd.maxima = "maxima"
    # cmd.maxima = "./maxima"

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

layout = QVBoxLayout(window)

layout.addWidget(QLabel(
    u"""
Задайте параметры для следующей системы:<b><br>
\u1E8B = (a·x + b·y + c)·(d·x + e·y + f)<br>
\u1E8F = (g·x + h·y + j)</b>
    """.strip(),
    window))

inputs = QGridLayout()
layout.addLayout(inputs)

for i, t in enumerate([
    u"Особая точка 1, координата <b>x<sub>1</sub>:</b>",
    u"Особая точка 1, координата <b>y<sub>1</sub>:</b>",
    u"Особая точка 2, координата <b>x<sub>2</sub>:</b>",
    u"Особая точка 2, координата <b>y<sub>2</sub>:</b>",
    ]):
    l = QLabel(t, window)
    l.setAlignment(Qt.AlignRight)
    inputs.addWidget(l, i, 0, 1, 1)

edits = []
for i in range(4):
    t = QLineEdit(window)
    inputs.addWidget(t, i, 1, 1, 1)
    edits.append(t)

inputs.addWidget(QLabel(u"Выберите тип особой точки (вторая особая точка будет иметь тип седло):"), 4, 0, 1, 2)

point_types = [
    u"Неустойчивый узел",
    u"Устойчивый узел",
    # u"Седло",
    # %% это центр или фокус;
    u"Центр",
    u"Неустойчивый фокус",
    u"Устойчивый фокус",
    u"Неустойчивый вырожденный узел",
    u"Устойчивый вырожденный узел",
    u"Неустойчивый дикритический узел",
    u"Устойчивый дикритический узел"
]

types = QComboBox(window)
inputs.addWidget(types, 5, 0, 1, 2)

types_model = QStandardItemModel()

for t in point_types:
    types_model.appendRow([ QStandardItem(t) ])
types.setModel(types_model)
types.setModelColumn(0)

def do_toggle():
    t = toggle_button.text()
    t = str(3 - int(t[-1]))
    toggle_button.setText(u'Сделать седлом особую точку ' + t)
    show_input()

toggle_button = QPushButton(u'Сделать седлом особую точку 1', window)
inputs.addWidget(toggle_button, 6, 0, 1, 2)
conn(toggle_button, "clicked()",
     do_toggle)

inputs.addWidget(QLabel(u"Минимальное возможное значение произвольных постоянных:", window), 7, 0, 1, 1)
inputs.addWidget(QLabel(u"Максимальное возможное значение произвольных постоянных:", window), 8, 0, 1, 1)
for i in range(2):
    t = QLineEdit(window)
    inputs.addWidget(t, 7 + i, 1, 1, 1)
    edits.append(t)

integer_box = QCheckBox(u'Произвольные постоянные должны быть целыми числами', window)
layout.addWidget(integer_box)

input_data_label = QLabel('', window)
layout.addWidget(input_data_label)

def float_or(string, default):
    try:
        return float(string)
    except ValueError:
        return float(default)

def show_input(*ignored_args):
    vmin = float_or(edits[4].text(), -5.0)
    vmax = float_or(edits[5].text(), +5.0)
    vint = u''
    if integer_box.checkState():
        vint = u' и являются целыми числами'
    x1 = float_or(edits[0].text(), 0.0)
    y1 = float_or(edits[1].text(), 0.0)
    x2 = float_or(edits[2].text(), 1.0)
    y2 = float_or(edits[3].text(), 1.0)
    tt = toggle_button.text()[-1]
    t1 = t2 = u'Седло'
    if tt == '1':
        # Точка 2 - седло.
        t1 = point_types[types.currentIndex()]
    else:
        t2 = point_types[types.currentIndex()]
    if x1 == x2 and y1 == y2:
        x2 += 1
        y2 += 1
    r = (vmin, vmax, vint, x1, y1, t1, x2, y2, t2)
    t = u'Итого. Требования к задаче:\na, b, c, d, e, f, g, h, l принадлежат интервалу [{}, {}]{}.\nОсобые точки:\n({}, {}) - {},\n({}, {}) - {}'.format(*r)
    input_data_label.setText(t)
    return r

show_input()

for e in edits:
    conn(e, "textChanged(const QString &)",
         show_input)

conn(types, "activated(int)",
     show_input)

conn(integer_box, "stateChanged(int)",
     show_input)

def clean_sub():
    while the_panel_list:
        w = the_panel_list.pop()
        sub_layout.removeWidget(w)
        w.setParent(None)

the_panel_list = []
def panel_add(w):
    the_panel_list.append(w)
    sub_layout.addWidget(w)

# Wrapper to catch exceptions
def do_create():
    clean_sub()
    try:
        do_create_i()
    except Exception, exc:
        panel_add(QLabel(u"<h1>Ошибка</h1>", window))
        panel_add(QLabel(type(exc).__name__ + u"\n" + unicode(exc), window))


def maxima_read(output_stream):
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
                pass
                #qDebug("WARNING: rat replaced something")
            elif t.indexOf(":") > -1:
                # ** Unspecified line skipper.
                # %% Do that after concatenation.
                qDebug(QString("WARNING: we skipped a line due to a colon: %1").arg(t))
            else:
                if t.startsWith(" "):
                    output[-1] += t
                else:
                    output.append(t)

    # for l in output:
    #     print l
    # exit()

    return output

with open("solve.mac") as f:
    script = f.read()

def maxima_try_iter(ii, max_k, fx1, fy1, it1, fx2, fy2, it2):
    k = 0
    for t in ii:
        print t
        if t == None:
            return None
        k += 1
        # print k
        if k > max_k:
            return None
        maxima = QProcess()
        maxima.start(cmd.maxima, ["--very-quiet"])
        maxima.write("dotx : ({} * x + {} * y + {}) * ({} * x + {} * y + {}) $ doty : ({} * x + {} * y + {})$\n".format(*t))
        maxima.write("specials : []$\n")
        maxima.write("mnewtons : []$\n")
        maxima.write(script)
        maxima.closeWriteChannel()
        maxima.waitForFinished();
        output_stream = QTextStream(maxima)
        output = maxima_read(output_stream)
        special_points_count = int(output[7])
        if special_points_count != 2:
            continue

        tt, tx1 = output[8].split(' = ')
        assert tt == 'x'
        if str(tx1).startswith("%"):
            continue
        tx1 = float(tx1)
        if tx1 != fx1 and tx1 != fx2:
            continue

        tt, ty1 = output[9].split(' = ')
        assert tt == 'y'
        if str(ty1).startswith("%"):
            continue
        ty1 = float(ty1)
        if ty1 != fy1 and ty1 != fy2:
            continue

        tt, tx2 = output[8 + 29].split(' = ')
        assert tt == 'x'
        if str(tx2).startswith("%"):
            continue
        tx2 = float(tx2)
        if tx2 != fx1 and tx2 != fx2:
            continue

        tt, ty2 = output[9 + 29].split(' = ')
        assert tt == 'y'
        if str(ty2).startswith("%"):
            continue
        ty2 = float(ty2)
        if ty2 != fy1 and ty2 != fy2:
            continue

        tt1 = output[8 + 29 - 1]
        tt2 = output[8 + 2 * 29 - 1]
        if tx1 == fx1:
            if not (ty1 == fy1 and tx2 == fx2 and ty2 == fy2):
                continue
        else:
            # tx1 == fx2
            if not (ty1 == fx2 and tx2 == fx1 and ty2 == fy1):
                continue
            tt1, tt2 = tt2, tt1
        tt, tt1 = tt1.split(' = ')
        assert tt == 'type'
        tt1 = int(tt1)
        tt, tt2 = tt2.split(' = ')
        assert tt == 'type'
        tt2 = int(tt2)
        # print tt1, tt2
        if tt1 != it1 or tt2 != it2:
            continue
        # we found good system
        # print t
        return t
    return 0

def gen(vmin, vmax, vint, x1, y1, t1, x2, y2, t2):
    # return None on failures, return 0 if it is impossible to generate
    vint = bool(vint)
    x1 = fractions.Fraction(x1)
    y1 = fractions.Fraction(y1)
    x2 = fractions.Fraction(x2)
    y2 = fractions.Fraction(y2)
    fx1 = float(x1)
    fy1 = float(y1)
    fx2 = float(x2)
    fy2 = float(y2)
    yyxx1 = (y1 - y2) / (x1 - x2)
    yyxx2 = (x1 * y2 - y1 * x2) / (x1 - x2)
    types = (
        u"Особая точка\nне допускает\nлинеаризацию",
        u"Неустойчивый узел",
        u"Устойчивый узел",
        u"Седло",
        u"Центр",
        u"Неустойчивый фокус",
        u"Устойчивый фокус",
        u"Неустойчивый вырожденный узел",
        u"Устойчивый вырожденный узел",
        # ** 7а и 8а идут не по порядку, после всех.
        u"Неустойчивый дикритический узел",
        u"Устойчивый дикритический узел")
    it1 = types.index(t1)
    it2 = types.index(t2)
    if vint:
        la, lb, lc, ld, le, lf, lg, lh, lj = [ range(int(math.ceil(vmin)),
                                                     int(math.floor(vmax)) + 1)
                                               for i in range(9) ]
        if x1 - x2 == 0:
            if 0 not in lh:
                return 0
            # h = 0; g * x1 = - j
            lhgj = []
            for g in lg:
                for j in lj:
                    if g * x1 == - j:
                        lhgj.append((0, g, j))
        else:
            lhg = []
            for g in lg:
                for h in lh:
                    if g == - h * yyxx1:
                        lhg.append((g, h))
            lhgj = []
            for g, h in lhg:
                for j in lj:
                    if h * yyxx2 == -j:
                        lhgj.append((h, g, j))
        if lhgj == []:
            return 0
        labc = []
        for a in la:
            for b in lb:
                for c in lc:
                    if a * x1 + b * y1 == -c:
                        labc.append((a, b, c))
        if labc == []:
            return 0
        ldef = []
        for d in ld:
            for e in le:
                for f in lf:
                    if d * x2 + e * y2 == -f:
                        ldef.append((d, e, f))
        if ldef == []:
            return 0
        # print map(len, (labc, ldef, lhgj))
        cs = []
        for a in labc:
            for b in ldef:
                for c in lhgj:
                    cs.append(a + b + c)
        def give_from_cs(cs):
            while cs:
                ti = random.randint(0, len(cs) - 1)
                t = cs.pop(ti)
                yield t
        return maxima_try_iter(give_from_cs(cs), 100,
                               fx1, fy1, it1, fx2, fy2, it2)
    else:
        # no requirement of integer coefficients
        def give_random():
            max_k = 1000000
            def pick():
                return float(random.randint(vmin * 10, vmax * 10)) / 10
                # return float(random.randint(int(math.ceil(vmin)),
                #                             int(math.floor(vmax))))
            while True:
                if (x1 - x2) == 0:
                    if 0 < vmin or 0 > vmax:
                        return
                    h = 0
                    for k in xrange(max_k):
                        g = pick()
                        j = - g * x1
                        if j < vmin or j > vmax:
                            continue
                        break
                    else:
                        yield None
                else:
                    for k in xrange(max_k):
                        h = pick()
                        g = - h * yyxx1
                        if g < vmin or g > vmax:
                            continue
                        j = - h * yyxx2
                        if j < vmin or j > vmax:
                            continue
                        break
                    else:
                        yield None
                # print h, g, j
                for k in xrange(max_k):
                    a = pick()
                    b = pick()
                    c = - (a * x1 + b * y1)
                    if c < vmin or c > vmax:
                        continue
                    break
                else:
                    yield None
                # print a, b, c
                for k in xrange(max_k):
                    d = pick()
                    e = pick()
                    f = - (d * x2 + e * y2)
                    if f < vmin or f > vmax:
                        continue
                    break
                else:
                    yield None
                yield a, b, c, d, e, f, g, h, j
        return maxima_try_iter(give_random(), 100,
                               fx1, fy1, it1, fx2, fy2, it2)
        return None
    return None

def do_create_i():
    tr = show_input()
    # print tr
    vmin, vmax, vint, x1, y1, t1, x2, y2, t2 = tr
    r = gen(*tr)
    if r == None:
        raise Exception(
            u'Не получается создать задачу с заданными условиями.')
    if r == 0:
        raise Exception(
            u'Невозможно создать задачу с заданными условиями.')
    assert type(r) == tuple
    # print len(r)
    # print r
    panel_add(QLabel(
        u"""
\u1E8B = ({}·x + {}·y + {})·({}·x + {}·y + {})<br>
\u1E8F = ({}·x + {}·y + {})</b>
        """.strip().format(*r),
        window))
    x_list = [ x1, x2 ]
    y_list = [ y1, y2 ]
    dot_foo_js_texts = [
        '({} * x + {} * y + {}) * ({} * x + {} * y + {})'.format(*r),
        '({} * x + {} * y + {})'.format(*r[6 : ]) ]
    w = QWidget(window)
    h = QHBoxLayout(w)
    panel_add(w)
    widget = Canvas(x_list, y_list, dot_foo_js_texts, 600, 600, window)
    w = wrap_with_border(widget)
    h.addWidget(w)
    h.addStretch()

create_button = QPushButton(u'Создать задачу', window)
layout.addWidget(create_button)
conn(create_button, "clicked()",
     do_create)

the_panel = QWidget(window)
layout.addWidget(the_panel)
sub_layout = QVBoxLayout(the_panel)

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
                  ("black", 1))
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
                            #+ "#define NPY_NO_DEPRECATED_API\n"
                            #+ "#define NPY_1_7_API_VERSION\n"
                            ),
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
        self.pixmap.fill(Qt.white)

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
        # def mouse_press_event(event):
        #     if event.button() & (Qt.LeftButton | Qt.MiddleButton):
        #         l = mnewton if event.button() & Qt.LeftButton else specials
        #         t = l.text()
        #         l.setText(t
        #                   + (", " if t.indexOf("]") > -1 else "")
        #                   + "[x = {0}, y = {1}]".format(*translate_back_from_event(event)))
        #         # %% Remember the system (texts) at start and reset back here.
        #         start()
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
        # self.mousePressEvent = mouse_press_event

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
    # if zenburn:
    #     color = "#dcdccc"
    w.setStyleSheet(".QWidget { border: 1px solid " + color + " }")
    QVBoxLayout(w).addWidget(widget)
    return w

layout.addStretch()

# We don't enter main loop under ipython to allow interactive
# manipulations.
if not vars().has_key('get_ipython'):
    sys.exit(app.exec_())
