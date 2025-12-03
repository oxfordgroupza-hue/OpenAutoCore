from pathlib import Path
from PyQt6 import QtCore, QtWidgets, QtGui
from openauto.utils.validator import Validator
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.appointment_repository import AppointmentRepository
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.ro_c3_repository import ROC3Repository
from openauto.managers.appointments.print_controller import PrintController
from PyQt6.QtCore import QTime
from openauto.subclassed_widgets.models.customer_list_model import CustomerListModel
from openauto.subclassed_widgets.models.vehicle_list_model import VehicleListModel
from pyvin import VIN
from openauto.managers.parts_tree.go_sidecar_manager import GoSidecarManager
from openauto.managers.vehicle_manager import VehicleManager
from openauto.managers.customer_manager import CustomerManager
from openauto.utils.qml_utils import appt_theme_palette, build_appt_qml_proxy


STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def _ptcli_available() -> bool:
    try:
        # appointments_manager.py lives in managers/appointments/, so hop to the managers root
        ptcli_path = (Path(__file__).resolve().parents[1] / "parts_tree" / "ptcli").resolve()
        return ptcli_path.is_file()
    except Exception:
        return False

class AppointmentsManager:
    def __init__(self, main_window, sql_monitor):
        self.ui = main_window
        self.sql_monitor = sql_monitor
        self.print_controller = PrintController(self.ui)
        self.selected_vehicle_id = None  ### ID NUMBER DECLARED EARLY
        self.selected_customer_id = None
        self.waiter = None
        self.dropper = None
        self.customer_model = CustomerListModel(self.ui)
        self.vehicle_model = VehicleListModel(self.ui)
        self._filter_timer = QtCore.QTimer(self.ui)
        self._filter_timer.setSingleShot(True)
        self._pending_filter_text = ""

        #create a print button for the daily schedule
        self.ui.print_schedule_button = QtWidgets.QPushButton(parent=self.ui.calender_frame)
        self.ui.print_schedule_button.setObjectName("print_schedule_button")
        self.ui.print_schedule_button.setMaximumSize(QtCore.QSize(200, 16777215))
        print_icon = QtGui.QIcon()
        print_icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-print.png"))
        self.ui.print_schedule_button.setIcon(print_icon)
        self.ui.print_schedule_button.setIconSize(QtCore.QSize(30, 30))
        self.ui.print_schedule_button.setText("Print")
        self.ui.print_schedule_button.setFlat(True)
        self.ui.gridLayout_12.addWidget(self.ui.print_schedule_button, 0, 3, 1, 1)
        self.ui.print_schedule_button.clicked.connect(self.print_daily_schedule)

        try:
            # Show only when hourly schedule page (hub index 5) is active
            self._update_print_schedule_visibility(self.ui.hub_stacked_widget.currentIndex())
            self.ui.hub_stacked_widget.currentChanged.connect(self._update_print_schedule_visibility)
        except Exception:
            pass

        self._plate_sidecar = None

    

