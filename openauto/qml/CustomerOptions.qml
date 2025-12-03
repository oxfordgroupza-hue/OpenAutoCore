import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: customerOptions
    objectName: "customer_options_form"
    width: 720
    height: 230
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
        "success": "#76ABAE",
        "successHover": "#828786",
        "successPress": "#5b7f83",
        "danger": "#A0153E",
        "dangerHover": "#C49497",
        "dangerPress": "#7a0f31",
        "buttonText": "#FFFFFF"
    }

    // Derived text colors so dark theme is always pure white
    property color textColor: palette.name === "dark" ? "#FFFFFF" : (palette.text || "#1E1E1E")
    property color subTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.text2 || palette.text || "#5C5C5C")

    property int buttonWidth: 140
    property int buttonHeight: 44

    signal cancelRequested()
    signal createRoRequested()
    signal editCustomerRequested()
    signal addVehicleRequested()
    signal deleteCustomerRequested()

    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        width: Math.min(parent.width - 48, 640)
        height: 190
        radius: 12
        color: palette.surface
        border.color: palette.fieldBorder
        border.width: 0

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 14

            // Title + subtitle
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Label {
                    text: "Customer Options"
                    color: customerOptions.textColor
                    font.pixelSize: 18
                    font.bold: true
                    Layout.fillWidth: true
                }

                Label {
                    text: "Choose what you’d like to do with this customer."
                    color: customerOptions.subTextColor
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            // Main actions row
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 10

                // Create RO
                Button {
                    id: create_ro_customer_button
                    objectName: "create_ro_customer_button"
                    text: "Create RO"
                    icon.source: "qrc:/resources/Icons/add-document.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: customerOptions.buttonWidth
                    Layout.preferredHeight: customerOptions.buttonHeight
                    onClicked: customerOptions.createRoRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: create_ro_customer_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: create_ro_customer_button.text
                            color: palette.buttonText || palette.text
                            font: create_ro_customer_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: create_ro_customer_button.down ? palette.successPress
                              : create_ro_customer_button.hovered ? palette.successHover
                              : palette.success
                    }
                }

                // Edit customer
                Button {
                    id: edit_customer_button
                    objectName: "edit_customer_button"
                    text: "Edit Customer"
                    icon.source: "qrc:/resources/Icons/user.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: customerOptions.buttonWidth
                    Layout.preferredHeight: customerOptions.buttonHeight
                    onClicked: customerOptions.editCustomerRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: edit_customer_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: edit_customer_button.text
                            color: palette.buttonText || palette.text
                            font: edit_customer_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: edit_customer_button.down ? palette.accentPress
                              : edit_customer_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }

                // Add vehicle
                Button {
                    id: add_customer_vehicle_button
                    objectName: "add_customer_vehicle_button"
                    text: "Add Vehicle"
                    icon.source: "qrc:/resources/Icons/car.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: customerOptions.buttonWidth
                    Layout.preferredHeight: customerOptions.buttonHeight
                    onClicked: customerOptions.addVehicleRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: add_customer_vehicle_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: add_customer_vehicle_button.text
                            color: palette.buttonText || palette.text
                            font: add_customer_vehicle_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: add_customer_vehicle_button.down ? palette.accentPress
                              : add_customer_vehicle_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }

                // Delete customer
                Button {
                    id: delete_customer_button
                    objectName: "delete_customer_button"
                    text: "Delete"
                    icon.source: "qrc:/resources/Icons/trash.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: customerOptions.buttonWidth
                    Layout.preferredHeight: customerOptions.buttonHeight
                    onClicked: customerOptions.deleteCustomerRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: delete_customer_button.icon.source
                            width: 20; height: 20
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: delete_customer_button.text
                            color: palette.buttonText || palette.text
                            font: delete_customer_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: delete_customer_button.down ? palette.dangerPress
                              : delete_customer_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }

                // Cancel
                Button {
                    id: cancel_customer_options_button
                    objectName: "cancel_customer_options_button"
                    text: "Cancel"
                    icon.source: "qrc:/resources/icons3/24x24/cil-x.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: customerOptions.buttonWidth
                    Layout.preferredHeight: customerOptions.buttonHeight
                    onClicked: customerOptions.cancelRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Image {
                            source: cancel_customer_options_button.icon.source
                            width: 18; height: 18
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: cancel_customer_options_button.text
                            color: palette.buttonText || palette.text
                            font: cancel_customer_options_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: cancel_customer_options_button.down ? palette.dangerPress
                              : cancel_customer_options_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }
            }
        }
    }

    focus: true
    Keys.onEscapePressed: cancel_customer_options_button.clicked()
}
