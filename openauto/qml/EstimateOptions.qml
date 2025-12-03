import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: estimateOptions
    objectName: "estimate_options_form"
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
    signal openRequested()
    signal changeStatusRequested()
    signal duplicateRequested()
    signal deleteRequested()

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
                    text: "Estimate Options"
                    color: estimateOptions.textColor
                    font.pixelSize: 18
                    font.bold: true
                    Layout.fillWidth: true
                }

                Label {
                    text: "Choose what you’d like to do with this estimate."
                    color: estimateOptions.subTextColor
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            // Main actions row
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 10

                // Open RO
                Button {
                    id: open_ro_button
                    objectName: "open_ro_button"
                    text: "Open RO"
                    icon.source: "qrc:/resources/icons3/24x24/cil-folder-open.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: estimateOptions.buttonWidth
                    Layout.preferredHeight: estimateOptions.buttonHeight
                    onClicked: estimateOptions.openRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: open_ro_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: open_ro_button.text
                            color: palette.buttonText || palette.text
                            font: open_ro_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: open_ro_button.down ? palette.successPress
                              : open_ro_button.hovered ? palette.successHover
                              : palette.success
                    }
                }

                // Change status
                Button {
                    id: change_ro_status_button
                    objectName: "change_ro_status_button"
                    text: "Change Status"
                    icon.source: "qrc:/resources/icons3/24x24/cil-list.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: estimateOptions.buttonWidth
                    Layout.preferredHeight: estimateOptions.buttonHeight
                    visible: true
                    onClicked: estimateOptions.changeStatusRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: change_ro_status_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: change_ro_status_button.text
                            color: palette.buttonText || palette.text
                            font: change_ro_status_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: change_ro_status_button.down ? palette.accentPress
                              : change_ro_status_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }

                // Duplicate
                Button {
                    id: duplicate_ro_button
                    objectName: "duplicate_ro_button"
                    text: "Duplicate"
                    icon.source: "qrc:/resources/icons3/24x24/cil-copy.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: estimateOptions.buttonWidth
                    Layout.preferredHeight: estimateOptions.buttonHeight
                    onClicked: estimateOptions.duplicateRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: duplicate_ro_button.icon.source
                            width: 22; height: 22
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: duplicate_ro_button.text
                            color: palette.buttonText || palette.text
                            font: duplicate_ro_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: duplicate_ro_button.down ? palette.accentPress
                              : duplicate_ro_button.hovered ? palette.accentHover
                              : palette.accent
                    }
                }

                // Delete
                Button {
                    id: delete_ro_button
                    objectName: "delete_ro_button"
                    text: "Delete"
                    icon.source: "qrc:/resources/icons3/24x24/cil-trash.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: estimateOptions.buttonWidth
                    Layout.preferredHeight: estimateOptions.buttonHeight
                    onClicked: estimateOptions.deleteRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Image {
                            source: delete_ro_button.icon.source
                            width: 20; height: 20
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: delete_ro_button.text
                            color: palette.buttonText || palette.text
                            font: delete_ro_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: delete_ro_button.down ? palette.dangerPress
                              : delete_ro_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }

                // Cancel
                Button {
                    id: cancel_ro_options_button
                    objectName: "cancel_ro_options_button"
                    text: "Cancel"
                    icon.source: "qrc:/resources/icons3/24x24/cil-exit-to-app.png"
                    font.bold: true
                    font.pixelSize: 14
                    Layout.preferredWidth: estimateOptions.buttonWidth
                    Layout.preferredHeight: estimateOptions.buttonHeight
                    onClicked: estimateOptions.cancelRequested()

                    contentItem: Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Image {
                            source: cancel_ro_options_button.icon.source
                            width: 18; height: 18
                            fillMode: Image.PreserveAspectFit
                            visible: source !== ""
                        }
                        Text {
                            text: cancel_ro_options_button.text
                            color: palette.buttonText || palette.text
                            font: cancel_ro_options_button.font
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: cancel_ro_options_button.down ? palette.dangerPress
                              : cancel_ro_options_button.hovered ? palette.dangerHover
                              : palette.danger
                    }
                }
            }
        }
    }

    focus: true
    Keys.onEscapePressed: cancel_ro_options_button.clicked()
}
