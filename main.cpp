/* LICENSE
 * Copyright © 2012 Aleksey Cherepanov <aleksey.4erepanov@gmail.com>.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 * END OF LICENSE
 */

#include <QApplication>

#include "window.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    Window window;
    window.show();
    return app.exec();
}
