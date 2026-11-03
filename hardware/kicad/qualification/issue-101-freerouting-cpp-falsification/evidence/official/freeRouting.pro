TEMPLATE = app
TARGET = freeRouting
DESTDIR = bin

QT += widgets
CONFIG += c++17 release warn_off exceptions
CONFIG -= app_bundle

CONFIG += object_parallel_to_source
unix:OBJECTS_DIR = o
unix:UI_DIR = o
unix:RCC_DIR = o
unix:MOC_DIR = o

# Only top-level dirs on -I. Leaf package dirs (geometry/planar, …) must not be
# on the include path: on case-insensitive macOS APFS, Limits.h shadows the
# system <limits.h> that libc++ pulls via <climits>, breaking Qt headers.
INCLUDEPATH += src src/jcompat

win32 {
    DEFINES += WINDOWS
}
unix {
    DEFINES += LINUX
}
macx {
    DEFINES -= LINUX
    DEFINES += MACOSX
    QMAKE_APPLE_DEVICE_ARCHS = "arm64 x86_64"
    QMAKE_MACOSX_DEPLOYMENT_TARGET = 12.3
}

SOURCES += src/main.cpp \
           src/jcompat/java_math.cpp \
           src/jcompat/java_util.cpp \
           src/jcompat/java_swing.cpp \
           src/jcompat/java_io.cpp \
           $$files(src/geometry/planar/*.cpp) \
           $$files(src/datastructures/*.cpp) \
           $$files(src/rules/*.cpp) \
           $$files(src/library/*.cpp) \
           $$files(src/board/*.cpp) \
           $$files(src/boardgraphics/*.cpp) \
           $$files(src/designformats/specctra/*.cpp) \
           $$files(src/autoroute/*.cpp) \
           $$files(src/autoroute2/*.cpp) \
           $$files(src/interactive/*.cpp) \
           $$files(src/tests/*.cpp) \
           $$files(src/gui/*.cpp) \
           src/debug/debugMemoryLeak.cpp

DEFINES += FR_HAS_GUI_MAIN

HEADERS += src/jcompat/*.h \
           src/fr_fwd.h \
           src/fr_all.h

RESOURCES += resources.qrc