### OPENS new_appointment QML ###
    def open_new_appointment(self):
        base_dir = Path(__file__).resolve().parents[2]
        qml_path = str(base_dir / "qml" / "NewAppointment.qml")
        
        try:
            palette = appt_theme_palette(self.ui)
            self.ui.new_appointment, root_obj = self.ui.widget_manager.create_or_restore_qml(
                "new_appointment",
                qml_path,
                parent=self.ui,
                context_properties={
                       "themePalette": palette,
                        "themeName": palette.get("name", "dark"),
                        "appointmentsManager": self,
                        "customerListModel": self.customer_model,
                        "vehicleListModel": self.vehicle_model,
                        
                }
            )
            
            
            self.ui.new_appointment_ui = build_appt_qml_proxy(root_obj)
            form = self.ui.new_appointment_ui
            form.new_cust_appt_button.hide()
            form.new_vehc_appt_button.hide()
            self.ui.new_appointment.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
            self.ui.new_appointment.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
            )
            
            self.ui.new_appointment.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.ui.new_appointment.setWindowTitle("New Appointment")
            # Reset selections and model filters so each open starts fresh
            self.selected_customer_id = None
            self.selected_vehicle_id = None
            try:
                self.customer_model.apply_filter("")
            except Exception:
                pass
            try:
                self.vehicle_model.filter_by_owner_ids(None)
            except Exception:
                pass
            try:
                root_obj.setProperty("selectedCustomerId", "")
                root_obj.setProperty("selectedVehicleId", "")
                root_obj.setProperty("searchTerm", "")
            except Exception:
                pass
            self._wire_new_appt_qml_signals(root_obj)
            self.ui.new_appointment.show()
            return self.ui.new_appointment_ui
        
        except Exception:        
            Validator.show_validation_error(self.ui.message, "Unable to load new appointment form.")
            return None
            
            
            

    def _wire_new_appt_qml_signals(self, root_obj):                   
        def _safe_connect(sig, slot):
            try:
                sig.connect(slot, QtCore.Qt.ConnectionType.UniqueConnection)
            except TypeError:
                try:
                    sig.connect(slot)
                except Exception:
                    pass
            except Exception:
                pass

        # Root-level QML signals
        
        _safe_connect(
            getattr(root_obj, "saveRequested"),
            lambda *args: self._save_appointment(*args),
        )
        
        _safe_connect(
            getattr(root_obj, "newVehicleRequested", None),
            lambda cid=None: self._on_new_vehicle_requested(cid)
        )
        _safe_connect(getattr(root_obj, "newCustomerRequested", None), self._create_new_customer)
        _safe_connect(getattr(root_obj, "customerHighlighted", None), self._on_customer_highlighted)
        _safe_connect(getattr(root_obj, "vehicleHighlighted", None), self._on_vehicle_highlighted)
        
        _safe_connect(
            getattr(root_obj, "cancelRequested", None),
            lambda: self.ui.widget_manager.close_and_delete("new_appointment")
        )
        
        _safe_connect(getattr(root_obj, "searchChanged", None), self._schedule_filter)
        

            
            
    def _on_new_vehicle_requested(self, cid=None, *args):
        chosen_cust = cid or self.selected_customer_id or getattr(self.ui, "customer_id_small", None)
        self.add_vehicle(chosen_cust)




    def _on_customer_highlighted(self, customer_id):
        self.ui.customer_id_small = customer_id
        try:
            self.selected_customer_id = int(customer_id)
        except Exception:
            self.selected_customer_id = customer_id
            
        customer_table = getattr(self.ui, "customer_table_small", None)
        vehicle_table = getattr(self.ui, "vehicle_table_small", None)
        
        if customer_table is not None and vehicle_table is not None:
            self._filter_vehicles_by_customer()
            return
        
        if not customer_id:
            self.vehicle_model.filter_by_owner_ids(None)
            self.selected_vehicle_id = None
            return
        
        self.vehicle_model.filter_by_owner_ids({str(customer_id)})
        
        try:
            if self.vehicle_model.rowCount() > 0:
                first_index = self.vehicle_model.index(0, 0)
                first_id = self.vehicle_model.data(
                    first_index, self.vehicle_model.ID_ROLE
                )
                try:
                    self.selected_vehicle_id = int(first_id)
                except Exception:
                    self.selected_vehicle_id = first_id
            else:
                self.selected_vehicle_id = None
        except Exception:
            self.selected_vehicle_id = None



    def _on_vehicle_highlighted(self, vehicle_id):
        try:
            self.selected_vehicle_id = int(vehicle_id)
        except Exception:
            self.selected_vehicle_id = vehicle_id

            

    ### OPENS NewCustomer dialog (QML) ###
    def _create_new_customer(self):
        # Use shared QML/new_customer logic via CustomerManager
        cm = CustomerManager(self.ui)
        cm.open_new_customer(on_saved=self.save_customer)
        # Hide the appointment dialog while creating a new customer
       # self.ui.new_appointment.hide()



    ### FILTERS CUSTOMERS AND VEHICLES UNDER SEARCH ###
    def _filter_customers_and_vehicles(self, text=None):
        
        search = (text or "").strip()

        customer_table = getattr(self.ui, "customer_table_small", None)
        vehicle_table = getattr(self.ui, "vehicle_table_small", None)

        # --- QML / model path ---
        if customer_table is None and vehicle_table is None:
            visible_customer_ids = self.customer_model.apply_filter(search)

            if search:
                self.vehicle_model.filter_by_owner_ids(visible_customer_ids)
            else:
                self.vehicle_model.filter_by_owner_ids(None)
            return

        # --- Legacy widget path
        visible_customer_ids = set()
        for row in range(customer_table.rowCount()):
            match = any(
                search.lower() in (
                    customer_table.item(row, col).text().lower()
                    if customer_table.item(row, col) else ""
                )
                for col in range(customer_table.columnCount())
            )
            customer_table.setRowHidden(row, not match)

            if match:
                id_item = customer_table.item(row, 3)  # Customer ID column
                if id_item:
                    visible_customer_ids.add(id_item.text().strip())

        for row in range(vehicle_table.rowCount()):
            vehicle_owner_item = vehicle_table.item(row, 3)  # Vehicle owner ID column
            if vehicle_owner_item:
                owner_id = vehicle_owner_item.text().strip()
                vehicle_table.setRowHidden(row, owner_id not in visible_customer_ids)
                
                
    #DEBOUNCES THE FILTER TO AVOID RECOMPUTING ON EVERY KEYSTROKE ###
    def _schedule_filter(self, text=None):
        self._pending_filter_text = text or ""
        self._filter_timer.stop()
        try:
            self._filter_timer.timeout.disconnect()
        except Exception:
            pass
        self._filter_timer.timeout.connect(lambda: self._filter_customers_and_vehicles(self._pending_filter_text))
        self._filter_timer.start(120)

        
            
            

