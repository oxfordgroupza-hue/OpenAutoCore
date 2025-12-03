from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from pyvin import VIN
from openauto.utils.validator import Validator
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.managers.belongs_to_manager import BelongsToManager
from openauto.managers.parts_tree.go_sidecar_manager import GoSidecarManager
from types import SimpleNamespace


STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def _ptcli_available() -> bool:
    try:
        ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
        return ptcli_path.is_file()
    except Exception:
        return False


class VehicleManager:
    def __init__(self, main_window):
        self.ui = main_window
        self.belongs_to_manager = BelongsToManager(main_window)
        self._plate_sidecar = None
        self._vehicle_root = None

    # --- helpers ---
    def _form(self):
        form = getattr(self.ui, "vehicle_window_ui", None)
        if form is None:
            self._show_message("Vehicle form is not available.")
        return form

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
                cursorPosition=lambda: obj.property("cursorPosition") or 0,
                setCursorPosition=lambda pos: obj.setProperty("cursorPosition", pos),
                setVisible=lambda v: obj.setProperty("visible", bool(v)),
                hide=lambda: obj.setProperty("visible", False),
                show=lambda: obj.setProperty("visible", True),
            )

        def wrap_combo(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                addItems=lambda items: obj.setProperty("model", items),
                currentText=lambda: obj.property("currentText") or "",
                setMinimumWidth=lambda _w: None,
                hide=lambda: obj.setProperty("visible", False),
                show=lambda: obj.setProperty("visible", True),
                setObjectName=lambda val: obj.setObjectName(val),
            )

        def wrap_button(name):
            obj = root_obj.findChild(QtCore.QObject, name)
            if obj is None:
                return None
            return SimpleNamespace(
                _obj=obj,
                clicked=getattr(obj, "clicked", None),
                setText=lambda v: obj.setProperty("text", v or ""),
                setMinimumWidth=lambda _w: None,
                setMaximumWidth=lambda _w: None,
                setSizePolicy=lambda *args, **kwargs: None,
                setVisible=lambda v: obj.setProperty("visible", bool(v)),
                hide=lambda: obj.setProperty("visible", False),
                show=lambda: obj.setProperty("visible", True),
            )

        proxy = SimpleNamespace(
            vin_search_button=wrap_button("vin_search_button"),
            plate_state_box=wrap_combo("plate_state_box"),
            plate_line=wrap_line("plate_line"),
            vin_line=wrap_line("vin_line"),
            year_line=wrap_line("year_line"),
            make_line=wrap_line("make_line"),
            model_line=wrap_line("model_line"),
            engine_line=wrap_line("engine_line"),
            trim_line=wrap_line("trim_line"),
            vehicle_cancel_button=wrap_button("vehicle_cancel_button"),
            vehicle_save_button=wrap_button("vehicle_save_button"),
            horizontalLayout=None,
        )
        return proxy

    def _theme_palette(self):
        """Return a palette dict matching the current theme name."""
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

    def add_vehicle(self):
        if not self.ui.customer_table.currentItem():
            self._show_message("No Customer Selected, Please Highlight A Customer!")
            return

        form = self._open_vehicle_form()
        if form is None:
            return
        form.vin_search_button.clicked.connect(self.search_vehicle)
        form.vehicle_save_button.clicked.connect(self.load_customer_id)

    def _open_vehicle_form(self):
        base_dir = Path(__file__).resolve().parents[1]
        qml_path = str(base_dir / "qml" / "VehicleSearch.qml")

        # QML-only vehicle search form
        try:
            palette = self._theme_palette()
            self.ui.vehicle_window, root_obj = self.ui.widget_manager.create_or_restore_qml(
                "vehicle_window",
                qml_path,
                parent=self.ui,
                context_properties={
                    "vehicleManager": self,
                    "mainWindow": self.ui,
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )

            self._vehicle_root = root_obj
            self.ui.vehicle_window.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint |
                QtCore.Qt.WindowType.Dialog
            )
            self.ui.vehicle_window.setWindowModality(
                QtCore.Qt.WindowModality.WindowModal
            )
            self.ui.vehicle_window.setParent(self.ui)
            self.ui.vehicle_window.setFocus()

            # Map QML objectNames to a proxy so downstream code can keep using the same attributes.
            self.ui.vehicle_window_ui = self._build_qml_proxy(root_obj)
            form = self._form()
            if form is None:
                return None

            # Optional QML-level signals
            for sig_name, slot in (
                ("searchRequested", self.search_vehicle),
                ("saveRequested", self.load_customer_id),
                ("cancelRequested", lambda: self.ui.widget_manager.close_and_delete("vehicle_window")),
            ):
                sig = getattr(root_obj, sig_name, None)
                if sig is not None:
                    try:
                        sig.connect(slot)
                    except Exception:
                        pass

            # Populate plate state list if present and ptcli is available
            if _ptcli_available():
                if form.plate_state_box:
                    try:
                        form.plate_state_box.addItems(STATES)
                        form.plate_state_box.show()
                    except Exception:
                        pass
                if form.plate_line:
                    try:
                        form.plate_line.show()
                    except Exception:
                        pass
            else:
                if form.plate_state_box:
                    try:
                        form.plate_state_box.hide()
                    except Exception:
                        pass
                if form.plate_line:
                    try:
                        form.plate_line.hide()
                    except Exception:
                        pass

            # Wire cancel + uppercase normalization
            if form.vehicle_cancel_button and form.vehicle_cancel_button.clicked:
                try:
                    form.vehicle_cancel_button.clicked.connect(
                        lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))
                except Exception:
                    pass
            if form.vin_line and form.vin_line.textChanged:
                form.vin_line.textChanged.connect(self._enforce_uppercase_vin)
            if form.plate_line and form.plate_line.textChanged:
                form.plate_line.textChanged.connect(self._enforce_uppercase_plate)

            self.ui.vehicle_window.show()
            return form
        except Exception:
            self._show_message("Unable to load vehicle form.")
            return None

    def search_vehicle(self):
        form = self._form()
        if form is None:
            return
        vin_text = (form.vin_line.text() or "").strip().upper()
        plate = (form.plate_line.text() or "").strip().upper()

        if _ptcli_available() and plate:
            state = (form.plate_state_box.currentText() or "").strip().upper()
            if not state:
                self._show_message("Select a plate state for Plate2VIN lookup.")
                return

            if self._plate_sidecar is None:
                ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
                self._plate_sidecar = GoSidecarManager(str(ptcli_path), parent=self.ui)
                self._plate_sidecar.plateDecoded.connect(
                    self._on_plate_decoded, QtCore.Qt.ConnectionType.UniqueConnection
                )
                self._plate_sidecar.errorText.connect(
                    lambda msg: self._show_message(msg)
                )

            token = ""
            ph = getattr(self.ui, "parts_hub_manager", None)
            if ph is not None:
                try:
                    token = ph._current_token() or ""
                except Exception:
                    token = ""

            if not token:
                self._show_message("Plate lookup requires a valid token. Configure in Settings first.")
                return

            self._plate_sidecar.plate_to_vin(token=token, plate=plate, state=state)
            self._show_message("Looking up plate, please wait...")
            return

        ### Fallback to VIN decoding if propietary plate2vin is not available ###
        if vin_text and len(vin_text) == 17:
            try:
                vin = VIN(vin_text)
                form.year_line.setText(vin.ModelYear)
                form.make_line.setText(vin.Make)
                form.model_line.setText(vin.Model)
                form.engine_line.setText(vin.DisplacementL)
                form.trim_line.setText(vin.Trim)
                return
            except Exception:
                pass

        self._show_message("Please enter a valid 17 digit VIN or plate.")
        form.vin_line.clear()

    def load_customer_id(self):
        """Determine the selected customer_id and save the vehicle for that customer."""
        if self._form() is None:
            return
        row = self.ui.customer_table.currentRow()
        customer_data = [
            self.ui.customer_table.item(row, col).text() if self.ui.customer_table.item(row, col) else ""
            for col in range(self.ui.customer_table.columnCount())
        ]

        customer_id = customer_data[9]

        if customer_id:
            self.save_vehicle(customer_id)
        else:
            self._show_message("Could not find customer ID.")

    def save_vehicle(self, customer_id):
        form = self._form()
        if form is None:
            return
        vehicle_data = [
            form.vin_line.text(),
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id,
        ]

        try:
            plate = (form.plate_line.text() or "").strip().upper()
        except Exception:
            plate = ""
        try:
            state = (form.plate_state_box.currentText() or "").strip().upper() if _ptcli_available() else ""
        except Exception:
            state = ""

        vehicle_data.append(plate)
        vehicle_data.append(state)

        if not Validator.vehicle_fields_filled(vehicle_data[:6]):
            self._show_message("Please decode VIN or fill in year, make, and model.")
            return

        VehicleRepository.insert_vehicle(vehicle_data)
        self.ui.widget_manager.close_and_delete("vehicle_window")
        QtCore.QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.information(self.ui, "Vehicle Added",
                        "Vehicle has been added."))

    def vehicle_search_filter(self, text):
        for row in range(self.ui.vehicle_table.rowCount()):
            match = any(
                text.lower() in (self.ui.vehicle_table.item(row, col).text().lower() if self.ui.vehicle_table.item(row, col) else "")
                for col in range(self.ui.vehicle_table.columnCount())
            )
            self.ui.vehicle_table.setRowHidden(row, not match)

    def add_new_vehicle(self):
        """Triggered from other workflows (e.g., belongs_to); reuses the same dialog."""
        form = self._open_vehicle_form()
        if form is None:
            return
        form.vehicle_save_button.setText("Next")
        form.vin_search_button.clicked.connect(self.search_vehicle)
        form.vehicle_save_button.clicked.connect(self.belongs_to_manager.belongs_to)

    def _show_message(self, text):
        msg = getattr(self.ui, "message", None)
        if msg is None:
            return
        parent = getattr(self.ui, "vehicle_window", None)
        try:
            if parent is not None and parent.isVisible():
                msg.setParent(parent)
            else:
                msg.setParent(self.ui)
        except RuntimeError:
            return
        msg.setText(text)
        msg.show()

    #Normalize VIN INPUT TO UPPERCASE AN NO SPACES
    def _enforce_uppercase_vin(self, text=None):
        form = self._form()
        if form is None:
            return
        # If the signal did not pass text (e.g., QML), fall back to current field text.
        current = text if text is not None else getattr(form.vin_line, "text", lambda: "")()
        cleaned = (current or "").replace(" ", "").upper()
        le = form.vin_line
        try:
            cursor_pos = le.cursorPosition()
            le.setText(cleaned)
            le.setCursorPosition(min(cursor_pos, len(cleaned)))
        except Exception:
            le.setText(cleaned)
        
    #NORMALIZE PLATE INPUT TO UPPERCASE AN NO SPACES
    def _enforce_uppercase_plate(self, text=None):
        form = self._form()
        if form is None:
            return
        current = text if text is not None else getattr(form.plate_line, "text", lambda: "")()
        cleaned = (current or "").replace(" ", "").upper()
        le = form.plate_line
        try:
            cursor_pos = le.cursorPosition()
            le.setText(cleaned)
            le.setCursorPosition(min(cursor_pos, len(cleaned)))
        except Exception:
            le.setText(cleaned)

    def _on_plate_decoded(self, payload: dict):
        form = self._form()
        vw = getattr(self.ui, "vehicle_window", None)
        try:
            if form is None or vw is None or not vw.isVisible():
                return
        except RuntimeError:
            return

        results = payload.get("results") or payload.get("Results") or []
        if isinstance(results, list) and results:
            result = results[0]
        elif isinstance(results, dict):
            result = results
        else:
            self._show_message("No vehicle found for that plate.")
            return

        vin_str = (result.get("vin") or result.get("VIN") or "").strip().upper()
        decode = result.get("vinDecode") or result.get("vin_decode") or {}

        if vin_str:
            try:
                form.vin_line.setText(vin_str)
            except RuntimeError:
                return

        year = decode.get("MDL_YR") or decode.get("ACES_YEAR_ID") or ""
        make = decode.get("ACES_MAKE_NAME") or decode.get("MAK_NM") or ""
        model = decode.get("ACES_MODEL_NAME") or decode.get("MDL_DESC") or ""
        liters = decode.get("ACES_LITERS") or decode.get("ENG_DISPLCMNT_CL")
        trim = decode.get("TRIM_DESC") or decode.get("ACES_SUB_MODEL_NAME") or ""

        engine = ""
        if liters:
            l_str = str(liters)
            if l_str and "." not in l_str and len(l_str) == 1:
                l_str = f"{l_str}.0"
            engine = f"{l_str}L"

        try:
            if year:
                form.year_line.setText(str(year))
            if make:
                form.make_line.setText(str(make))
            if model:
                form.model_line.setText(str(model))
            if engine:
                form.engine_line.setText(engine)
            if trim:
                form.trim_line.setText(str(trim))
        except RuntimeError:
            return
