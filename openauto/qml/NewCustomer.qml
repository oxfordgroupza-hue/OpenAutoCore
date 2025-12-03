import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: newCustomerForm
    objectName: "create_customer_form"
    width: 606
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

    // Derived text colors (dark → pure white)
    property color textColor: palette.name === "dark" ? "#FFFFFF" : (palette.text || "#1E1E1E")
    property color fieldTextColor: palette.name === "dark" ? "#FFFFFF" : (palette.inputText || palette.text || "#1E1E1E")

    // Shared button font size
    property int buttonFontSize: 16

    signal saveRequested()
    signal cancelRequested()
    signal editRequested()

    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        width: Math.min(parent.width - 32, 570)
        height: Math.min(parent.height - 32, contentLayout.implicitHeight + 36)
        radius: 10
        color: palette.surface
        border.color: palette.divider
        border.width: 0

        ColumnLayout {
            id: contentLayout
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            // Title
            Label {
                text: "New Customer"
                color: newCustomerForm.textColor
                font.pixelSize: 20
                font.bold: true
                Layout.fillWidth: true
            }

            // First / Last name
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: first_name_line
                    objectName: "first_name_line"
                    Layout.fillWidth: true
                    placeholderText: "First Name"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: first_name_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }

                TextField {
                    id: last_name_line
                    objectName: "last_name_line"
                    Layout.fillWidth: true
                    placeholderText: "Last Name"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: last_name_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }
            }

            // Address
            TextField {
                id: address_line
                objectName: "address_line"
                Layout.fillWidth: true
                placeholderText: "Address"
                color: newCustomerForm.fieldTextColor
                font.pixelSize: 14
                background: Rectangle {
                    anchors.fill: parent
                    radius: 4
                    color: palette.fieldBg
                    border.color: address_line.activeFocus ? palette.accent : palette.fieldBorder
                    implicitHeight: 40
                }
            }

            // City / State / Zip
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: city_line
                    objectName: "city_line"
                    Layout.fillWidth: true
                    placeholderText: "City"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: city_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }

                TextField {
                    id: state_line
                    objectName: "state_line"
                    Layout.preferredWidth: 80
                    placeholderText: "State"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    horizontalAlignment: TextInput.AlignHCenter
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: state_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }

                TextField {
                    id: zipcode_line
                    objectName: "zipcode_line"
                    Layout.preferredWidth: 100
                    placeholderText: "Zip"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    horizontalAlignment: TextInput.AlignHCenter
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: zipcode_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }
            }

            // Phone / Alt phone
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: phone_line
                    objectName: "phone_line"
                    Layout.fillWidth: true
                    placeholderText: "Phone #"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    horizontalAlignment: TextInput.AlignHCenter
                    inputMask: "(000) 000-0000;_"
                    inputMethodHints: Qt.ImhDialableCharactersOnly
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: phone_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }

                TextField {
                    id: alt_line
                    objectName: "alt_line"
                    Layout.fillWidth: true
                    placeholderText: "Second #"
                    color: newCustomerForm.fieldTextColor
                    font.pixelSize: 14
                    horizontalAlignment: TextInput.AlignHCenter
                    inputMask: "(000) 000-0000;_"
                    inputMethodHints: Qt.ImhDialableCharactersOnly
                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: palette.fieldBg
                        border.color: alt_line.activeFocus ? palette.accent : palette.fieldBorder
                        implicitHeight: 40
                    }
                }
            }

            // Email
            TextField {
                id: email_line
                objectName: "email_line"
                Layout.fillWidth: true
                placeholderText: "Email"
                color: newCustomerForm.fieldTextColor
                font.pixelSize: 14
                background: Rectangle {
                    anchors.fill: parent
                    radius: 4
                    color: palette.fieldBg
                    border.color: email_line.activeFocus ? palette.accent : palette.fieldBorder
                    implicitHeight: 40
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 8
            }

            // Buttons row: Cancel | Edit | Save
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Button {
                    id: cancel_customer_button
                    objectName: "cancel_customer_button"
                    text: "Cancel"
                    hoverEnabled: true
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 36
                    onClicked: newCustomerForm.cancelRequested()

                    contentItem: Text {
                        text: cancel_customer_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: newCustomerForm.buttonFontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: cancel_customer_button.down ? palette.dangerPress
                              : cancel_customer_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }

                Button {
                    id: edit_customer_button
                    objectName: "edit_customer_button"
                    text: "Edit"
                    hoverEnabled: true
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 36
                    onClicked: newCustomerForm.editRequested()

                    contentItem: Text {
                        text: edit_customer_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: newCustomerForm.buttonFontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: edit_customer_button.down ? palette.accentPress
                              : edit_customer_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }

                Button {
                    id: save_customer_button
                    objectName: "save_customer_button"
                    text: "Save"
                    hoverEnabled: true
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 36
                    onClicked: newCustomerForm.saveRequested()

                    contentItem: Text {
                        text: save_customer_button.text
                        anchors.centerIn: parent
                        color: palette.buttonText
                        font.pixelSize: newCustomerForm.buttonFontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: save_customer_button.down ? palette.successPress
                              : save_customer_button.hovered ? palette.successHover
                              : palette.success
                    }
                }
            }
        }
    }
}
