/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */
#include <QtGui>
#include <QtScript>
#include <QDebug>
#include <QPixmap>
#include <QToolTip>

#include "canvasfull.h"

// %% Move all that Window stuff into window.cpp, use signals and slots.
#include "window.h"

CanvasFull::CanvasFull(QList<qreal> x, QList<qreal> y, QString texts[2], Window *window, QWidget *parent)
    : QWidget(parent), m_window(window)
{
    setAutoFillBackground(true);
    QPalette pal = palette();
    // pal.setColor(backgroundRole(), "#ffeaff");
    pal.setColor(QPalette::Window, "white");
    // pal.setColor(QPalette::Window, "lightgreen");
    setPalette(pal);

    m_pixmap_drawn = m_drawing = false;

    m_xList = x;
    m_yList = y;
    m_texts[0] = texts[0];
    m_texts[1] = texts[1];

    setMouseTracking(true);
    m_mouse = 0;
}

void CanvasFull::enterEvent(QEvent *event)
{
    qDebug() << "enter";
    m_mouse = 1;
}

// %% Translation was copy-pasted.
// %% *Y in GET_X_* ? Typo, fortunately not effective.
#define GET_X_FROM_EVENT() (qreal(event->pos().x()) * (m_maxY - m_minY) / height() + m_midX - (m_maxY - m_minY) / 2.0)
#define GET_Y_FROM_EVENT() (qreal(height() - event->pos().y()) * (m_maxY - m_minY) / height() + m_midY - (m_maxY - m_minY) / 2.0)
#define STRING_XY(format)         QString(format).arg(GET_X_FROM_EVENT()).arg(GET_Y_FROM_EVENT())

void CanvasFull::mouseMoveEvent(QMouseEvent *event)
{
    qDebug() << "move";
    m_mouseX = event->pos().x();
    m_mouseY = event->pos().y();
    QToolTip::showText(mapToGlobal(QPoint()), STRING_XY("(%1, %2)"));
    repaint();
}

void CanvasFull::leaveEvent(QEvent *event)
{
    qDebug() << "leave";
    m_mouse = 0;
    repaint();
}

void CanvasFull::mousePressEvent(QMouseEvent *event)
{
    qDebug() << "mouse press";
    // if (event->button() & (Qt::LeftButton | Qt::RightButton)) {
    if (event->button() & (Qt::LeftButton | Qt::MiddleButton)) {
        QLineEdit *l = event->button() & Qt::LeftButton
            ? m_window->m_mnewton
            : m_window->m_specials;
        QString t = l->text();
        l->setText(
            t
            + (t.indexOf("]") > -1 ? ", " : "")
            + STRING_XY("[x = %1, y = %2]"));
        m_window->start();
    }
}

