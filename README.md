# PhaPl

PhaPl is a program to plot and research phase planes. Description and the program in English live in branch 'en'.

## Описание

Phapl - умная программа для построения фазовых портретов, которая сама находит особые точки и строит фазовые траектории по связности.

Поддерживаются Windows, Linux и теоретически Mac OS X. Примечания:
- Windows: есть скомпилированная версия (см. ниже или в release).
- Mac OS X: не тестировался, готовых бинарников нет.

В своей основе phapl использует свободное ПО: Maxima для нахождения особых точек, Qt4 для построения графического интерфейса, LaTeX для рендеринга формул. Программа реализует виджет для рендеринга частей фазовых портретов и обеспечивает работу всех компонентов вместе.

Программа использует текущий каталог для хранения временных файлов. Поэтому её нужно запускать из её папки.

> Внимание! Если Вы используете cmd для запуска программы, перейдите в каталог с ней.

## Windows

Есть бинарный пакет (~185mb, ~600мб в распакованном виде):
https://github.com/AlekseyCherepanov/phapl/releases/download/v1.1/phapl.ru.2017-02-13.7z

Программу можно распаковать на съёмный носитель.

Пакет включает несвободные задачи, взятые из следующего учебника:
Асташова И.В., Никишкин В.А. Практикум по курсу «Дифференциальные уравнения». Учебное пособие. Изд. 3-е, исправленное. М.: Изд. центр ЕАОИ, 2010. 94 с., ил.

Асташова И.В. предоставила неявное разрешение на их распространение в неизменном виде для использования в МЭСИ и МГУ.

Так же этот пакет включает все зависимости, требуемые для работы программы: MiKTeX в неизменном виде; части Qt4 (QtCore, QtGui, QtScript) в неизменном виде; а так же Maxima со следующим исправлением: убрано начало глобального пути в вызываемом батнике, сделав его относительным (чтобы "оторвать" Maxima от папки после установки).

Сборка из исходников происходит примерно так же, как на Linux.

## Linux

Зависимости:
- Maxima
- Qt4 (включая QtCore, QtGui и QtScript)
- LaTeX
- если собирать из исходников, то ещё понадобится следующее ПО:
  - Qt4 SDK
  - gcc и g++ (mingw на Windows)

Команды для сборки из исходников и запуска, в шелле в папке проекта:
```shell
qmake
make
./phapl
```

## Известные проблемы

- Программа не всегда находит особые точки. Это связано с решением системы уравнений. Чтобы улучшить ситуацию, отдельно проверяются все целочисленные точки от -10 до +10. Но это не решает проблему для исследователей.
- Ввод от пользователя передаётся в Maxima напрямую, что позволяет пользователю выполнять код Maxima. Это уязвимость. При текущем способе использования не серьёзная, но её надо учитывать при желании сделать, скажем, web-интерфейс для программы.
- Программа требует много места.
- Нет удобного способа изменить масштаб. Хотя его можно менять, добавляя дополнительные точки для исследования.
- Добавленные вручную точки для исследования всегда называются особыми, хотя могут таковыми не являться.
- Сборка из исходников не работает на системах, где по умолчанию включены дополнительные предупреждения компилятора C++.
- Собрать всё вместе в бинарный пакет - трудоёмкая задача.

## Реализация на Python

В папке есть скрипт phapl.py на Python 2 с PyQt4, который реализует ту же функциональность почти один в один. Все технологии те же. Единственное отличие - другой механизм для интерпретации кода для вычисления векторов в точках. Есть медленный вариант с генерацией кода на Python (возможно, с PyPy он был бы хорош, но такой эксперимент не ставился). По умолчанию включён значительно более быстрый вариант с генерацией кода на C++ и подключением этого кода в программу при помощи SciPy.Weave.

Большинство проблем из описанных выше эта версия не устраняет.

## Планы

Планируется переделать программу с использованием других технологий, чтобы решить описанные проблемы.

## Библиографическая ссылка (ГОСТ)

*Черепанов А. А.* Программный комплекс PhaPl для автоматического построения и исследования фазовых портретов на плоскости // Открытое образование. 2017. №3. - С. 66-72

Старая:

*Черепанов А.А.* Программа для построения и исследования фазовых портретов на основе программных компонентов с открытым исходным кодом // Теоретические и прикладные аспекты математики, информатики и образования: Материалы Международной научной конференции, 16-21 ноября 2014 г., г. Архангельск. - С. 594-598.
