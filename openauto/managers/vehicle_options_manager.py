from pathlib import Path
from types import SimpleNamespace
from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.managers import animations_manager, customer_manager


class VehicleOptionsManager:
    def __init__(self, parent, vehicle_id, new_ro_request):
        self.parent = parent
        self.vehicle_id = vehicle_id
        self.new_ro_request = new_ro_request
        self.widget_manager = WidgetManager()
        self.customer_manager = customer_manager.CustomerManager(self)
        self.animations_manager = animations_manager.AnimationsManager

        self.vehicle_options = None
        self.vehicle_options_ui = None
        self._setup_ui()

    # --- palette helper shared with QML ---
    def _theme_palette(self):
        theme = getattr(self.parent, "current_theme", "dark")
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
            create_ro_vehicle_button=wrap_button("create_ro_vehicle_button"),
            change_owner_vehicle_button=wrap_button("change_owner_vehicle_button"),
            delete_vehicle_button=wrap_button("delete_vehicle_button"),
            cancel_vehicle_options_button=wrap_button("cancel_vehicle_options_button"),
        )

    def _open_options_form(self):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "VehicleOptions.qml")

        try:
            palette = self._theme_palette()
            self.vehicle_options, root_obj = self.widget_manager.create_or_restore_qml(
                "vehicle_options",
                qml_path,
                parent=self.parent,
                context_properties={
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )
            self.vehicle_options_ui = self._build_qml_proxy(root_obj)
            self.vehicle_options.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint |
                QtCore.Qt.WindowType.Dialog
            )
            self.vehicle_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.vehicle_options.setParent(self.parent)
            self.vehicle_options.setFocus()
            return self.vehicle_options_ui
        except Exception:
            return None

    def _setup_ui(self):
        form = self._open_options_form()
        if form is None:
            return

        if form.cancel_vehicle_options_button and form.cancel_vehicle_options_button.clicked:
            form.cancel_vehicle_options_button.clicked.connect(
                lambda: self.widget_manager.close_and_delete("vehicle_options")
            )
        if form.change_owner_vehicle_button and form.change_owner_vehicle_button.clicked:
            form.change_owner_vehicle_button.clicked.connect(self.change_owner)
        if form.create_ro_vehicle_button and form.create_ro_vehicle_button.clicked:
            form.create_ro_vehicle_button.setVisible(False)
            form.create_ro_vehicle_button.clicked.connect(self.create_ro)
        if form.delete_vehicle_button and form.delete_vehicle_button.clicked:
            form.delete_vehicle_button.clicked.connect(self.delete_vehicle)

        self.vehicle_options.show()


    def change_owner(self):
        from openauto.managers import belongs_to_manager

        temp_belongs_to_manager = belongs_to_manager.BelongsToManager(self.parent, vehicle_id=self.vehicle_id)
        temp_belongs_to_manager.belongs_to_cust_change()
        self.widget_manager.close_and_delete("vehicle_options")


    def create_ro(self):
        self.new_ro_request.emit()
        self.widget_manager.close_and_delete("vehicle_options")

    def delete_vehicle(self):
        confirmation = QtWidgets.QMessageBox(self.vehicle_options)
        confirmation.setWindowTitle("Confirm Delete")
        confirmation.setText("Are you sure you want to delete this vehicle?")
        confirmation.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        confirmation.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = confirmation.exec()

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            from openauto.repositories.vehicle_repository import VehicleRepository
            VehicleRepository.delete_vehicle(vin = self.vehicle_id[0], vehicle_id=self.vehicle_id[1])
            self.widget_manager.close_and_delete("vehicle_options")
