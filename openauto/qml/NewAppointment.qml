import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: appointmentForm
    objectName: "new_appointment_form"
    width: 960
    height: 560
    color: palette.bg

    // Palette injected from Python via context property "themePalette"
    property var palette: themePalette || {
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
        "inputText": "#FFFFFF"
    }

    property color textColor: palette.name === "dark" ? "#FFFFFF" : (palette.text || "#1E1E1E")
    property color subTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.text2 || palette.text || "#5C5C5C")
    property color fieldTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.inputText || palette.text || "#1E1E1E")

    // Backing models are filled from Python using the helper functions below
    ListModel { id: customersModel }
    ListModel { id: vehiclesModel }
    // Allow injected QAbstractListModels from Python; fallback to local ListModels
    property var customerModel: (typeof customerListModel !== "undefined" && customerListModel) ? customerListModel : customersModel
    property var vehicleModel: (typeof vehicleListModel !== "undefined" && vehicleListModel) ? vehicleListModel : vehiclesModel
    // Selection + filter state
    property string searchTerm: ""
    property string selectedCustomerId: ""
    property string selectedVehicleId: ""

    // Convenience accessors for Python
    property alias notesText: notes_appt_edit.text
    function setNotes(value) { notes_appt_edit.text = value || "" }
    function setSearch(text) { customer_search__appt_line.text = text || "" }

    // Replace the table widgets' update* helpers with QML-friendly ones
    function setCustomers(rows) {
        customersModel.clear()
        if (!rows) {
            return
        }
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i] || []
            customersModel.append({
                last: row.last || row[0] || "",
                first: row.first || row[1] || "",
                phone: row.phone || row[2] || "",
                id: row.id || row.customer_id || row[3] || ""
            })
        }
    }

    function setVehicles(rows) {
        vehiclesModel.clear()
        if (!rows) {
            return
        }
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i] || []
            vehiclesModel.append({
                year: row.year || row[0] || "",
                make: row.make || row[1] || "",
                model: row.model || row[2] || "",
                ownerId: row.ownerId || row.customer_id || row[3] || "",
                vin: row.vin || row[4] || "",
                vehicleId: row.vehicleId || row[5] || ""
            })
        }
    }



    signal cancelRequested()
    signal saveRequested(string customerId, string vehicleId, string notes, string status)
    signal newCustomerRequested()
    signal newVehicleRequested(string customerId)
    signal customerHighlighted(string customerId)
    signal vehicleHighlighted(string vehicleId)
    signal searchChanged(string term)

    onSelectedCustomerIdChanged: {
        if (vehicle_table_small.count > 0) {
            vehicle_table_small.currentIndex = 0
        }
    }


    Rectangle {
        id: card
        anchors.centerIn: parent
        width: Math.min(parent.width - 32, 920)
        height: Math.min(parent.height - 32, 520)
        radius: 12
        color: palette.surface
        border.color: palette.divider
        border.width: 0

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Title + search row
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 4

                    Label {
                        text: "New Appointment"
                        color: appointmentForm.textColor
                        font.pixelSize: 18
                        font.bold: true
                        Layout.fillWidth: true
                    }
                    Label {
                        text: "Pick the customer and vehicle, jot down concerns, then save."
                        color: appointmentForm.subTextColor
                        font.pixelSize: 12
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }

                TextField {
                    id: customer_search__appt_line
                    objectName: "customer_search__appt_line"
                    Layout.preferredWidth: 220
                    placeholderText: "Search ..."
                    color: appointmentForm.fieldTextColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: TextInput.AlignHCenter
                    onTextChanged: {
                        appointmentForm.searchTerm = text.toLowerCase()
                        appointmentForm.searchChanged(text)
                    }
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: palette.fieldBg
                        border.color: customer_search__appt_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 38
                    }
                }
            }

            // Tables
            GridLayout {
                id: twoPanelGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 2
                columnSpacing: 12
                rowSpacing: 10
                property real colWidth: (width - columnSpacing) / 2

                // Customer panel
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: twoPanelGrid.colWidth
                    Layout.columnSpan: 1
                    spacing: 6

                    Label {
                        text: "Customer"
                        color: appointmentForm.textColor
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 8
                        color: palette.bg
                        border.color: palette.fieldBorder
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 4
                            spacing: 4

                            // Header
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                Label { text: "Last"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.fillWidth: true }
                                Label { text: "First"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.fillWidth: true }
                                Label { text: "Phone"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.preferredWidth: 120 }
                            }

                            ListView {
                                id: customer_table_small
                                objectName: "customer_table_small"
                                clip: true
                                spacing: 4
                                Layout.row: 1
                                Layout.column: 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: appointmentForm.customerModel
                                currentIndex: -1

                                delegate: Rectangle {
                                    id: customer_row_rect
                                    width: ListView.view.width
                                    height: visible ? 38 : 0
                                    radius: 6
                                    color: ListView.isCurrentItem ? palette.accentPress : palette.surface
                                    border.color: ListView.isCurrentItem ? palette.accent : palette.fieldBorder
                                    opacity: visible ? 1 : 0


                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 12

                                        Text {
                                            text: last
                                            color: (customer_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor

                                            font.pixelSize: 13
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: (parent.width - 120 - 24) / 2
                                        }

                                        Text {
                                            text: first
                                            color: (customer_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor
                                            font.pixelSize: 13
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: (parent.width - 120 - 24) / 2
                                        }

                                        Text {
                                            text: phone
                                            color: (customer_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor
                                            font.pixelSize: 13
                                            horizontalAlignment: Text.AlignHCenter
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: 120
                                        }
                                    }

                                

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            customer_table_small.currentIndex = index
                                            appointmentForm.selectedCustomerId = id
                                            appointmentForm.customerHighlighted(id)


                                            
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Button {
                        id: new_customer_appt_button
                        objectName: "new_customer_appt_button"
                        text: "New Customer"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        font.pixelSize: 14
                        font.bold: true
                        onClicked: appointmentForm.newCustomerRequested()

                        contentItem: Row {
                            anchors.centerIn: parent
                            spacing: 8
                            Image {
                                source: "qrc:/resources/icons3/24x24/cil-plus.png"
                                width: 22; height: 22
                                fillMode: Image.PreserveAspectFit
                            }
                            Text { text: new_customer_appt_button.text; color: palette.buttonText; font: new_customer_appt_button.font }
                        }

                        background: Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: new_customer_appt_button.down ? palette.accentPress
                                  : new_customer_appt_button.hovered ? palette.accentHover
                                  : palette.accent
                        }
                    }
                }

                // Vehicle panel
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: twoPanelGrid.colWidth
                    spacing: 6

                    Label {
                        text: "Vehicle"
                        color: appointmentForm.textColor
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 8
                        color: palette.bg
                        border.color: palette.fieldBorder
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 4
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                Label { text: "Year"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.preferredWidth: 70 }
                                Label { text: "Make"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.fillWidth: true }
                                Label { text: "Model"; color: appointmentForm.subTextColor; font.pixelSize: 12; Layout.fillWidth: true }
                            }

                            ListView {
                                id: vehicle_table_small
                                objectName: "vehicle_table_small"
                                clip: true
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 2
                                model: appointmentForm.vehicleModel
                                currentIndex: -1
                                delegate: Rectangle {
                                    width: ListView.view ? ListView.view.width : 0
                                    height: visible ? 36 : 0
                                    radius: 6
                                    color: ListView.isCurrentItem ? palette.accentPress : palette.surface
                                    border.color: ListView.isCurrentItem ? palette.accent : palette.fieldBorder
                                    opacity: visible ? 1 : 0
                                    property string ownerId: model.ownerId || model.customer_id || ""
                                    property string vehicleId: model.vehicleId || model.id || ""

                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 6
                                        Text {
                                            text: year
                                            color:(vehicle_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor
                                            font.pixelSize: 13
                                            horizontalAlignment: Text.AlignHCenter
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: (parent.width - 120 - 24) / 2
                                        }
                                        Text {
                                            text: make
                                            color:(vehicle_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor
                                            font.pixelSize: 13
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: (parent.width - 120 - 24) / 2
                                        }
                                        Text {
                                            text: model
                                            color:(vehicle_table_small.currentIndex === index) ? "#FFFFFF" : appointmentForm.textColor
                                            font.pixelSize: 13
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            wrapMode: Text.NoWrap
                                            verticalAlignment: Text.AlignVCenter
                                            width: 120
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            if (appointmentForm.selectedCustomerId !== "" && ownerId !== appointmentForm.selectedCustomerId) {
                                                return
                                            }
                                            vehicle_table_small.currentIndex = index
                                            appointmentForm.selectedVehicleId = vehicleId
                                            appointmentForm.vehicleHighlighted(vehicleId)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Button {
                        id: new_vehicle_appt_button
                        objectName: "new_vehicle_appt_button"
                        text: "New Vehicle"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        enabled: true
                       // visible: appointmentForm.selectedCustomerId !== ""
                      //  enabled: appointmentForm.selectedCustomerId !== ""
                        font.pixelSize: 14
                        font.bold: true
                        onClicked: appointmentForm.newVehicleRequested(appointmentForm.selectedCustomerId)

                        contentItem: Row {
                            anchors.centerIn: parent
                            spacing: 8
                            Image {
                                source: "qrc:/resources/icons3/24x24/cil-plus.png"
                                width: 22; height: 22
                                fillMode: Image.PreserveAspectFit
                            }
                            Text { text: new_vehicle_appt_button.text; color: palette.buttonText; font: new_vehicle_appt_button.font }
                        }

                        background: Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: new_vehicle_appt_button.down ? palette.accentPress
                                  : new_vehicle_appt_button.hovered ? palette.accentHover
                                  : palette.accent
                        }
                    }
                }
            }

            // Notes
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Label {
                    id: notes_appt_label
                    objectName: "notes_appt_label"
                    text: "Notes"
                    color: appointmentForm.textColor
                    font.pixelSize: 14
                    font.bold: true
                    font.italic: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                    radius: 8
                    color: palette.bg
                    border.color: palette.fieldBorder
                    border.width: 1

                    TextArea {
                        id: notes_appt_edit
                        objectName: "notes_appt_edit"
                        anchors.fill: parent
                        anchors.margins: 10
                        font.pixelSize: 14
                        font.bold: true
                        color: appointmentForm.fieldTextColor
                        wrapMode: TextEdit.WordWrap
                        background: null
                    }
                }
            }

            // Footer controls
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                // Drop / Wait radios
                RowLayout {
                    spacing: 12

                    RadioButton {
                        id: drop_appt_button
                        objectName: "drop_appt_button"
                        text: "Drop"
                        font.pixelSize: 13
                        font.bold: true
                        onClicked: console.log("Drop radio clicked, checked =", checked)
                    }

                    RadioButton {
                        id: wait_appt_button
                        objectName: "wait_appt_button"
                        text: "Wait"
                        font.pixelSize: 13
                        font.bold: true
                        onClicked: console.log("Wait radio clicked, checked =", checked)

                    }
                }

                Item { Layout.fillWidth: true }

                Button {
                    id: cancel_appt_button
                    objectName: "cancel_appt_button"
                    text: "Cancel"
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    font.bold: true
                    onClicked: appointmentForm.cancelRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Image {
                            source: "qrc:/resources/icons3/24x24/cil-x.png"
                            width: 20; height: 20
                            fillMode: Image.PreserveAspectFit
                        }
                        Text { text: cancel_appt_button.text; color: palette.buttonText; font: cancel_appt_button.font }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: cancel_appt_button.down ? palette.dangerPress
                              : cancel_appt_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }

                Button {
                    id: save_appt_button
                    objectName: "save_appt_button"
                    text: "Save"
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 42
                    enabled: true 
                    font.pixelSize: 14
                    font.bold: true
                    onClicked: {
                        var status = drop_appt_button.checked ? "drop" 
                                    : (wait_appt_button.checked ? "wait" : "")
                        appointmentForm.saveRequested(
                           appointmentForm.selectedCustomerId, 
                           appointmentForm.selectedVehicleId, 
                           notes_appt_edit.text, 
                           status
                        )

                        
                    }

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Image {
                            source: "qrc:/resources/icons3/24x24/cil-check.png"
                            width: 20; height: 20
                            fillMode: Image.PreserveAspectFit
                        }
                        Text { text: save_appt_button.text; color: palette.buttonText; font: save_appt_button.font }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: save_appt_button.down ? palette.successPress
                              : save_appt_button.hovered ? palette.successHover
                              : palette.success
                    }
                }
            }
        }
    }

    focus: true
    Keys.onEscapePressed: cancel_appt_button.clicked()
}