void CanvasFull::paintEvent(QPaintEvent *event)
{
    // Вычисляем края множества точек
    qreal minX, maxX;
    qreal minY, maxY;
    // %% Empty lists?
    minX = maxX = m_xList[0];
    minY = maxY = m_yList[0];
    foreach (qreal tx, m_xList) {
        if (tx > maxX) {
            maxX = tx;
        }
        if (tx < minX) {
            minX = tx;
        }
    }
    foreach (qreal ty, m_yList) {
        if (ty > maxY) {
            maxY = ty;
        }
        if (ty < minY) {
            minY = ty;
        }
    }
    minX -= 1;
    minY -= 1;
    maxX += 1;
    maxY += 1;

    qreal hw = (maxX - minX) / 2.0;
    qreal hh = (maxY - minY) / 2.0;
    if (hw > hh) {
        qreal dwh = hw - hh;
        maxY += dwh;
        minY -= dwh;
    } else {
        qreal dhw = hh - hw;
        maxX += dhw;
        minX -= dhw;
    }
    qreal midX, midY;
    midX = (minX + maxX) / 2.0;
    midY = (minY + maxY) / 2.0;

    // qreal midX, midY;
    // midX = (minX + maxX) / 2.0;
    // midY = (minY + maxY) / 2.0;
    // qreal hw = (maxX - minX) / 2.0;
    // qreal hh = (maxY - minY) / 2.0;
    // if (hw > hh) {
    //     hh = hw;
    // }
    // minX = midX - hh;
    // minY = midY - hh;
    // maxX = midX + hh;
    // maxY = midY + hh;

    m_minX = minX;
    m_maxX = maxX;
    m_midX = midX;
    m_minY = minY;
    m_maxY = maxY;
    m_midY = midY;


    // %% fx, fy could be initialized once.
    QScriptEngine e;
#define E(fun) e.evaluate(fun " = Math." fun ";");
    E("pow");
    E("sin");
    E("cos");
    E("tan");
    E("atan");
    E("asin");
    E("acos");
    E("sqrt");
    E("abs");
    E("log");
#undef E
    e.evaluate("e = Math.E");
    e.evaluate("pi = Math.PI");
    e.evaluate("arctg = Math.atan");
    QString sx("(function (x, y) { return %1; })");
    sx = sx.arg(m_texts[0]);
    QString sy("(function (x, y) { return %1; })");
    sy = sy.arg(m_texts[1]);
    qDebug() << sx << sy;
    QScriptValue fx = e.evaluate(sx);
    QScriptValue fy = e.evaluate(sy);

    qreal x, y, rx, ry, t;

    if (!m_drawing && size() != m_pixmap.size()) {
        m_drawing = true;
        m_pixmap = QPixmap::grabWidget(this);
        m_drawing = false;
        update();
    }

    if (m_drawing) {

    QPainter p(this);
    // %% Не высота, а меньшее из высоты и ширины.
    p.scale(height() / (maxY - minY), height() / (maxY - minY));
    p.translate(QPointF(-midX + (maxY - minY) / 2.0, -midY + (maxY - minY) / 2.0));
    // ** We need to inverse coordinates at every draw.
#define INVERSE(t) midY - (t - midY)
    // %% Inverse coordinates here.
    // %% Make this lines appear correctly (violet as OX,
    //  % and cyan above) not changing coordinates.
    // p.setPen(QPen(QColor("#FF00FF"), 30.0 / height()));
    // p.drawLine(QLine(m_minX - 1, 0, m_maxX + 1, 0));
    // p.setPen(QPen(QColor("#00FFFF"), 30.0 / height()));
    // p.drawLine(QLine(m_minX - 1, 1, m_maxX + 1, 1));

    // Grid
#define GRID_COLOR "lightgrey"
#define GRID_COLOR_AXIS "violet"
    // ** Assignment to int rounds things.
    for (int i = m_minX - 1; i < m_maxX + 1; i++) {
        // %% What is the difference between 1 / height() and 1.0 / height() ?
        p.setPen(QPen(QColor(i ? GRID_COLOR : GRID_COLOR_AXIS), 1 / height()));
        // p.drawLine(QLine(i, m_minY - 1, i, m_maxY + 1));
        p.drawLine(QLineF(i, INVERSE(m_minY - 1), i, INVERSE(m_maxY + 1)));
    }
    for (int j = m_minY - 1; j < m_maxY + 1; j++) {
        p.setPen(QPen(QColor(j ? GRID_COLOR : GRID_COLOR_AXIS), 1 / height()));
        // %% After avoiding INVERSE check lines' positions.
        // p.drawLine(QLine(m_minX - 1, j, m_maxX + 1, j));
        // ** It is important to floating point line due to INVERSE.
        p.drawLine(QLineF(m_minX - 1, INVERSE(j), m_maxX + 1, INVERSE(j)));
    }
#undef GRID_COLOR_AXIS
#undef GRID_COLOR

    p.setPen(QPen(QColor("black"), 1 / height()));

    // foreach (qreal px, m_xList) {
    //     foreach (qreal py, m_yList) {
    for (int pi = 0; pi < m_xList.length(); pi++) {
        qreal px = m_xList[pi];
        qreal py = m_yList[pi];
        {

    // %% Magic number are about random.
    int parts = height() / 20 /* pixels */ / m_xList.length();
    for (int i = 0; i <= parts; i++) {
        // %% Нужны ещё проверки, вх и ву не являются нулями
        //  % одновременно.
#define S\
        x = rx;\
        y = ry;\
        //qDebug() << x << y;
#define F\
        t = 1;\
        for (int k = 0; k < height() * 10 && x <= maxX && y <= maxY && x >= minX && y >= minY && t; k++)
#define A\
            p.drawPoint(QPointF(x, INVERSE(y)));   \
            QScriptValueList args;\
            args << x << y;\
            qreal vx = fx.call(QScriptValue(), args).toNumber();\
            qreal vy = fy.call(QScriptValue(), args).toNumber();\
            t = qSqrt(vx * vx + vy * vy) * height() / 2;\
            if (t) {\
                vx /= t;\
                vy /= t;\
            }\
            //qDebug() << k << x << y << vx << vy << t;
#define I\
            x += vx;\
            y += vy;
#define D\
            x -= vx;\
            y -= vy;
#define C if (k > 10 && (x - rx) * (x - rx) + (y - ry) * (y - ry) < (vx * vx + vy * vy) * 25 ) { break; }
#define LINEP S F { A; I; C }
#define LINEN S F { A; D; C }
#define LINE LINEP LINEN
        rx = px - 1 + i * 2.0 / parts;
        ry = py - 1;
        LINE;
        rx = px - 1;
        ry = py - 1 + i * 2.0 / parts;;
        LINE;
        rx = px - 1 + i * 2.0 / parts;
        ry = py + 1;
        LINE;
        rx = px + 1;
        ry = py - 1 + i * 2.0 / parts;;
        LINE;
    }

    }} // end of foreachs

    } // end if(!m_mouse)

    QPainter p(this);
    if (!m_drawing) {
        // %% Copy-pasting is evil!
        p.setPen(QPen(QColor("black"), 1 / height()));
        p.drawPixmap(QPoint(0, 0), m_pixmap);

        if (m_mouse) {
            // %% Не высота, а меньшее из высоты и ширины.
            p.scale(height() / (maxY - minY), height() / (maxY - minY));
            p.translate(QPointF(-midX + (maxY - minY) / 2.0, -midY + (maxY - minY) / 2.0));
            // ** Translation back
            // %% Auto translation
            rx = qreal(m_mouseX) * (maxY - minY) / height() + midX - (maxY - minY) / 2.0;
            ry = qreal(height() - m_mouseY) * (maxY - minY) / height() + midY - (maxY - minY) / 2.0;
            p.setPen(QPen(QColor("red"), qreal(16) / height()));
            LINEP;
            p.setPen(QPen(QColor("blue"), qreal(16) / height()));
            LINEN;
        }
    }

    // Center
    //p.drawPoint(QPointF(m_x, m_y));
}

QSize CanvasFull::minimumSizeHint() const
{
    return QSize(600, 600);
}

QSize CanvasFull::sizeHint() const
{
    return minimumSizeHint();
}