### GRABS THE ID NUMBER OF THE CUSTOMER SELECTED SO OTHER FUNCTIONS CAN USE IT FOR MYSQL ###
    def store_selected_vehicle_id(self, row, column):
        item = self.ui.customer_table_small.item(row, 3)
        if item:
            try:
                self.selected_customer_id = int(item.text())
            except ValueError:
                self.selected_customer_id = None
        else:
            self.selected_customer_id = None
            
            

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
        customer_id = CustomerRepository.insert_customer(customer_data)
        self.add_vehicle(customer_id)
        self.ui.widget_manager.close_and_delete("new_customer")


### OPENS vehicle_search (QML) ###
    def add_vehicle(self, customer_id=None):
        if customer_id is not None:
            self.selected_customer_id = customer_id

        # Use the shared VehicleSearch QML dialog via VehicleManager's loader + proxy,
        # but keep this manager's search/save logic.
        vm = VehicleManager(self.ui)
        # vm._open_vehicle_form()
        base_dir = Path(__file__).resolve().parents[2]
        qml_path = str(base_dir / "qml" / "VehicleSearch.qml")

        try:
            palette = vm._theme_palette()
            self.ui.vehicle_window, root_obj = self.ui.widget_manager.create_or_restore_qml(
                "vehicle_window",
                qml_path,
                parent=self.ui,
                context_properties={
                    "vehicleManager": vm,
                    "mainWindow": self.ui,
                    "themePalette": palette,
                    "themeName": palette.get("name", "dark"),
                },
            )

            # Reuse VehicleManager's proxy so form.* APIs match the old widget form.
            self.ui.vehicle_window_ui = vm._build_qml_proxy(root_obj)

            self.ui.vehicle_window.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
            self.ui.vehicle_window.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
            )
            self.ui.vehicle_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.ui.vehicle_window.setFocus()

            form = self.ui.vehicle_window_ui

            # Wire cancel + uppercase + search/save to this manager's logic.
            if form.vehicle_cancel_button and form.vehicle_cancel_button.clicked:
                form.vehicle_cancel_button.clicked.connect(
                    lambda: self.ui.widget_manager.close_and_delete("vehicle_window")
                )
            if form.vin_line and form.vin_line.textChanged:
                form.vin_line.textChanged.connect(self._enforce_uppercase_vin)
            if form.plate_line and form.plate_line.textChanged:
                form.plate_line.textChanged.connect(self._enforce_uppercase_plate)
            if form.vin_search_button and form.vin_search_button.clicked:
                form.vin_search_button.clicked.connect(self.search_vehicle)
            if form.vehicle_save_button and form.vehicle_save_button.clicked:
                form.vehicle_save_button.clicked.connect(self.save_vehicle)

            # Plate state availability
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

            # Ensure the dialog appears above the appointment form
            self.ui.vehicle_window.show()
            try:
                self.ui.vehicle_window.raise_()
                self.ui.vehicle_window.activateWindow()
            except Exception:
                pass
        except Exception:
            Validator.show_validation_error(self.ui.message, "Unable to load vehicle search.")


