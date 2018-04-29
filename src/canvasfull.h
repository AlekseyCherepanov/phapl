/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */
#ifndef CANVASFULL_H
#define CANVASFULL_H

#include <QWidget>
#include <QList>

QT_BEGIN_NAMESPACE
class QPixmap;
class Window;
QT_END_NAMESPACE

class CanvasFull : public QWidget
{
    // %% Set appropriate access modifiers.

    Q_OBJECT

public:
    CanvasFull(QList<qreal> x, QList<qreal> y, QString texts[2], Window *window, QWidget *parent = 0);
    void paintEvent(QPaintEvent *event);
    QSize minimumSizeHint() const;
    QSize sizeHint() const;

    void leaveEvent(QEvent *event);
    void enterEvent(QEvent *event);
    void mouseMoveEvent(QMouseEvent *event);

    void mousePressEvent(QMouseEvent *event);
private:
    Window *m_window;

    QList<qreal> m_xList;
    QList<qreal> m_yList;
    qreal m_minX;
    qreal m_maxX;
    qreal m_midX;
    qreal m_minY;
    qreal m_maxY;
    qreal m_midY;
    QString m_texts[2];

    int m_mouse;
    int m_mouseX;
    int m_mouseY;

    QPixmap m_pixmap;
    bool m_pixmap_drawn;
    bool m_drawing;
};

#endif
