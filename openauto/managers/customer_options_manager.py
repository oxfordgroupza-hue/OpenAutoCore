from pathlib import Path
from types import SimpleNamespace
from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.repositories import customer_repository
from openauto.managers import vehicle_manager, animations_manager
from openauto.managers.customer_manager import CustomerManager


class CustomerOptionsManager:
    def __init__(self, parent, customer_id, vehicle_signal, ro_signal):
        self.parent = parent
        self.customer_id = customer_id
        self.vehicle_signal = vehicle_signal
        self.ro_signal = ro_signal
        self.widget_manager = WidgetManager()
        self.vehicle_manager = vehicle_manager.VehicleManager(self)
        self.animations_manager = animations_manager.AnimationsManager

        self.customer_options = None
        self.customer_options_ui = None

        self._setup_ui()

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
            create_ro_customer_button=wrap_button("create_ro_customer_button"),
            edit_customer_button=wrap_button("edit_customer_button"),
            add_customer_vehicle_button=wrap_button("add_customer_vehicle_button"),
            delete_customer_button=wrap_button("delete_customer_button"),
            cancel_customer_options_button=wrap_button("cancel_customer_options_button"),
        )

    def _open_options_form(self):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "CustomerOptions.qml")

        try:
            palette = self._theme_palette()
            self.customer_options, root_obj = self.widget_manager.create_or_restore_qml(
                "customer_options",
                qml_path,
                parent=self.parent,
                context_properties={
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )
            self.customer_options_ui = self._build_qml_proxy(root_obj)
            self.customer_options.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint |
                QtCore.Qt.WindowType.Dialog
            )
            self.customer_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.customer_options.setParent(self.parent)
            self.customer_options.setFocus()
            return self.customer_options_ui
        except Exception:
            return None

