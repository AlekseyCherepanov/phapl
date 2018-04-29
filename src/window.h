/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */
#ifndef WINDOW_H
#define WINDOW_H

#include <QWidget>

QT_BEGIN_NAMESPACE
class QBoxLayout;
class QPushButton;
class QLabel;
class QComboBox;
class QLineEdit;
QT_END_NAMESPACE

class Window : public QWidget
{
    // %% Set appropriate access modifiers.

    Q_OBJECT

public:
    Window();
    void setDotFooText(int y_or_x, const QString &text);

    QLineEdit *m_mnewton;
    QLineEdit *m_specials;

public slots:
    void setDotXText(const QString &text);
    void setDotYText(const QString &text);
    void start();

    void handleLink(const QString &link);
    void taskActivated(int i);

private:
    QString m_dotFooTexts[2];
    QList<QPointF> m_pointsList;
    QBoxLayout *m_layout;
    QPushButton *m_startButton;
    QComboBox *m_tasks;
    QLineEdit *m_dotXEdit;
    QLineEdit *m_dotYEdit;

    QWidget *m_panel;

    QStringList m_helpSwap;
    QList<QLabel *> m_helpLabels;
    QLabel *createHelpLabel(const char *normalText, const char *helpText);

    QWidget *wrapWithBorder(QWidget *widget);
};

#endif
