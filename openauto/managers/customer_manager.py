from pathlib import Path
from types import SimpleNamespace
from PyQt6 import QtWidgets, QtCore
from openauto.repositories.customer_repository import CustomerRepository
from openauto.utils.validator import Validator

class CustomerManager:
    def __init__(self, main_window):
        self.ui = main_window

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
                "divider": "#C7CDD3",
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
                "divider": "#1F2937",
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
            "divider": "#3C3C3C",
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
        def wrap_line(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                text=lambda: obj.property("text") or "",
                setText=lambda v: obj.setProperty("text", v or ""),
                clear=lambda: obj.setProperty("text", ""),
                textChanged=getattr(obj, "textChanged", None),
            )

        def wrap_button(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                clicked=getattr(obj, "clicked", None),
                setVisible=lambda v: obj.setProperty("visible", bool(v)),
                hide=lambda: obj.setProperty("visible", False),
                show=lambda: obj.setProperty("visible", True),
            )

        return SimpleNamespace(
            first_name_line=wrap_line("first_name_line"),
            last_name_line=wrap_line("last_name_line"),
            address_line=wrap_line("address_line"),
            city_line=wrap_line("city_line"),
            state_line=wrap_line("state_line"),
            zipcode_line=wrap_line("zipcode_line"),
            phone_line=wrap_line("phone_line"),
            alt_line=wrap_line("alt_line"),
            email_line=wrap_line("email_line"),
            cancel_customer_button=wrap_button("cancel_customer_button"),
            edit_customer_button=wrap_button("edit_customer_button"),
            save_customer_button=wrap_button("save_customer_button"),
        )

    def _open_new_customer_qml(self):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "NewCustomer.qml")

        try:
            palette = self._theme_palette()
            self.ui.show_new_customer_page, root_obj = self.ui.widget_manager.create_or_restore_qml(
                "new_customer",
                qml_path,
                parent=self.ui,
                context_properties={
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )
            self.ui.show_new_customer_page_ui = self._build_qml_proxy(root_obj)

            self.ui.show_new_customer_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
            self.ui.show_new_customer_page.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
            )
            self.ui.show_new_customer_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.ui.show_new_customer_page.setFixedSize(606, 560)
            self.ui.show_new_customer_page.setWindowTitle("New Customer")
            self.ui.show_new_customer_page.setFocus()

            return self.ui.show_new_customer_page_ui
        except Exception:
            self._show_message("Unable to load customer form.")
            return None

    ### OPENS NewCustomer dialog (QML) ###
    def open_new_customer(self, on_saved=None):
        form = self._open_new_customer_qml()
        if form is None:
            return

        if form.cancel_customer_button and form.cancel_customer_button.clicked:
            form.cancel_customer_button.clicked.connect(
                lambda: self.ui.widget_manager.close_and_delete("new_customer")
            )
        if form.edit_customer_button:
            try:
                form.edit_customer_button.hide()
            except Exception:
                pass
        if form.save_customer_button and form.save_customer_button.clicked:
            handler = on_saved or self.save_customer
            form.save_customer_button.clicked.connect(handler)

        self.ui.show_new_customer_page.show()

### SAVES NEW CUSTOMER TO DB ###
    def save_customer(self):
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
            Validator.show_validation_error(self.ui.message, "Please provide at least a name and phone number.")
            return
        CustomerRepository.insert_customer(customer_data)
        self.ui.widget_manager.close_and_delete("new_customer")
        QtCore.QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.information(self.ui, "Customer Added",
                        "Customer has been added."))

    def customer_search_filter(self, text):
        for row in range(self.ui.customer_table.rowCount()):
            match = any(
                text.lower() in (self.ui.customer_table.item(row, col).text().lower() if self.ui.customer_table.item(row, col) else "")
                for col in range(self.ui.customer_table.columnCount())
            )
            self.ui.customer_table.setRowHidden(row, not match)


    def _show_message(self, text):
        self.ui.message.setText(text)
        self.ui.message.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.message.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ui.message.show()
