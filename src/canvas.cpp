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

#include "canvas.h"

Canvas::Canvas(qreal x, qreal y, QString texts[2], QWidget *parent)
    : QWidget(parent)
{
    setAutoFillBackground(true);
    QPalette pal = palette();
//    pal.setColor(backgroundRole(), "#ffeaff");
    pal.setColor(QPalette::Window, "white");
    setPalette(pal);

    m_pixmap_drawn = m_drawing = false;

    m_x = x;
    m_y = y;
    m_texts[0] = texts[0];
    m_texts[1] = texts[1];

    setMouseTracking(true);
    m_mouse = 0;
}

void Canvas::enterEvent(QEvent *event)
{
    qDebug() << "enter";
    m_mouse = 1;
}

void Canvas::mouseMoveEvent(QMouseEvent *event)
{
    qDebug() << "move";
    m_mouseX = event->pos().x();
    m_mouseY = event->pos().y();
    // %% Translation was copy-pasted.
    QToolTip::showText(
        mapToGlobal(QPoint()),
        QString("(%1, %2)").arg(
            qreal(m_mouseX) * 2.0 / height() + m_x - 1).arg(
                qreal(height() - m_mouseY) * 2.0 / height() + m_y - 1));
    repaint();
}

void Canvas::leaveEvent(QEvent *event)
{
    qDebug() << "leave";
    m_mouse = 0;
    repaint();
}

void Canvas::paintEvent(QPaintEvent *event)
{

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

    qreal x, y, rx, ry, t, vx, vy;
    bool colored;

    if (!m_drawing && size() != m_pixmap.size()) {
        m_drawing = true;
        m_pixmap = QPixmap::grabWidget(this);
        m_drawing = false;
        update();
    }

    if (m_drawing) {

    QPainter p(this);
    // %% Не высота, а меньшее из высоты и ширины.
    p.scale(height() / 2, height() / 2);
    p.translate(QPointF(-m_x + 1, -m_y + 1));
//#define fg_color "#ff0032"
#define fg_color "dark magenta"
    p.setPen(QPen(QColor(fg_color), 1 / height()));
//#define fg2_color "#32aa32"
#define fg2_color "green"

    // %% Magic number are about random.
    int parts = height() / 10 /* pixels */;
    for (int i = 0; i <= parts; i++) {
        // %% Нужны ещё проверки, вх и ву не являются нулями
        //  % одновременно.
#define S\
        x = rx;\
        y = ry;\
        //qDebug() << x << y;
#define F\
        t = 1;\
        for (int k = 0; k < height() * 10 && x <= m_x + 1 && y <= m_y + 1 && x >= m_x - 1 && y >= m_y - 1 && t; k++)
// Скалярное произведение вектора скорости в точке и вектора от точки
// к ближайшей точке покоя при приближении должно быть больше нуля.
#define CH ((m_x - x) * vx + (m_y - y) * vy > 0)
#define A\
            QScriptValueList args;\
            args << x << y;\
            vx = fx.call(QScriptValue(), args).toNumber();\
            vy = fy.call(QScriptValue(), args).toNumber();\
            if (colored) {\
                p.setPen(QPen(QColor(CH ? fg_color : fg2_color), 1 / height()));\
            }\
            p.drawPoint(QPointF(x, m_y - (y - m_y)));\
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
#define LINEP S F { A; I; }
#define LINEN S F { A; D; }
#define LINE LINEP LINEN

        colored = true;
        rx = m_x - 1 + i * 2.0 / parts;
        ry = m_y - 1;
        LINE;
        rx = m_x - 1;
        ry = m_y - 1 + i * 2.0 / parts;;
        LINE;
        rx = m_x - 1 + i * 2.0 / parts;
        ry = m_y + 1;
        LINE;
        rx = m_x + 1;
        ry = m_y - 1 + i * 2.0 / parts;;
        LINE;
    }

    } // end if(!m_mouse)

    QPainter p(this);
    if (!m_drawing) {
        // %% Copy-pasting is evil!
        p.setPen(QPen(QColor(fg_color), 1 / height()));
        p.drawPixmap(QPoint(0, 0), m_pixmap);

        if (m_mouse) {
            colored = false;
            // %% Не высота, а меньшее из высоты и ширины.
            p.scale(height() / 2, height() / 2);
            p.translate(QPointF(-m_x + 1, -m_y + 1));
            p.setPen(QPen(QColor("red"), qreal(8) / height()));
            // ** Translation back
            // %% Auto translation
            rx = qreal(m_mouseX) * 2.0 / height() + m_x - 1;
            ry = qreal(height() - m_mouseY) * 2.0 / height() + m_y - 1;
            LINEP;
            p.setPen(QPen(QColor("blue"), qreal(8) / height()));
            LINEN;
        }
    }

    // Center
    //p.drawPoint(QPointF(m_x, m_y));
}

QSize Canvas::minimumSizeHint() const
{
    return QSize(300, 300);
}

QSize Canvas::sizeHint() const
{
    return minimumSizeHint();
}