### SETS UP customer_options POPUP ###
    def _setup_ui(self):
        form = self._open_options_form()
        if form is None:
            return

        if form.cancel_customer_options_button and form.cancel_customer_options_button.clicked:
            form.cancel_customer_options_button.clicked.connect(
                lambda: self.widget_manager.close_and_delete("customer_options")
            )
        if form.delete_customer_button and form.delete_customer_button.clicked:
            form.delete_customer_button.clicked.connect(self.confirm_delete)
        if form.edit_customer_button and form.edit_customer_button.clicked:
            form.edit_customer_button.clicked.connect(self.open_edit_window)
        if form.add_customer_vehicle_button and form.add_customer_vehicle_button.clicked:
            form.add_customer_vehicle_button.clicked.connect(self.add_vehicle)
        if form.create_ro_customer_button:
            try:
                form.create_ro_customer_button.hide()
            except Exception:
                pass
            if form.create_ro_customer_button.clicked:
                form.create_ro_customer_button.clicked.connect(self.create_ro)

        self.customer_options.show()

    def confirm_delete(self):
        message_box = QtWidgets.QMessageBox(self.parent)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Confirm Delete")
        message_box.setText(
            "This will permanently delete the customer, all vehicles associated, and any open estimates.\n\nAre you sure?"
        )
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = message_box.exec()
        message_confirm = QtWidgets.QMessageBox(self.parent)
        message_confirm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_confirm.setStyleSheet("QLabel { color: black; }")
        message_confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_confirm.setText("Customer Deleted!! This Cannot Be Undone")

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            customer_id = self.customer_id
            customer_repository.CustomerRepository.delete_customer(customer_id)
            message_confirm.exec()
            self.widget_manager.close_and_delete("customer_options")

    ### OPENS customer edit window (QML NewCustomer) ###
    def open_edit_window(self):

        cm = CustomerManager(self.parent)
        form = cm._open_new_customer_qml()

        if form is None:
            return

        self.edit_customer_page = getattr(self.parent, "show_new_customer_page", None)
        self.edit_customer_page_ui = form

        if self.edit_customer_page is not None:
            self.edit_customer_page.setWindowTitle("Edit Customer")

        # For edit: use the green "Save" button as commit, hide the blue "Edit" button
        if form.edit_customer_button:
            try:
                form.edit_customer_button.hide()
            except Exception:
                pass
        if form.save_customer_button:
            try:
                form.save_customer_button.setText("Save Changes")
            except Exception:
                pass

        # Cancel should close the shared "new_customer" window
        if form.cancel_customer_button and form.cancel_customer_button.clicked:
            form.cancel_customer_button.clicked.connect(
                lambda: self.parent.widget_manager.close_and_delete("new_customer")
            )

        # Close customer options while editing
        self.widget_manager.close_and_delete("customer_options")

        # Populate fields and hook change trackers / save handler
        self._populate_customer_fields()

        # Show the shared NewCustomer window configured for edit mode
        try:
            self.edit_customer_page.show()
        except Exception:
            pass

    ### FILLS DATA FROM SELECTED CUSTOMER INTO edit form ###
    def _populate_customer_fields(self):
        data = customer_repository.CustomerRepository.get_customer_info_by_id(self.customer_id)

        self.edit_customer_page_ui.first_name_line.setText(data['first_name'])
        self.edit_customer_page_ui.last_name_line.setText(data['last_name'])
        self.edit_customer_page_ui.address_line.setText(data['address'])
        self.edit_customer_page_ui.city_line.setText(data['city'])
        self.edit_customer_page_ui.state_line.setText(data['state'])
        self.edit_customer_page_ui.zipcode_line.setText(data['zip'])
        self.edit_customer_page_ui.phone_line.setText(data['phone'])
        self.edit_customer_page_ui.alt_line.setText(data['alt_phone'])
        self.edit_customer_page_ui.email_line.setText(data['email'])

        self.changed_values = {}

        self.edit_customer_page_ui.last_name_line.textChanged.connect(
            lambda: self.track_changes("last_name", self.edit_customer_page_ui.last_name_line.text()))
        self.edit_customer_page_ui.first_name_line.textChanged.connect(
            lambda: self.track_changes("first_name", self.edit_customer_page_ui.first_name_line.text()))
        self.edit_customer_page_ui.address_line.textChanged.connect(
            lambda: self.track_changes("address", self.edit_customer_page_ui.address_line.text()))
        self.edit_customer_page_ui.city_line.textChanged.connect(
            lambda: self.track_changes("city", self.edit_customer_page_ui.city_line.text()))
        self.edit_customer_page_ui.state_line.textChanged.connect(
            lambda: self.track_changes("state", self.edit_customer_page_ui.state_line.text()))
        self.edit_customer_page_ui.zipcode_line.textChanged.connect(
            lambda: self.track_changes("zip", self.edit_customer_page_ui.zipcode_line.text()))
        self.edit_customer_page_ui.phone_line.textChanged.connect(
            lambda: self.track_changes("phone", self.edit_customer_page_ui.phone_line.text()))
        self.edit_customer_page_ui.alt_line.textChanged.connect(
            lambda: self.track_changes("alt_phone", self.edit_customer_page_ui.alt_line.text()))
        self.edit_customer_page_ui.email_line.textChanged.connect(
            lambda: self.track_changes("email", self.edit_customer_page_ui.email_line.text()))

        # Commit edits via the green "Save Changes" button
        if self.edit_customer_page_ui.save_customer_button and self.edit_customer_page_ui.save_customer_button.clicked:
            self.edit_customer_page_ui.save_customer_button.clicked.connect(self.make_customer_changes)

### TRACKS EDIT TO CUSTOMER ###
    def track_changes(self, column, value):
        if not hasattr(self, 'changed_values'):
            self.changed_values = {}
        self.changed_values[column] = value.strip()

    ### MAKES CHANGES TO CUSTOMER ###
    def make_customer_changes(self):
        try:
            customer_repository.CustomerRepository.update_customer_by_id(
                self.customer_id, self.changed_values
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.edit_customer_page, "Database Error", str(e))

        # Disconnect save button to avoid duplicate saves
        try:
            self.edit_customer_page_ui.save_customer_button.clicked.disconnect()
        except Exception:
            pass

        # Close the edit window and the options popup
        try:
            self.parent.widget_manager.close_and_delete("new_customer")
        except Exception:
            pass

        self.widget_manager.close_and_delete("customer_options")
        message_box = QtWidgets.QMessageBox(self.edit_customer_page)
        message_box.setWindowTitle("Success")
        message_box.setText("Customer changes have been saved successfully.")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStyleSheet("QLabel { color: black; }")
        message_box.exec()


### PYQTSIGNALS FROM workflow_tables.CUSTOMERTABLE ###
    def add_vehicle(self):
        self.vehicle_signal.emit(int(self.customer_id))
        self.widget_manager.close_and_delete("customer_options")

    def create_ro(self):
        self.ro_signal.emit()
        self.widget_manager.close_and_delete("customer_options")
