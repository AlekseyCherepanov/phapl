/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */
#include <QtGui>

#include "window.h"
#include "canvas.h"
#include "canvasfull.h"

// ** Platform/package specific macros.
#ifdef Q_OS_WIN32
#   define ERASEGENERATED "erasegenerated.bat"
#   define MAXIMA "maxima.bat"
#   define COMPILETEX "compiletex.bat"
#else
#   define ERASEGENERATED "./erasegenerated.sh"
#   define MAXIMA "maxima"
#   define COMPILETEX "./compiletex.sh"
#endif

// %% Make an inline function for that.
// %% Make one argument instead of 2.
#define HEX_NAME(dotX, dotY) \
    QDir("tasksimages").filePath(QString("\"%1\", \"%2\"").arg(dotX).arg(dotY).toUtf8().toHex())


Window::Window()
{
    // ** We do not use first element.
    m_helpLabels << 0;
    m_helpSwap << 0;

//    setStyleSheet("QWidget { border: 1px solid black }");

    m_layout = new QBoxLayout(QBoxLayout::TopToBottom, this);
    setLayout(m_layout);

    QPalette pal = palette();
    pal.setColor(backgroundRole(), "white");
    setPalette(pal);

    m_layout->addWidget(
        createHelpLabel(
            "<b>Введите систему</b> HELP",
            // %% Reformat
            "Для ввода системы можно использовать переменные (x, y), константы "
            "(e, pi и любые числа; десятичная часть отделяется точкой), функции "
            "(sin, cos, sqrt (корень квадратный), tan (тангенс), atan или arctg (арктангенс), "
            "asin (арксинус), acos (арккосинус), abs (модуль), ln или log (логарифм)), операции (+, -, *, "
            "/, ^ (возведение в степень)), Круглые скобки для группирования. Вокруг "
            "аргумента функции надо обязательно ставить скобки."));

    // setStyleSheet("QComboBox QAbstractItemView { background-color: yellow; decoration-position: right; }");
    // setStyleSheet("QComboBox QAbstractItemView::item { background-color: light green; }");

    m_tasks = new QComboBox(this);
    m_layout->addWidget(m_tasks);


    // setStyleSheet("QComboBox QAbstractItemView { background-color: lightgreen; }");

    QStandardItemModel *tasksModel = new QStandardItemModel();
    QFile tasksFile("tasks.txt");
    tasksFile.open(QIODevice::ReadOnly);
    QTextStream tasksStream(&tasksFile);
    int k = 1;
    while (!tasksStream.atEnd()) {
        QList<QStandardItem *> row;
#define A(d) row << new QStandardItem((d));
        QString line = tasksStream.readLine();
        // %% Check for quotes before mid().
        QStringList t = line.mid(1, line.length() - 2).split("\", \"");
        // %% Won't it crash on empty list?
        A(t[0]);
        A(t[1]);
        A(QString::fromUtf8("%1)  %2").arg(k).arg(line));
#undef A
        tasksModel->appendRow(row);
        tasksModel->setData(tasksModel->index(tasksModel->rowCount() - 1, 2),
                            QPixmap(HEX_NAME(t[0], t[1])),
                            Qt::DecorationRole);
        k++;
    }
    tasksFile.close();
    m_tasks->setModel(tasksModel);
    m_tasks->setModelColumn(2);
    // Calculate maximal width of images.
    int maxWidth = 0;
    for (int i = 0; i < tasksModel->rowCount(); i++) {
        int width = tasksModel->data(tasksModel->index(i, 2), Qt::DecorationRole).value<QPixmap>().width();
        if (width > maxWidth)
            maxWidth = width;
    }
    // Enlarge images to fixed width, add some padding and decoration.
    const int vPadding = 10;
    const int hPadding = 20;
    maxWidth += hPadding;
    for (int i = 0; i < tasksModel->rowCount(); i++) {
        QPixmap m = tasksModel->data(tasksModel->index(i, 2), Qt::DecorationRole).value<QPixmap>();
        QPixmap n(maxWidth, m.height() + vPadding * 2);
        QPainter p(&n);
        p.fillRect(n.rect(), QColor("white"));
        // %% A bit darker color but lighter than "grey"?
        p.setPen(QPen(QColor("lightgrey"), 1));
        p.drawLine(QLine(maxWidth - 1, vPadding, maxWidth - 1, n.height() - vPadding));
        p.drawPixmap(0, vPadding, m);
        tasksModel->setData(tasksModel->index(i, 2), n, Qt::DecorationRole);
    }

    connect(m_tasks, SIGNAL(activated(int)),
            this, SLOT(taskActivated(int)));

    // // ** Use it to enable cycle for task images autogeneration.
    // connect(m_tasks, SIGNAL(currentIndexChanged(int)),
    //         this, SLOT(taskActivated(int)));


    QGridLayout *system = new QGridLayout(this);
    m_layout->addLayout(system);

    // %% Картинки стоит переконвертировать при запуске с     //  % текущего dpi.
    system->addWidget(new QLabel("<img src='static/system.png' />", this), 0, 0, 2, 1);

    pal.setColor(backgroundRole(), "gray");

    m_dotXEdit = new QLineEdit(this);
    m_dotXEdit->setPalette(pal);
    system->addWidget(m_dotXEdit, 0, 1);
    connect(m_dotXEdit, SIGNAL(textChanged(const QString &)),
            this, SLOT(setDotXText(const QString &)));
    // ** It may be better to move focus to next line edit.
    connect(m_dotXEdit, SIGNAL(returnPressed()),
            this, SLOT(start()));

    m_dotYEdit = new QLineEdit(this);
    m_dotYEdit->setPalette(pal);
    system->addWidget(m_dotYEdit, 1, 1);
    connect(m_dotYEdit, SIGNAL(textChanged(const QString &)),
            this, SLOT(setDotYText(const QString &)));
    connect(m_dotYEdit, SIGNAL(returnPressed()),
            this, SLOT(start()));

    m_layout->addWidget(
        createHelpLabel(
            "Точки для поиска решения методом Ньютона HELP",
            // %% Reformat
            "Из этих точек будет начат поиск решений методом Ньютона. Формат описания такой же, как у дополнительных точек исследования."
            ));
    m_mnewton = new QLineEdit(this);
    m_layout->addWidget(m_mnewton);
    connect(m_mnewton, SIGNAL(returnPressed()),
            this, SLOT(start()));

    m_layout->addWidget(
        createHelpLabel(
            "Дополнительные точки исследования HELP",
            // %% Reformat
            "Это поле позволяет вручную ввести список точек для исследования. Они будут добавлены к списку особых точек, найденных программой, и будут исследованы как особые точки, даже если не являются таковыми. Это поле стоит использовать, <b>если программа не может найти особые точки</b>, находит не все особые точки и для управления границами построения общего фазового портрета. Изменение границ общего фазового портрета возможно, потому что все исследуемые точки (плюс окрестность радиуса 1) отображаются на общем фазовом портрете. Каждая точка вводится формате <b>[x=значение, y=значение]</b>. Список разделён запятыми. Например, чтобы получить фазовый портрет ширины и высоты 10 с центром в начале координат (при условии отсутствия точек за пределами этого квадрата), надо ввести: <b>[x=-5, y=-5], [x=5, y=5]</b> или [x=5, y=-5], [x=-5, y=5]."
            ));
    m_specials = new QLineEdit(this);
    m_layout->addWidget(m_specials);
    connect(m_specials, SIGNAL(returnPressed()),
            this, SLOT(start()));

    m_startButton = new QPushButton(QString::fromUtf8("Исследовать и построить!"), this);
    m_layout->addWidget(m_startButton);
    connect(m_startButton, SIGNAL(clicked()),
            this, SLOT(start()));
    m_startButton->setAutoDefault(true);

    m_layout->addStretch();

    QScrollArea *scrollArea = new QScrollArea;
    scrollArea->setWidget(this);
    scrollArea->setWidgetResizable(true);
    scrollArea->show();

    m_tasks->setCurrentIndex(0);
    taskActivated(0);

    m_panel = 0;

    // // ** Cycle to generate images for predefined tasks.
    // // %% Compute upper boundary.
    // for (int i = 0; i < 7; i++) {
    //     m_tasks->setCurrentIndex(i);
    //     taskActivated(i);
    //     start();
    //     QProcess::execute(QString("mv generated/pp1.png ") + HEX_NAME(m_dotFooTexts[0], m_dotFooTexts[1]));
    // }

    // %% Delete
    //start();

}

