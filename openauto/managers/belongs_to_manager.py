from pathlib import Path
from types import SimpleNamespace
from PyQt6 import QtCore, QtWidgets
from openauto.utils.validator import Validator
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories import vehicle_repository
from openauto.managers.customer_manager import CustomerManager

class BelongsToManager:
    def __init__(self, main_window, vehicle_id=None):
        self.ui = main_window
        self.vehicle_id = vehicle_id

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
                "inputText": "#1E1E1E",
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
                "inputText": "#E2E8F0",
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
            "inputText": "#FFFFFF",
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
            )

        def wrap_line(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                text=lambda: obj.property("text") or "",
                setText=lambda v: obj.setProperty("text", v or ""),
                setPlaceholderText=lambda v: obj.setProperty("placeholderText", v or ""),
                textChanged=getattr(obj, "textChanged", None),
            )

        def wrap_combo(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None

            items = []

            def clear():
                items.clear()
                obj.setProperty("model", [])

            def addItem(text, data=None):
                items.append((text, data))
                obj.setProperty("model", [t for t, _ in items])

            def currentData():
                index = obj.property("currentIndex")
                try:
                    index = int(index)
                except Exception:
                    index = -1
                if index is None or index < 0 or index >= len(items):
                    return None
                return items[index][1]

            def currentText():
                return obj.property("currentText") or ""

            def count():
                return len(items)

            def itemText(idx):
                return items[idx][0]

            def itemData(idx):
                return items[idx][1]

            return SimpleNamespace(
                _obj=obj,
                clear=clear,
                addItem=addItem,
                currentData=currentData,
                currentText=currentText,
                count=count,
                itemText=itemText,
                itemData=itemData,
            )

        return SimpleNamespace(
            customer_search_edit=wrap_line("customer_search_edit"),
            customer_name_box=wrap_combo("customer_name_box"),
            belongs_to_label=root_obj.findChild(QtCore.QObject, "belongs_to_label"),
            confirm_customer_search_button=wrap_button("confirm_customer_search_button"),
            cancel_customer_search_button=wrap_button("cancel_customer_search_button"),
            add_customer_button=wrap_button("add_customer_button"),
        )

    def _open_customer_search(self, key="belongs_to"):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "BelongsTo.qml")

        palette = self._theme_palette()
        window, root_obj = self.ui.widget_manager.create_or_restore_qml(
            key,
            qml_path,
            parent=self.ui,
            context_properties={
                "themePalette": palette,
                "themeName": palette.get("name", "dark"),
            },
        )
        self.ui.belongs_to_window = window
        self.ui.belongs_to_window_ui = self._build_qml_proxy(root_obj)

        window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )
        window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        window.setParent(self.ui)
        window.setFixedSize(636, 256)
        window.setFocus()
        return self.ui.belongs_to_window_ui

    ### OPENS customer_search QML WINDOW ###
    def belongs_to(self):
        form = self.ui.vehicle_window_ui

        if not Validator.vehicle_fields_filled([
            form.vin_line.text(),
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text()
        ]):
            Validator.show_validation_error(self.ui.message, "Please decode VIN or enter Year, Make, and Model")
            return

        self._open_customer_search("belongs_to")

        self.ui.belongs_to_window_ui.cancel_customer_search_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("belongs_to"))

        if self.ui.belongs_to_window_ui.customer_search_edit and self.ui.belongs_to_window_ui.customer_search_edit.textChanged:
            self.ui.belongs_to_window_ui.customer_search_edit.textChanged.connect(self.customer_combo_filter)
        self.ui.vehicle_window.hide()
        self.name_box_items()
        self.ui.belongs_to_window.show()

        self.ui.belongs_to_window_ui.confirm_customer_search_button.clicked.connect(self.new_vehicle_customer)
        self.ui.belongs_to_window_ui.add_customer_button.clicked.connect(self.join_vehicle_customer)


### ADDS VEHICLE TO CUSTOMER ALREADY IN THE SYSTEM ###
    def new_vehicle_customer(self):
        customer_id = self.ui.belongs_to_window_ui.customer_name_box.currentData()
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "Please select a customer")
            return

        form = self.ui.vehicle_window_ui
        vin_raw = (form.vin_line.text() or "").strip().upper()
        vin = vin_raw if vin_raw else None

        vehicle_data = [
            vin,
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id,
        ]
        # Optional plate and state
        try:
            plate = (form.plate_line.text() or "").strip().upper()
        except Exception:
            plate = ""
        try:
            state = (form.plate_state_box.currentText() or "").strip().upper()
        except Exception:
            state = ""

        vehicle_data.append(plate)
        vehicle_data.append(state)

        VehicleRepository.insert_vehicle(vehicle_data)
        self._show_message("Vehicle Added")
        self._close_windows(["vehicle_window", "belongs_to"])


    ### LOADS CUSTOMER SEARCH WINDOW FOR ADDING NEW CUSTOMER WITH VEHICLE ###
    def join_vehicle_customer(self):
        # Use shared NewCustomer dialog; on save attach the new vehicle
        cm = CustomerManager(self.ui)
        cm.open_new_customer(on_saved=self.save_cust_vehc_join)
        self.ui.belongs_to_window.hide()

