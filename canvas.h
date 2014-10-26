/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */
#ifndef CANVAS_H
#define CANVAS_H

#include <QWidget>

QT_BEGIN_NAMESPACE
class QPixmap;
QT_END_NAMESPACE

class Canvas : public QWidget
{
    // %% Set appropriate access modifiers.

    Q_OBJECT

public:
    Canvas(qreal x, qreal y, QString texts[2], QWidget *parent = 0);
    void paintEvent(QPaintEvent *event);
    QSize minimumSizeHint() const;
    QSize sizeHint() const;

    void leaveEvent(QEvent *event);
    void enterEvent(QEvent *event);
    void mouseMoveEvent(QMouseEvent *event);

private:
    qreal m_x;
    qreal m_y;
    QString m_texts[2];

    int m_mouse;
    int m_mouseX;
    int m_mouseY;

    QPixmap m_pixmap;
    bool m_pixmap_drawn;
    bool m_drawing;
};

#endif