QLabel *Window::createHelpLabel(const char *normalText, const char *helpText)
{
    QString n = QString::fromUtf8(normalText);
    QString h = n + " <p style='background: lightyellow;'>" + QString::fromUtf8(helpText) + "</p>";
    QString p = "HELP";
    int k = m_helpLabels.count();
    QString sn = QString::fromUtf8("<a href='help%1'>(&#9658; кликните сюда для получения справки)</a>").arg(k);
    QString sh = QString::fromUtf8("<a href='help%1'>(&#9660; кликните сюда для скрытия справки)</a>").arg(k);
    n = n.replace(p, sn);
    h = h.replace(p, sh);
    QLabel *l = new QLabel(n, this);
    // l->setTextInteractionFlags(Qt::LinksAccessibleByKeyboard | l->textInteractionFlags());
    connect(l, SIGNAL(linkActivated(const QString &)),
            this, SLOT(handleLink(const QString &)));
    l->setWordWrap(true);
    l->setMaximumWidth(500);
    m_helpLabels << l;
    m_helpSwap << h;
    return l;
}

void Window::taskActivated(int i)
{
#define S(where, what) (where)->setText(m_tasks->model()->data(m_tasks->model()->index(i, (what))).toString());
    S(m_dotXEdit, 0);
    S(m_dotYEdit, 1);
#undef S
    // start();
}

