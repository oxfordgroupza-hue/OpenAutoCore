import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: customerSearchForm
    objectName: "customer_search_form"
    width: 636
    height: 278
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

    // Derived text colors (dark → pure white)
    property color textColor: palette.name === "dark" ? "#FFFFFF" : (palette.text || "#1E1E1E")
    property color subTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.text2 || palette.text || "#5C5C5C")
    property color fieldTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.inputText || palette.text || "#1E1E1E")

    signal confirmRequested()
    signal cancelRequested()
    signal addCustomerRequested()

    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        width: Math.min(parent.width - 32, 600)
        height: 230
        radius: 10
        color: palette.surface
        border.color: palette.divider
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Top row: combo + "New Customer"
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                ComboBox {
                    id: customer_name_box
                    objectName: "customer_name_box"
                    Layout.fillWidth: true
                    implicitHeight: 32

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: customer_name_box.activeFocus ? palette.accent : palette.fieldBorder
                    }

                    contentItem: Text {
                        text: customer_name_box.currentText.length > 0 ? customer_name_box.currentText : "Customer"
                        color: customerSearchForm.fieldTextColor
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        leftPadding: 8
                    }
                }

                Button {
                    id: add_customer_button
                    objectName: "add_customer_button"
                    text: "New Customer"
                    icon.source: "qrc:/resources/Icons/user-add.png"
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: 36
                    onClicked: customerSearchForm.addCustomerRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Image {
                            source: add_customer_button.icon.source
                            width: 20; height: 20
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: add_customer_button.text
                            color: palette.buttonText
                            font: add_customer_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: add_customer_button.down ? palette.accentPress
                              : add_customer_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }
            }

            // Middle row: label + search field
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Label {
                    id: belongs_to_label
                    objectName: "belongs_to_label"
                    text: "Vehicle Belongs To..."
                    color: customerSearchForm.textColor
                    font.pixelSize: 13
                    font.bold: true
                    Layout.preferredWidth: 160
                }

                TextField {
                    id: customer_search_edit
                    objectName: "customer_search_edit"
                    Layout.fillWidth: true
                    placeholderText: "Search ..."
                    color: customerSearchForm.fieldTextColor
                    font.pixelSize: 14
                    horizontalAlignment: TextInput.AlignHCenter

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: customer_search_edit.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 32
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            // Bottom row: Cancel + Confirm
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    id: cancel_customer_search_button
                    objectName: "cancel_customer_search_button"
                    text: "Cancel"
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 36
                    onClicked: customerSearchForm.cancelRequested()

                    contentItem: Text {
                        text: cancel_customer_search_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: cancel_customer_search_button.down ? palette.dangerPress
                              : cancel_customer_search_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }

                Item { Layout.fillWidth: true }

                Button {
                    id: confirm_customer_search_button
                    objectName: "confirm_customer_search_button"
                    text: "Confirm"
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: 36
                    onClicked: customerSearchForm.confirmRequested()

                    contentItem: Text {
                        text: confirm_customer_search_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: confirm_customer_search_button.down ? palette.successPress
                              : confirm_customer_search_button.hovered ? palette.successHover
                              : palette.success
                    }
                }
            }
        }
    }
}
