from modules.connection_manager import ConnectionManager
from PyQt6.QtCore import QFile, QPoint, Qt, QTextStream, QIODeviceBase, QIODevice
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication, QWidget


class BaseWindow(QWidget):
    def __init__(self, parent=None, app=None, version=None):
        super().__init__()
        self.parent = parent

        if parent is None:
            self.app = app
            self.version = version

            # Setup pool manager
            self.cm = ConnectionManager(version=version)
            self.cm.setup()
            self.manager = self.cm.manager

            # Setup font
            QFontDatabase.addApplicationFont(
                ":/resources/fonts/OpenSans-SemiBold.ttf")
            self.font_10 = QFont("Open Sans SemiBold", 10)
            self.font_10.setHintingPreference(
                QFont.HintingPreference.PreferNoHinting)
            self.font_8 = QFont("Open Sans SemiBold", 8)
            self.font_8.setHintingPreference(
                QFont.HintingPreference.PreferNoHinting)
            self.app.setFont(self.font_10)

            # Setup style
            file = QFile(":/resources/styles/global.qss")
            file.open(QIODevice.OpenModeFlag.ReadOnly)
            self.style_sheet = QTextStream(file).readAll()
            self.app.setStyleSheet(self.style_sheet)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.pos = self.pos()
        self.pressing = False

        self.destroyed.connect(lambda: self._destroyed())

    def mousePressEvent(self, event):
        self.pos = event.pos()
        self.pressing = True
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.pressing:
            delta = QPoint(event.pos() - self.pos)
            self.moveWindow(delta, True)
            self.pos = event.pos()

    def moveWindow(self, delta, chain=False):
        self.move(self.x() + delta.x(), self.y() + delta.y())

        if chain and self.parent is not None:
            for window in self.parent.windows:
                if window is not self:
                    window.moveWindow(delta)

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def showEvent(self, event):
        parent = self.parent

        if parent is not None:
            if self not in parent.windows:
                parent.windows.append(self)
                parent.show_signal.connect(self.show)
                parent.close_signal.connect(self.hide)

            if self.parent.isVisible():
                x = parent.x() + (parent.width() - self.width()) * 0.5
                y = parent.y() + (parent.height() - self.height()) * 0.5
            else:
                size = parent.app.screens()[0].size()
                x = (size.width() - self.width()) * 0.5
                y = (size.height() - self.height()) * 0.5

            self.move(x, y)
            event.accept()

    def _destroyed(self):
        if self.parent is not None:
            if (self in self.parent.windows):
                self.parent.windows.remove(self)
