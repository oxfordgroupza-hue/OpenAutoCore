from pathlib import Path
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton
from PyQt6.QtQuickWidgets import QQuickWidget
from openauto.subclassed_widgets import event_handlers

### CLASS TO CALL MAIN LEFT MENU ###

class ControlMenu(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("cmenu_frame")
        self.setMouseTracking(True)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(size_policy)
        self.collapsed_width = 60
        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(60)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.frame_filter = event_handlers.CMenuHandler(self)
        self.installEventFilter(self.frame_filter)

        # Optional QML skin for the control menu; by default we
        # keep the original QWidget-based menu unless the host
        # window explicitly opts in via `use_qml_cmenu = True`.
        self._qml = None
        host = parent.window() or parent
        if getattr(host, "use_qml_cmenu", False):
            self._init_qml_skin(host)

    def _init_qml_skin(self, host):
        base_dir = Path(__file__).resolve().parents[2]
        qml_path = str(base_dir / "qml" / "ControlMenu.qml")

        try:
            self._qml = QQuickWidget(self)
            self._qml.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)

            # Expose the main window to QML if needed later
            ctx = self._qml.rootContext()
            ctx.setContextProperty("mainWindow", host)

            url = QtCore.QUrl.fromLocalFile(qml_path)
            self._qml.setSource(url)

            if self._qml.status() == QQuickWidget.Status.Error:
                # If QML fails, fall back silently to the original QWidget menu.
                self._qml.deleteLater()
                self._qml = None
                return

            # Hide the original QPushButtons visually but keep them for signal wiring / CMenuHandler.
            for name in [
                "repair_orders_button", "customers_button", "vehicles_button",
                "messaging_button", "scheduling_button", "analytics_button",
                "settings_button", "quit_button",
            ]:
                btn = getattr(host, name, None)
                if btn is not None:
                    btn.hide()

            # Wire QML button clicks to the existing QWidget button slots by triggering their .click()
            root_obj = self._qml.rootObject()
            if root_obj is not None:
                for name in [
                    "repair_orders_button", "customers_button", "vehicles_button",
                    "messaging_button", "scheduling_button", "analytics_button",
                    "settings_button", "quit_button",
                ]:
                    qml_btn = root_obj.findChild(QtCore.QObject, name)
                    qt_btn = getattr(host, name, None)
                    if qml_btn is not None and qt_btn is not None:
                        clicked = getattr(qml_btn, "clicked", None)
                        if clicked is not None:
                            try:
                                clicked.connect(qt_btn.click)
                            except Exception:
                                pass

            # Keep the QML content on top and sized to the frame.
            self._qml.setGeometry(self.rect())
            self._qml.raise_()
        except Exception:
            self._qml = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._qml is not None:
            self._qml.setGeometry(self.rect())