### LOADS VEHICLE INFO BY VIN OR MANUALLY ENTERED DATA AND PASSES IT TO MYSQL VIA save_vehicle ###
    def search_vehicle(self):
        form = self.ui.vehicle_window_ui
        vin_text = (form.vin_line.text() or "").strip().upper()
        plate = (form.plate_line.text() or "").strip().upper()

        # Prefer Plate2VIN via GoSidecarManager, using plate + state
        if _ptcli_available() and plate:
            state = (form.plate_state_box.currentText() or "").strip().upper()
            if not state:
                Validator.show_validation_error(self.ui.message, "Select a plate state for Plate2VIN lookup.")
                return

            if self._plate_sidecar is None:
                ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
                self._plate_sidecar = GoSidecarManager(str(ptcli_path), parent=self.ui)
                self._plate_sidecar.plateDecoded.connect(
                    self._on_plate_decoded, QtCore.Qt.ConnectionType.UniqueConnection
                )
                self._plate_sidecar.errorText.connect(
                    lambda msg: Validator.show_validation_error(self.ui.message, msg)
                )

            token = ""
            ph = getattr(self.ui, "parts_hub_manager", None)
            if ph is not None:
                try:
                    token = ph._current_token() or ""
                except Exception:
                    token = ""

            if not token:
                Validator.show_validation_error(
                    self.ui.message,
                    "Plate lookup requires a valid token. Configure in Settings first.",
                )
                return

            self._plate_sidecar.plate_to_vin(token=token, plate=plate, state=state)
            return

        # Fallback: plain VIN decode when it looks valid
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

        Validator.show_validation_error(self.ui.message, "Invalid VIN or plate.")
        form.vin_line.clear()


### ENFORCES UPPERCASE INPUT TO VIN ###
    def _enforce_uppercase_vin(self, text):
        cleaned = (text or "").replace(" ", "").upper()
        le = self.ui.vehicle_window_ui.vin_line
        cursor_pos = le.cursorPosition()
        le.setText(cleaned)
        le.setCursorPosition(min(cursor_pos, len(cleaned)))

    def _enforce_uppercase_plate(self, text):
        cleaned = (text or "").replace(" ", "").upper()
        le = self.ui.vehicle_window_ui.plate_line
        cursor_pos = le.cursorPosition()
        le.setText(cleaned)
        le.setCursorPosition(min(cursor_pos, len(cleaned)))

    def _on_plate_decoded(self, payload: dict):
        form = getattr(self.ui, "vehicle_window_ui", None)
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
            Validator.show_validation_error(self.ui.message, "No vehicle found for that plate.")
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