void Window::handleLink(const QString &link)
{
    QString t = link;
    t.replace("help", "");
    int help_id = t.toInt();
    // ** We use 0 for non-existent links. Do not use it!
    if (help_id > 0) {
        QLabel *l = m_helpLabels[help_id];
        QString t = l->text();
        l->setText(m_helpSwap[help_id]);
        m_helpSwap[help_id] = t;
    }
}

void Window::setDotXText(const QString &text)
{
    setDotFooText(0, text);
}

void Window::setDotYText(const QString &text)
{
    setDotFooText(1, text);
}

// y_or_x: 1 means y, 0 means x.
// %% Maybe enum?
void Window::setDotFooText(int y_or_x, const QString &text)
{
    m_dotFooTexts[y_or_x] = text;
}

void Window::start()
{
    qDebug() << "Window::start: dotX = " << m_dotFooTexts[0] << ", dotY = " << m_dotFooTexts[1];
    m_startButton->setEnabled(false);
    // Сносим всё после первых трёх элементов.
    if (m_panel)
        delete m_panel;

    m_panel = new QWidget(this);
    m_layout->addWidget(m_panel);
    QBoxLayout *layout = new QBoxLayout(QBoxLayout::TopToBottom, this);
    m_panel->setLayout(layout);

    QProcess::execute(ERASEGENERATED);

    // Собираем параметры.
    QStringList arguments;
    arguments << "--very-quiet";
    // Вызываем maxima.
    QProcess maxima;
    // %% Paths.
    maxima.start(MAXIMA, arguments);
    QFile script("solve.mac");
    script.open(QIODevice::ReadOnly);

    // ** Here is a preamble for maxima. Make a separate script if it is too big.
    // %% Use subst in maxima for that.
    maxima.write("e : %e$ pi : %pi$ ln : log$ arctg : atan$\n");

    maxima.write(QString("dotx : %1$ doty : %2$\n").arg(m_dotFooTexts[0]).arg(m_dotFooTexts[1]).toUtf8());
    // %% Should we use variable to track m_specials->text() like m_dotFooTexts?
    maxima.write(QString("specials : [%1]$\n").arg(m_specials->text()).toUtf8());
    maxima.write(QString("mnewtons : [%1]$\n").arg(m_mnewton->text()).toUtf8());
    maxima.write(script.readAll());
    maxima.closeWriteChannel();
    maxima.waitForFinished();
    // Читаем результаты.
    QTextStream outputStream(&maxima);
    QStringList output;
    // %% Clean out previous joiner.
    // maxima режет слишком длинные строки при выводе TeX'а, поэтому
    // мы склеиваем строки, когда первая начинается с долларов, но не
    // заканчивается ими, до тех пор, пока не найдём строку,
    // заканчивающуюся долларами.
    // bool shouldJoin = false;
    while (!outputStream.atEnd()) {
        QString t = outputStream.readLine();
        qDebug() << t;
        if (!t.isEmpty()) {
            // %% Do that in maxima.
            if (t.startsWith("algsys: tried")) {
                qDebug() << "WARNING: algsys error was skipped";
                continue;
            }
            if (t.startsWith("log: encountered log(0)")) {
                qDebug() << "WARNING: log(0) error was skipped";
                continue;
            }
            if (t.startsWith("rat: replaced")) {
                qDebug() << "WARNING: rat replaced something";
                continue;
            }
            // ** Unspecified line skipper.
            // %% Do that after concatenation.
            if (t.indexOf(":") > -1) {
                qDebug() << "WARNING: we skipped a line due to a colon: " << t;
                continue;
            }
            // if (shouldJoin) {
            //     // %% Maybe assert?
            //     if (t.startsWith("$$")) {
            //         qDebug() << "ERROR 1: wrong join";
            //     }
            //     output.last() += t;
            // } else {
            //     output << t;
            // }
            // if (t.startsWith("$$")) {
            //     shouldJoin = true;
            // }
            // if (t.endsWith("$$")) {
            //     shouldJoin = false;
            // }
            if (t.startsWith(" ")) {
                output.last() += t;
            } else {
                output << t;
            }
        }
    }
    // %% Proper names.
    const int lines_per_point = 29;
    const int lines_preamble = 7 + 1;
    for (int i = 0; i < output.length(); i++) {
        qDebug() << QString("maxima %1 (+%2): ").arg(i).arg((i - lines_preamble) % lines_per_point) << output[i];
    }
    qDebug() << "maxima's output length:" << output.length();

    QStringList texStrings;
    QList<QLabel *> texLabels;

    // Показываем систему в виде картинки из теха.
    layout->addWidget(
        createHelpLabel(
            "<b>Исследуемая система</b> HELP",
            "Здесь Вы видите запись системы в виде, близком к рукописному. Проверьте его."));
    QString texX = output[4];
    QString texY = output[5];
    texX.replace("$$", "");
    texY.replace("$$", "");
    QString texSystem("$$\\left\\{\\begin{aligned}"
                      "\\dot{x} &= %1 \\\\"
                      "\\dot{y} &= %2 \\\\"
                      "\\end{aligned}\\right.$$");
    texStrings << texSystem.arg(texX).arg(texY);
    QLabel *systemLabel = new QLabel(
        tr("<img src='generated/pp%1.png' />").arg(texStrings.length()),
        this);
    layout->addWidget(systemLabel);
    texLabels << systemLabel;

    // Делаем табличку для точек: координаты, лямбды, тип, график,
    // устойчивость.
    layout->addWidget(
        createHelpLabel(
            "<b>Особые точки</b> HELP",
            "В таблице ниже приведены особые точки системы и фазовые портреты их "
            "окрестностей (квадрате размера со стороной 2 и центром в исследуемой "
            "особой точке). Фиолетовым цветом на данных фазовых портретах показаны "
            "точки, вектор скорости которых направлен к особой точке, зелёным - от "
            "особой точки. При наведении мыши на фазовый портрет на нём строится "
            "дополнительная фазовая кривая, раскрашенная в два цвета: красная часть "
            "показывает положительное направление движения точки по фазовой кривой из "
            "положения указателя (увеличение времени), синяя - отрицательное "
            "направление (уменьшение времени)."));
    QGridLayout *grid = new QGridLayout(this);
#define GRID_ADD_WIDGET(widget, row, col) grid->addWidget(wrapWithBorder(widget), (row), (col))
    grid->setSpacing(0);
    layout->addLayout(grid);
    {
        int pos = 0;
#define AL(str)                                                         \
        do {                                                            \
            QLabel *l = new QLabel(QString::fromUtf8("<b>"str"</b>"), this); \
            l->setAlignment(Qt::AlignHCenter);                          \
            GRID_ADD_WIDGET(l, 0, pos++);                               \
        } while (0)
        AL("№");
        AL("Координаты");
        AL("Корни<br>характеристического<br>уравнения");
        AL("Точка покоя");
        AL("Фазовый портрет<br>в окрестности точки");
        AL("Устойчивость<br>(неустойчивость)<br>тривиального<br>решения");
#undef AL
    }

    QList<qreal> xList;
    QList<qreal> yList;
    // %% Тут должно быть два цикла, один выводит в тех другой
    //  % расклаыдывает картинки.
    // Разбираем результаты.
    QString dotFooJSTexts[2];
    dotFooJSTexts[0] = output[2];
    dotFooJSTexts[1] = output[3];
    dotFooJSTexts[0].replace("%", "");
    dotFooJSTexts[1].replace("%", "");
    int specialPointsCount = output[7].toInt();
    for (int i = 1; i < specialPointsCount + 1; i++) {
        GRID_ADD_WIDGET(new QLabel(QString("%1").arg(i), this), i, 0);

        // Номер строки начала вывода о текущей особой точке.
        int o = lines_preamble /* строк до первой точки */ + ((i - 1) * lines_per_point) /* строк о предыдущих точках */;
        // Запоминаем значения для построения графика.
        //qDebug() << output[o + 0] << output[o + 1];
#define O(n) (output[o + (n)])
#define S(n) O(n).replace("$$", "")
#define PUT_IMAGE(col) do {                                             \
            QLabel *l =                                                 \
                new QLabel(                                             \
                    tr("<img src='generated/pp%1.png' />").arg(texStrings.length()), \
                    this);                                              \
            texLabels << l;                                             \
            GRID_ADD_WIDGET(l, i, (col));                               \
        } while (0)
        O(0).replace("x = ", "");
        O(1).replace("y = ", "");
        double x = O(0).toDouble();
        double y = O(1).toDouble();
        //qDebug() << O(0) << O(1);

        // Запоминаем значения для компиляции теха.
        S(2);
        O(2).replace("x=", "");
        S(3);
        O(3).replace("y=", "");
        texStrings << tr("$$(%1, %2)$$").arg(O(2)).arg(O(3));
        PUT_IMAGE(1);

        S(19);
        O(19).replace("lambda", "lambda_1");
        S(20);
        O(20).replace("lambda", "lambda_2");
        texStrings << tr("$$%1, %2$$").arg(O(19)).arg(O(20));
        //GRID_ADD_WIDGET(new QLabel(tr("%1, %2").arg(O(19)).arg(O(20)), this), i, 1);
        PUT_IMAGE(2);

        // Строим график.
        // Рисуем фазовый портрет окрестности особой точки.
        xList << x;
        yList << y;
        Canvas *canvas = new Canvas(x, y, dotFooJSTexts, this);
        GRID_ADD_WIDGET(canvas, i, 4);

        // Показываем тип точки.
        QString typeString = O(28);
        typeString.replace("type = ", "");
        bool ok;
        int type = typeString.toInt(&ok);
        if (type < 0) {
            type = 0;
        }
        static const char * const types [] = {
            "Особая точка\nне допускает\nлинеаризацию",
            "Неустойчивый узел",
            "Устойчивый узел",
            "Седло",
            "Центр",
            "Неустойчивый фокус",
            "Устойчивый фокус",
            "Неустойчивый вырожденный узел",
            "Устойчивый вырожденный узел",
            // ** 7а и 8а идут не по порядку, после всех.
            "Неустойчивый дикритический узел",
            "Устойчивый дикритический узел",
        };
        static const char * const stabilities [] = {
            "Особая точка\nне допускает\nлинеаризацию",
            // %% Дефайны лучше заменить переменными.
#define U "Неустойчиво"
            U,
#define AS "Асимптотически устойчиво"
            AS,
            U,
#define L "Устойчиво по Ляпунову"
            L,
            U,
            AS,
            U,
            AS,
            U,
            AS,
#undef L
#undef AS
#undef U
        };
        // Тип точки
        GRID_ADD_WIDGET(new QLabel(QString::fromUtf8(types[type])), i, 3);
        // Устойчивость
        GRID_ADD_WIDGET(new QLabel(QString::fromUtf8(stabilities[type])), i, 5);

        grid->addItem(new QSpacerItem(0, 0), i, 6);

#undef PUT_IMAGE
#undef S
#undef O
    }
    grid->setColumnStretch(6, 1);

    // Вызываем тех.
    for (int i = 0; i < texStrings.count(); i++) {
        texStrings[i].replace("\\%", "");
    }
    QString tex = tr("\\documentclass[a4paper,12pt]{article}\n"
                     "\\usepackage[utf8]{inputenc}\n"
                     "\\usepackage{amsmath}\n"
                     "\\usepackage{amssymb}\n"
                     "\\usepackage{geometry}\n"
                     "\\usepackage{latexsym}\n"
                     "\\usepackage[russian]{babel}\n"
                     "\\pagestyle{empty}\n"
                     "\\begin{document}\n"
                     "%1\n"
                     "\\end{document}\n").arg(texStrings.join("\n\\clearpage\n"));
    QFile texGenerated ("generated/pp.tex");
    texGenerated.open(QIODevice::WriteOnly);
    texGenerated.write(tex.toUtf8());
    texGenerated.close();
    QProcess::execute(COMPILETEX);
    // ** Тут может быть необходимо вызывать обновление картинок, но пока это не нужно.

    // // ** Image saving for task images autogeneration.
    // // %% Check return code.
    // // %% Slashes on Windows?
    // // %% Filename size.
    // QFile(QDir("generated").filePath("pp1.png")).copy(HEX_NAME(m_dotFooTexts[0], m_dotFooTexts[1]));

    if (specialPointsCount == 0) {
        xList << 0;
        yList << 0;
        layout->addWidget(new QLabel(QString::fromUtf8("Особые точки не найдены")));
    }
    // Добавляем полный фазовый портрет
    layout->addWidget(
        createHelpLabel(
            "<b>Общий фазовый портрет</b> HELP",
            "Ниже приведён общий фазовый портрет системы. На нём представлены все "
            "особые точки системы плюс окрестность шириной 1. Все лини чёрные. При "
            "наведении мыши так же проводится дополнительная фазовая кривая."));
    QBoxLayout *hLayout = new QBoxLayout(QBoxLayout::LeftToRight, this);
    layout->addLayout(hLayout);
    hLayout->addWidget(wrapWithBorder(new CanvasFull(xList, yList, dotFooJSTexts, this, this)));
    hLayout->addStretch();
    // %% Кажется на layout растяжку добавлять не надо.
    layout->addStretch();
    m_layout->addStretch();
    m_startButton->setEnabled(true);

}

QWidget *Window::wrapWithBorder(QWidget *widget)
{
    QWidget *w = new QWidget(this);
    w->setStyleSheet(".QWidget { border: 1px solid black }");
    QBoxLayout *bl =  new QBoxLayout(QBoxLayout::TopToBottom, this);
    w->setLayout(bl);
    bl->addWidget(widget);
    return w;
}
