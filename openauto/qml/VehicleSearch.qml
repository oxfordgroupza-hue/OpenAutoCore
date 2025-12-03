import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: vehicleSearchForm
    objectName: "vehicle_search_form"
    width: 593
    height: 600
    color: palette.bg

    // Palette is injected from Python via context property "themePalette"; defaults to dark.
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

    // Derived text colors so dark theme is always pure white
    property color textColor: palette.name === "dark" ? "#FFFFFF" : (palette.text || "#1E1E1E")
    property color subTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.text2 || palette.text || "#5C5C5C")
    property color fieldTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.inputText || palette.text || "#1E1E1E")

    // Used by Python code & consistent across buttons
    property int buttonfontSize: 18

    // Centered "card" for the actual form
    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        width: Math.min(parent.width - 48, 520)
        height: Math.min(parent.height - 48, 520)
        radius: 12
        color: palette.surface
        border.color: palette.divider
        border.width: 0

        ColumnLayout {
            id: contentLayout
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // --- Title & subtitle ---
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Label {
                    text: "Vehicle Lookup"
                    color: vehicleSearchForm.textColor
                    font.pixelSize: 20
                    font.bold: true
                    Layout.fillWidth: true
                }

                Label {
                    text: "Search by VIN or license plate, then confirm the decoded details."
                    color: vehicleSearchForm.subTextColor
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            // --- Plate row (State + Plate # + Search button) ---
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Label {
                    text: "License Plate"
                    color: vehicleSearchForm.textColor
                    font.pixelSize: 13
                    Layout.fillWidth: true
                }

                RowLayout {
                    spacing: 10
                    Layout.fillWidth: true

                    ComboBox {
                        id: plate_state_box
                        objectName: "plate_state_box"
                        Layout.preferredWidth: 130
                        editable: false
                        // Model will be set from Python via addItems()
                        background: Rectangle {
                            anchors.fill: parent
                            radius: 4
                            color: palette.fieldBg
                            border.color: plate_state_box.activeFocus ? palette.accent : palette.fieldBorder
                            implicitHeight: 36
                        }
                        contentItem: Text {
                            text: plate_state_box.currentText
                            color: vehicleSearchForm.fieldTextColor
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                            leftPadding: 8
                        }
                    }

                    TextField {
                        id: plate_line
                        objectName: "plate_line"
                        Layout.preferredWidth: 150
                        placeholderText: "Plate #"
                        color: vehicleSearchForm.fieldTextColor
                        font.pixelSize: 14
                        font.bold: true

                        background: Rectangle {
                            anchors.fill: parent
                            radius: 4
                            color: palette.fieldBg
                            border.color: plate_line.activeFocus ? palette.accent : palette.fieldBorder
                            implicitHeight: 36
                        }
                    }

                    Button {
                        id: vin_search_button
                        objectName: "vin_search_button"
                        text: "Search"
                        icon.source: "qrc:/resources/Icons/search.png"
                        icon.width: 25
                        icon.height: 25
                        hoverEnabled: true
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: vehicleSearchForm.actionButtonHeight
                        font.pixelSize: vehicleSearchForm.buttonfontSize
                        font.weight: Font.DemiBold
                        onClicked: vehicleSearchForm.searchRequested()

                        contentItem: Row {
                            anchors.centerIn: parent
                            spacing: 6

                            Image {
                                source: vin_search_button.icon.source
                                width: vin_search_button.icon.width
                                height: vin_search_button.icon.height
                                fillMode: Image.PreserveAspectFit
                            }

                            Text {
                                text: vin_search_button.text
                                color: palette.buttonText
                                font.pixelSize: vin_search_button.font.pixelSize
                                font.weight: vin_search_button.font.weight
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        background: Rectangle {
                            anchors.fill: parent
                            radius: 4
                            color: vin_search_button.down ? palette.accentPress
                                  : vin_search_button.hovered ? palette.accentHover
                                  : palette.accent
                        }
                    }
                }
            }

            // --- VIN helper label ---
            Label {
                text: "Or enter VIN manually"
                color: vehicleSearchForm.subTextColor
                font.pixelSize: 12
                Layout.fillWidth: true
                Layout.topMargin: 4
            }

            // --- VIN field under plate controls ---
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Label {
                    id: vin_label
                    objectName: "vin_label"
                    text: "VIN"
                    color: vehicleSearchForm.textColor
                    font.pixelSize: 13
                    Layout.fillWidth: true
                }

                TextField {
                    id: vin_line
                    objectName: "vin_line"
                    Layout.fillWidth: true
                    placeholderText: "17-digit VIN"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: TextInput.AlignHCenter

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: vin_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }
            }

            // --- Divider before decoded details ---
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: palette.divider
                Layout.topMargin: 8
                Layout.bottomMargin: 4
            }

            // --- Decoded details header ---
            Label {
                text: "Decoded Vehicle Details"
                color: vehicleSearchForm.textColor
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
            }

            // --- Details grid: year/make/model/trim/engine ---
            GridLayout {
                columns: 2
                columnSpacing: 10
                rowSpacing: 10
                Layout.fillWidth: true

                // Year
                TextField {
                    id: year_line
                    objectName: "year_line"
                    Layout.fillWidth: true
                    placeholderText: "Year"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: year_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }

                // Make
                TextField {
                    id: make_line
                    objectName: "make_line"
                    Layout.fillWidth: true
                    placeholderText: "Make"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: make_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }

                // Model
                TextField {
                    id: model_line
                    objectName: "model_line"
                    Layout.fillWidth: true
                    placeholderText: "Model"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: model_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }

                // Trim
                TextField {
                    id: trim_line
                    objectName: "trim_line"
                    Layout.fillWidth: true
                    placeholderText: "Trim"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: trim_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }

                // Engine (full width)
                TextField {
                    id: engine_line
                    objectName: "engine_line"
                    Layout.columnSpan: 2
                    Layout.fillWidth: true
                    placeholderText: "Engine (e.g. 3.5L V6)"
                    color: vehicleSearchForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: engine_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }
            }

            // --- Spacer to push buttons down if there's extra height ---
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            // --- Buttons row: Cancel (secondary) + Save (primary) ---
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 8
                spacing: 10

            Button {
                id: vehicle_cancel_button
                objectName: "vehicle_cancel_button"
                text: "Cancel"
                font.pixelSize: vehicleSearchForm.buttonfontSize
                Layout.preferredWidth: 150
                Layout.preferredHeight: 40
                hoverEnabled: true

                contentItem: Text {
                    text: vehicle_cancel_button.text
                    anchors.centerIn: parent
                    color: palette.buttonText
                    font.pixelSize: vehicleSearchForm.buttonfontSize
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    anchors.fill: parent
                    radius: 4
                    color: vehicle_cancel_button.down ? palette.dangerPress
                          : vehicle_cancel_button.hovered ? palette.dangerHover
                          : palette.danger
                }
            }

            Item { Layout.fillWidth: true } // spacer

                Button {
                    id: vehicle_save_button
                    objectName: "vehicle_save_button"
                    text: "Save Vehicle"
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 40
                    hoverEnabled: true
                    font.pixelSize: vehicleSearchForm.buttonfontSize
                    font.weight: Font.DemiBold

                    contentItem: Text {
                        text: vehicle_save_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: vehicle_save_button.font.pixelSize
                        font.weight: vehicle_save_button.font.weight
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: vehicle_save_button.down ? palette.successPress
                              : vehicle_save_button.hovered ? palette.successHover
                              : palette.success
                    }
                }
            }
        }
    }

    // Focus VIN on open for fast workflow
    Component.onCompleted: vin_line.forceActiveFocus()
}
