from pathlib import Path
from types import SimpleNamespace
from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.subclassed_widgets.models.ro_tree_model import ROTreeModel
from openauto.repositories import repair_orders_repository
from openauto.managers import ro_status_manager


class EstimateOptionsManager:
    def __init__(self, parent, estimate_id):
        self.ui = parent
        self.estimate_id = estimate_id
        self.widget_manager = WidgetManager()

        self.estimate_options = None
        self.estimate_options_ui = None

        self._setup_ui()

    def _theme_palette(self):
        theme = getattr(self.ui, "current_theme", "dark")
        if theme == "light":
            return {
                "name": "light",
                "bg": "#F5F7FA",
                "surface": "#FFFFFF",
                "text": "#1E1E1E",
                "text2": "#5C5C5C",
                "accent": "#314455",
                "accentHover": "#4F6D7A",
                "accentPress": "#22313F",
                "fieldBg": "#FFFFFF",
                "fieldBorder": "#C7CDD3",
                "success": "#4A6260",
                "successHover": "#759093",
                "successPress": "#314455",
                "danger": "#C96567",
                "dangerHover": "#9E5A63",
                "dangerPress": "#7a0f31",
                "buttonText": "#FFFFFF",
            }
        if theme == "slate":
            return {
                "name": "slate",
                "bg": "#0F172A",
                "surface": "#111827",
                "text": "#E2E8F0",
                "text2": "#94A3B8",
                "accent": "#38BDF8",
                "accentHover": "#0EA5E9",
                "accentPress": "#0284C7",
                "fieldBg": "#111827",
                "fieldBorder": "#1F2937",
                "success": "#38BDF8",
                "successHover": "#0EA5E9",
                "successPress": "#0284C7",
                "danger": "#EF4444",
                "dangerHover": "#F87171",
                "dangerPress": "#B91C1C",
                "buttonText": "#0B1220",
            }
        return {
            "name": "dark",
            "bg": "#1E1E1E",
            "surface": "#2B2B2B",
            "text": "#FFFFFF",
            "text2": "#FFFFFF",
            "accent": "#4A90E2",
            "accentHover": "#7BAFD4",
            "accentPress": "#2C5FA5",
            "fieldBg": "#2B2B2B",
            "fieldBorder": "#3C3C3C",
            "success": "#76ABAE",
            "successHover": "#828786",
            "successPress": "#5b7f83",
            "danger": "#A0153E",
            "dangerHover": "#C49497",
            "dangerPress": "#7a0f31",
            "buttonText": "#FFFFFF",
        }

    def _build_qml_proxy(self, root_obj):
        def wrap_button(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                clicked=getattr(obj, "clicked", None),
                setText=lambda v: obj.setProperty("text", v or ""),
                setVisible=lambda v: obj.setProperty("visible", bool(v)),
                hide=lambda: obj.setProperty("visible", False),
                show=lambda: obj.setProperty("visible", True),
            )

        return SimpleNamespace(
            open_ro_button=wrap_button("open_ro_button"),
            change_ro_status_button=wrap_button("change_ro_status_button"),
            duplicate_ro_button=wrap_button("duplicate_ro_button"),
            delete_ro_button=wrap_button("delete_ro_button"),
            cancel_ro_options_button=wrap_button("cancel_ro_options_button"),
        )

    def _open_options_form(self):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "EstimateOptions.qml")

        try:
            palette = self._theme_palette()
            self.estimate_options, root_obj = self.widget_manager.create_or_restore_qml(
                "estimate_options",
                qml_path,
                parent=self.ui,
                context_properties={
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )
            self.estimate_options_ui = self._build_qml_proxy(root_obj)
            self.estimate_options.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint |
                QtCore.Qt.WindowType.Dialog
            )
            self.estimate_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.estimate_options.setParent(self.ui)
            self.estimate_options.setFocus()
            return self.estimate_options_ui
        except Exception:
            return None
    def _setup_ui(self):
        form = self._open_options_form()
        if form is None:
            return

        if form.cancel_ro_options_button and form.cancel_ro_options_button.clicked:
            form.cancel_ro_options_button.clicked.connect(
                lambda: self.widget_manager.close_and_delete("estimate_options")
            )
        if form.delete_ro_button and form.delete_ro_button.clicked:
            form.delete_ro_button.clicked.connect(self.confirm_delete)
        if form.open_ro_button and form.open_ro_button.clicked:
            form.open_ro_button.clicked.connect(self._open_ro_page)
        if form.change_ro_status_button:
            try:
                form.change_ro_status_button.hide()
            except Exception:
                pass
            if form.change_ro_status_button.clicked:
                form.change_ro_status_button.clicked.connect(self.open_ro_status)

        self.estimate_options.show()

    def confirm_delete(self):
        message_box = QtWidgets.QMessageBox(self.ui)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Confirm Delete")
        message_box.setText(
            "This will permanently delete the estimate.\n\nAre you sure?"
        )
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = message_box.exec()
        message_confirm = QtWidgets.QMessageBox(self.ui)
        message_confirm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        # message_confirm.setStyleSheet("QLabel { color: black; }")
        message_confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_confirm.setText("Estimate Deleted!! This Cannot Be Undone")

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            ro_id = self.estimate_id
            from openauto.repositories.repair_orders_repository import RepairOrdersRepository
            RepairOrdersRepository.delete_repair_order_cascade(ro_id)
            message_confirm.exec()
            self.widget_manager.close_and_delete("estimate_options")


    def _open_ro_page(self):
        selected_estimate_row = self.ui.estimates_table.currentRow()
        model: ROTreeModel = self.ui.ro_items_table.model()
        model.clear()
        ro_id = self.estimate_id
        self.ui.ro_hub_manager.load_ro_into_hub(ro_id)
        self.widget_manager.close_and_delete("estimate_options")
        self.ui.animations_manager.ro_hub_page_show()

    def open_ro_status(self, checked=False):
        self.widget_manager.close_and_delete("estimate_options")
        ro_status_manager.ROStatusManager(self.ui)
