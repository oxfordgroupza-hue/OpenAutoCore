import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: cmenuFrame
    objectName: "cmenu_frame"
    width: 60
    color: menuBg
    radius: 5
    clip: true

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

    // Text and menu colors (mirrors QSS)
    property color textColor: "#FFFFFF"
    property color menuBg: "#4F6D7A" // #4F6D7A
    property color menuHover:"#314455"
    property color menuPress:"#22313F"
    property color quitBg:   "#C62828"
    property color quitHover:"#a72222"

    // Collapsed/expanded behavior – labels show only when expanded
    property int  collapsedWidth: 60
    property bool expanded: width > collapsedWidth + 10

    // Row sizing
    property int buttonHeight: 50
    property int buttonIconSize: 45

    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 1
        topPadding: 30
        spacing: 50

        // --- Repair Orders ---
        Button {
            id: repair_orders_button
            objectName: "repair_orders_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "RO's"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/repair_orders.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: repair_orders_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4




                color: repair_orders_button.down ? cmenuFrame.menuPress
                      : repair_orders_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Customers ---
        Button {
            id: customers_button
            objectName: "customers_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Customers"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/customers.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: customers_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: customers_button.down ? cmenuFrame.menuPress
                      : customers_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Vehicles ---
        Button {
            id: vehicles_button
            objectName: "vehicles_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Vehicles"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/vehicles.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: vehicles_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: vehicles_button.down ? cmenuFrame.menuPress
                      : vehicles_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Messages ---
        Button {
            id: messaging_button
            objectName: "messaging_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Messages"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/messaging.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: messaging_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: messaging_button.down ? cmenuFrame.menuPress
                      : messaging_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Schedule ---
        Button {
            id: scheduling_button
            objectName: "scheduling_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Schedule"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/schedule.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: scheduling_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: scheduling_button.down ? cmenuFrame.menuPress
                      : scheduling_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Analytics ---
        Button {
            id: analytics_button
            objectName: "analytics_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Analytics"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/analytics.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: analytics_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: analytics_button.down ? cmenuFrame.menuPress
                      : analytics_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Settings ---
        Button {
            id: settings_button
            objectName: "settings_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Settings"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/settings.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: settings_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: settings_button.down ? cmenuFrame.menuPress
                      : settings_button.hovered ? cmenuFrame.menuHover
                      : cmenuFrame.menuBg
            }
        }

        // --- Quit ---
        Button {
            id: quit_button
            objectName: "quit_button"
            width: contentColumn.width
            height: cmenuFrame.buttonHeight
            text: "Quit"
            hoverEnabled: true

            contentItem: Row {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                Image {
                    source: Qt.resolvedUrl("../theme/cmenu_icons/power.svg")
                    width: cmenuFrame.buttonIconSize
                    height: cmenuFrame.buttonIconSize
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    visible: source !== ""
                }

                Text {
                    text: quit_button.text
                    anchors.verticalCenter: parent.verticalCenter
                    color: cmenuFrame.textColor
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                    visible: cmenuFrame.expanded
                    elide: Text.ElideRight
                }
            }

            background: Rectangle {
                anchors.fill: parent
                radius: 4
                color: quit_button.down ? cmenuFrame.quitHover
                      : quit_button.hovered ? cmenuFrame.quitHover
                      : cmenuFrame.quitBg
            }
        }
    }
}