### SAVES VEHICLE TO DATABASE WITH MATCHING ID NUMBER WITH SELECTED CUSTOMER OR CREATED CUSTOMER ###
    def save_vehicle(self):
        customer_id = self.selected_customer_id
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "No customer selected.")
            return

        form = self.ui.vehicle_window_ui
        vehicle_data = [
            form.vin_line.text(),
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
            state = (form.plate_state_box.currentText() or "").strip().upper() if _ptcli_available() else ""
        except Exception:
            state = ""

        vehicle_data.append(plate)
        vehicle_data.append(state)
        if not Validator.vehicle_fields_filled(vehicle_data[:6]):
            return

        VehicleRepository.insert_vehicle(vehicle_data)
        self.ui.widget_manager.close_and_delete("vehicle_window")
        self.ui.new_appointment.show()




    def _save_appointment(self, customer_id=None, vehicle_id=None, notes=None, dropoff_type=None):
        w = self.ui.weekly_schedule_table
        d = self.ui.hourly_schedule_table

        # Prefer weekly context; if not available, use hourly context
        row = getattr(w, "selected_row", None)
        date = getattr(w, "selected_date", None)
        if row is None or date is None:
            row = getattr(d, "selected_row", None)
            date = getattr(d, "selected_date", None)

        if row is None or date is None:
            self.ui.message.setText("Pick a time slot in the schedule first.")
            self.ui.message.show()
            return

        # Row -> time (7:00 AM start, 30-min slots)
        base_hour = 7
        hour = base_hour + (row // 2)
        minute = 30 if (row % 2) else 0
        time = QTime(hour, minute)

        customer_id = customer_id or self.selected_customer_id or getattr(self.ui, "customer_id_small", None)
        if not customer_id:
            self.ui.message.setText("No customer selected.")
            self.ui.message.show()
            return

        try:
            customer_id_int = int(customer_id)
        except Exception:
            customer_id_int = customer_id
            
            
        vehicle_id = vehicle_id or self.selected_vehicle_id
        if vehicle_id in ("", None):
            vehicle_id_int = None
        else:
            try:
                vehicle_id_int = int(vehicle_id)
            except Exception:
                vehicle_id_int = vehicle_id
                
        ### NOTES
        notes_text = (notes or "").strip()
        
        dropoff_type = (dropoff_type or "").strip().lower()
        if dropoff_type not in ("drop", "wait", ""):
            self.ui.message.setText("Please select 'wait' or 'drop' for the appointment type.")
            self.ui.message.show()
            return
        
        vin = None
        if vehicle_id_int is not None and self.vehicle_model is not None:
            try:
                target_id = str(vehicle_id_int)
                for row_idx in range(self.vehicle_model.rowCount()):
                    idx = self.vehicle_model.index(row_idx, 0)
                    mid = self.vehicle_model.data(idx, self.vehicle_model.ID_ROLE)
                    if str(mid) == target_id:
                        vin_val = self.vehicle_model.data(idx, self.vehicle_model.VIN_ROLE)
                        vin = (str(vin_val).strip() or None) if vin_val is not None else None
                        break
            except Exception:
                vin = None
                
        appt_id = AppointmentRepository.insert_appointment(
            customer_id=customer_id_int,
            vehicle_id=vehicle_id_int,
            vin=vin,
            date=date,
            time=time,
            notes=notes_text,
            dropoff_type=dropoff_type,
        )
                    
                    
        ###CREATE REPAIR ORDER AS WELL WHEN APPOINTMENT IS SAVED ###
        try:
            current_user_id = getattr(self.ui, "current_user_id", None)
            if current_user_id is None:
               cu = getattr(self.ui, "current_user", None)
               current_user_id = cu.get("id") if isinstance(cu, dict) else getattr(cu, "id", None)

            assigned_writer_id = getattr(self.ui, "assigned_writer_id", None)
            if assigned_writer_id is None:
                aw = getattr(self.ui, "current_user", None)
                assigned_writer_id = aw.get("id") if isinstance(aw, dict) else getattr(aw, "id", None)
                
            ro_id = None
            if vehicle_id_int:
                ro_id = RepairOrdersRepository.create_repair_order(
                    customer_id=customer_id_int,
                    vehicle_id=vehicle_id_int,
                    appointment_id=appt_id,
                    ro_number=None,
                    created_by=current_user_id,
                    assigned_writer_id=assigned_writer_id,
                )
                
                if notes_text:
                    ROC3Repository.set_or_create_concern(
                        ro_id,
                        notes_text,
                        created_by=current_user_id, 
                    )
        except Exception:
            import traceback
            traceback.print_exc()
            
        try:
            self.ui.widget_manager.close_and_delete("new_appointment")
        except Exception:
            pass
        
        msg = QtWidgets.QMessageBox(self.ui)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setWindowTitle("Appointment Saved")
        msg.setText("Appointment Save Successful"
                    + (" + RO created." if vehicle_id_int else "."))
        msg.exec()
               
        

    def print_daily_schedule(self):
        # Prefer the day currently loaded in the hourly table (kept in sync with week/cell clicks)
        date = getattr(self.ui.hourly_schedule_table, "selected_date", None) or self.ui.schedule_calendar.selectedDate()
        appointments = AppointmentRepository.get_appointments_for_week(date, date)
        self.print_controller.print_daily_schedule(appointments, date)
        
               
    def _update_print_schedule_visibility(self, index: int):
        btn = getattr(self.ui, "print_schedule_button", None)
        if not btn:
            return
        # Hourly schedule page lives at hub_stacked_widget index 5
        btn.setVisible(index == 5)