### CREATES NEW CUSTOMER AND ADDS NEW VEHICLE ASSOCIATED WITH THEM ###
    def save_cust_vehc_join(self):
        form = self.ui.show_new_customer_page_ui
        customer_data = [
            form.last_name_line.text(),
            form.first_name_line.text(),
            form.phone_line.text(),
            form.address_line.text(),
            form.city_line.text(),
            form.state_line.text(),
            form.zipcode_line.text(),
            form.alt_line.text(),
            form.email_line.text()
        ]

        if not Validator.fields_filled(customer_data[:3]):
            Validator.show_validation_error(self.ui.message, "Please enter at least name and phone number.")
            return

        CustomerRepository.insert_customer(customer_data)
        customer_id = CustomerRepository.get_customer_id_by_details(customer_data)

        if not customer_id:
            Validator.show_validation_error(self.ui.message, "Unable to find newly created customer.")
            return

        form = self.ui.vehicle_window_ui
        vin_raw = (form.vin_line.text() or "").strip().upper()
        vin = vin_raw if vin_raw else None

        vehicle_data = [
            vin,
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id
        ]
        VehicleRepository.insert_vehicle(vehicle_data)
        self._show_message("New Vehicle and Customer Added")
        self._close_windows(["vehicle_window", "belongs_to", "new_customer"])

### LOADS EXISTING CUSTOMERS INTO belongs_to.py ###
    def name_box_items(self):
        results = CustomerRepository.get_all_customer_names()
        combo = self.ui.belongs_to_window_ui.customer_name_box
        combo.clear()
        for row in results:
            last_name, first_name, phone, cust_id = row
            combo.addItem(f"{last_name} - {first_name} - {cust_id}", cust_id)

    def _show_message(self, text):
        self.ui.message.setParent(self.ui)
        self.ui.message.setText(text)
        self.ui.message.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.message.setWindowFlags(QtCore.Qt.WindowType.Dialog)
        self.ui.message.show()

    def _close_windows(self, window_keys):
        for key in window_keys:
            self.ui.widget_manager.close_and_delete(key)


### CHANGES VEHICLE OWNER TO A DIFFERENT EXISTING CUSTOMER ###
    def belongs_to_cust_change(self):
        self._open_customer_search("belongs_to")

        self.ui.belongs_to_window_ui.cancel_customer_search_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("belongs_to"))

        if self.ui.belongs_to_window_ui.customer_search_edit and self.ui.belongs_to_window_ui.customer_search_edit.textChanged:
            self.ui.belongs_to_window_ui.customer_search_edit.textChanged.connect(self.customer_combo_filter)

        self.name_box_items()
        self.ui.belongs_to_window_ui.confirm_customer_search_button.clicked.connect(self.change_vehicle_owner)
        self.ui.belongs_to_window_ui.add_customer_button.clicked.connect(self.new_vehicle_owner)
        self.ui.belongs_to_window.show()

    def change_vehicle_owner(self):
        customer_id = self.ui.belongs_to_window_ui.customer_name_box.currentData()
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "Please select a customer")
            return

        vehicle_repository.VehicleRepository.change_vehicle_owner(vin=self.vehicle_id[0],
                                                                vehicle_id=self.vehicle_id[1],
                                                                customer_id=customer_id)

        self.ui.widget_manager.close_and_delete("belongs_to")
        message_box = QtWidgets.QMessageBox()
        message_box.setText("Vehicle Owner Changed Successfully")
        message_box.setWindowTitle("Success")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        message_box.exec()


    def customer_combo_filter(self, text=None):
        # Support both QWidget (text passed from signal) and QML (no arg)
        if text is None:
            try:
                text = self.ui.belongs_to_window_ui.customer_search_edit.text()
            except Exception:
                text = ""

        original_items = getattr(self, "_original_customer_items", None)

        # First time run: store all items
        if original_items is None:
            self._original_customer_items = [
                (self.ui.belongs_to_window_ui.customer_name_box.itemText(i),
                 self.ui.belongs_to_window_ui.customer_name_box.itemData(i))
                for i in range(self.ui.belongs_to_window_ui.customer_name_box.count())
            ]
            original_items = self._original_customer_items

        text = text.lower()

        combo = self.ui.belongs_to_window_ui.customer_name_box
        combo.clear()

        for display_text, user_data in original_items:
            if text in display_text.lower():
                combo.addItem(display_text, user_data)

    def new_vehicle_owner(self):
        # Use shared NewCustomer dialog; on save change owner to new customer
        cm = CustomerManager(self.ui)
        cm.open_new_customer(on_saved=self.new_cust_old_vehc)
        self.ui.belongs_to_window.hide()


    def new_cust_old_vehc(self):
        form = self.ui.show_new_customer_page_ui
        customer_data = [
            form.last_name_line.text(),
            form.first_name_line.text(),
            form.phone_line.text(),
            form.address_line.text(),
            form.city_line.text(),
            form.state_line.text(),
            form.zipcode_line.text(),
            form.alt_line.text(),
            form.email_line.text()
        ]


        CustomerRepository.insert_customer(customer_data)
        customer_id = CustomerRepository.get_customer_id_by_details(customer_data)
        vehicle_repository.VehicleRepository.change_vehicle_owner(self.vehicle_id, customer_id)
        message_box = QtWidgets.QMessageBox()
        message_box.setText("Vehicle Owner Changed Successfully")
        message_box.setWindowTitle("Success")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        message_box.exec()
        self._close_windows(["vehicle_window", "belongs_to", "new_customer"])
