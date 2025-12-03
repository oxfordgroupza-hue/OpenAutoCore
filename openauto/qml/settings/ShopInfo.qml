import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: 1358
    height: 803

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        TabBar {
            id: tabBar
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            currentIndex: 0
            background: Rectangle {
                color: "transparent"
                border.width: 0
            }

            TabButton {
                height: 40
                font.bold: true
                contentItem: Text {
                    text: qsTr("Shop Info")
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignBottom
                }
            }

            TabButton {
                height: 40
                font.bold: true
                contentItem: Text {
                    text: qsTr("Pricing")
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignBottom
                }
            }

            TabButton {
                height: 40
                font.bold: true
                contentItem: Text {
                    text: qsTr("Reviews")
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignBottom
                }
            }
        }

        StackLayout {
            id: stackView
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            anchors.left: parent.left


            GridLayout {
                columns: 4
                rowSpacing: 5
                columnSpacing: 5

                Label {
                    Layout.column: 0 
                    Layout.row: 0
                    text: qsTr("Shop Name: ")
                    font.bold: true
                }

                TextField {
                    id: shopNameField
                    Layout.column: 1
                    Layout.row: 0
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter shop name")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 1
                    text: qsTr("Address: ")
                    font.bold: true
                }
                
                TextField {
                    id: addressField
                    Layout.column: 1
                    Layout.row: 1
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: "Enter Address"
                }

                Label {
                    Layout.column: 0
                    Layout.row: 2
                    text: qsTr("City: ")
                    font.bold: true
                }

                TextField {
                    id: cityField
                    Layout.column: 1
                    Layout.row: 2
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter city")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 3
                    text: qsTr("State: ")
                    font.bold: true
                }

                ComboBox {
                    id: stateComboBox
                    Layout.column: 1
                    Layout.row: 3
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    model: stateModel
                    textRole: "abbreviation"
                    valueRole: "name"
                    delegate: ItemDelegate {
                        width: stateComboBox.width
                        text: abbreviation + " - " + name
                        highlighted: stateComboBox.highlightedIndex === index
                    }
                }

                ListModel {
                    id: stateModel

                    ListElement { abbreviation: "AL"; name: "Alabama" }
                    ListElement { abbreviation: "AK"; name: "Alaska" }
                    ListElement { abbreviation: "AZ"; name: "Arizona" }
                    ListElement { abbreviation: "AR"; name: "Arkansas" }
                    ListElement { abbreviation: "CA"; name: "California" }
                    ListElement { abbreviation: "CO"; name: "Colorado" }
                    ListElement { abbreviation: "CT"; name: "Connecticut" }
                    ListElement { abbreviation: "DE"; name: "Delaware" }
                    ListElement { abbreviation: "FL"; name: "Florida" }
                    ListElement { abbreviation: "GA"; name: "Georgia" }
                    ListElement { abbreviation: "HI"; name: "Hawaii" }
                    ListElement { abbreviation: "ID"; name: "Idaho" }
                    ListElement { abbreviation: "IL"; name: "Illinois" }
                    ListElement { abbreviation: "IN"; name: "Indiana" }
                    ListElement { abbreviation: "IA"; name: "Iowa" }
                    ListElement { abbreviation: "KS"; name: "Kansas" }
                    ListElement { abbreviation: "KY"; name: "Kentucky" }
                    ListElement { abbreviation: "LA"; name: "Louisiana" }
                    ListElement { abbreviation: "ME"; name: "Maine" }
                    ListElement { abbreviation: "MD"; name: "Maryland" }
                    ListElement { abbreviation: "MA"; name: "Massachusetts" }
                    ListElement { abbreviation: "MI"; name: "Michigan" }
                    ListElement { abbreviation: "MN"; name: "Minnesota" }
                    ListElement { abbreviation: "MS"; name: "Mississippi" }
                    ListElement { abbreviation: "MO"; name: "Missouri" }
                    ListElement { abbreviation: "MT"; name: "Montana" }
                    ListElement { abbreviation: "NE"; name: "Nebraska" }
                    ListElement { abbreviation: "NV"; name: "Nevada" }
                    ListElement { abbreviation: "NH"; name: "New Hampshire" }
                    ListElement { abbreviation: "NJ"; name: "New Jersey" }
                    ListElement { abbreviation: "NM"; name: "New Mexico" }
                    ListElement { abbreviation: "NY"; name: "New York" }
                    ListElement { abbreviation: "NC"; name: "North Carolina" }
                    ListElement { abbreviation: "ND"; name: "North Dakota" }
                    ListElement { abbreviation: "OH"; name: "Ohio" }
                    ListElement { abbreviation: "OK"; name: "Oklahoma" }
                    ListElement { abbreviation: "OR"; name: "Oregon" }
                    ListElement { abbreviation: "PA"; name: "Pennsylvania" }
                    ListElement { abbreviation: "RI"; name: "Rhode Island" }
                    ListElement { abbreviation: "SC"; name: "South Carolina" }
                    ListElement { abbreviation: "SD"; name: "South Dakota" }
                    ListElement { abbreviation: "TN"; name: "Tennessee" }
                    ListElement { abbreviation: "TX"; name: "Texas" }
                    ListElement { abbreviation: "UT"; name: "Utah" }
                    ListElement { abbreviation: "VT"; name: "Vermont" }
                    ListElement { abbreviation: "VA"; name: "Virginia" }
                    ListElement { abbreviation: "WA"; name: "Washington" }
                    ListElement { abbreviation: "WV"; name: "West Virginia" }
                    ListElement { abbreviation: "WI"; name: "Wisconsin" }
                    ListElement { abbreviation: "WY"; name: "Wyoming" }

                }

                Label {
                    Layout.column: 0
                    Layout.row: 4
                    text: qsTr("Zip Code: ")
                    font.bold: true
                }

                TextField {
                    id: zipCodeField
                    Layout.column: 1
                    Layout.row: 4
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter zip code")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 5
                    text: qsTr("Phone Number: ")
                    font.bold: true
                }

                TextField {
                    id: phoneNumberField
                    Layout.column: 1
                    Layout.row: 5
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter phone number")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 6
                    text: qsTr("Email: ")
                    font.bold: true
                }

                TextField {
                    id: emailField
                    Layout.column: 1
                    Layout.row: 6
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter email address")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 7
                    text: qsTr("Website: ")
                    font.bold: true
                }

                TextField {
                    id: websiteField
                    Layout.column: 1
                    Layout.row: 7
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter website URL")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 8
                    text: qsTr("Facility Id # ")
                    font.bold: true
                }

                TextField {
                    id: facilityIdField
                    Layout.column: 1
                    Layout.row: 8
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter Facility Id #")
                }

                Label {
                    Layout.column: 0
                    Layout.row: 9
                    text: qsTr("License # ")
                    font.bold: true
                }

                TextField {
                    id: licenseField
                    Layout.column: 1
                    Layout.row: 9
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter License #")
                }

                CheckBox {
                    id: warrantyDistanceCheckBox
                    Layout.column: 2
                    Layout.row: 0
                    text: qsTr("Warranty Distance")
                    Layout.preferredHeight: 40
                    font.bold: true
                    checked: true
                }

                TextField {
                    id: warrantyDistanceField
                    Layout.column: 3
                    Layout.row: 0
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter Warranty Distance")
                    visible: warrantyDistanceCheckBox.checked
                }

                CheckBox {
                    id: warrantyTimeCheckBox
                    text: qsTr("Warranty Time")
                    Layout.column: 2
                    Layout.row: 1
                    Layout.preferredHeight: 40
                    font.bold: true
                    checked: true
                }

                TextField {
                    Layout.column: 3
                    Layout.row: 1
                    id: warrantyTimeField
                    Layout.preferredHeight: 40
                    Layout.preferredWidth: 400
                    Layout.minimumWidth: 400
                    placeholderText: qsTr("Enter Warranty Time")
                    visible: warrantyTimeCheckBox.checked
                }
            }
        }

        StackLayout {
            id: shopLogoStackView
            // rows: 1
            // columns: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            anchors.right: parent.right
            anchors.top: parent.top

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignCenter
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 40
                spacing: 10

                Image {
                    id: shopLogoImage
                    source: "qrc:/resources/OpenAuto_Icons_48x48_dark_light/mainwindow_icon/dark_theme_logo.png"
                    fillMode: Image.PreserveAspectFit
                    anchors.centerIn: parent
                    Layout.maximumHeight: 120
                    Layout.maximumWidth: 120
                    onStatusChanged: {
                        if (status === Image.Error) {
                            // Fallback to local file path if the qrc resource is unavailable
                            source = Qt.resolvedUrl("../theme/OpenAuto_Icons_48x48_dark_light/mainwindow_icon/dark_theme_logo.png")
                        }
                    }
                }

                Button {
                    id: uploadLogoButton
                    spacing: 10
                    text: qsTr("Upload Shop Logo")
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 40
                    // anchors.centerIn: parent
                }
            }                    
        }

        StackLayout {
            id: warrantyDisclaimerStackView
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            // anchors.left: parent.left
            // anchors.bottom: parent.bottom
            // anchors.right: parent.right


            RowLayout {
                Layout.fillWidth: true
                // Layout.fillHeight: true
                Layout.minimumHeight: 400
                Layout.preferredHeight: 300

                // Disclaimer column
                ColumnLayout {
                    Layout.fillWidth: true
                    // Layout.fillHeight: true
                    Layout.maximumWidth: 650
                    // Layout.maximumHeight: 300
                    // Layout.preferredHeight: 400
                    spacing: 5

                    Label {
                        text: qsTr("Approval Disclaimer")
                        font.bold: true
                        font.pointSize: 16
                        Layout.alignment: Qt.AlignHCenter
                    }

                    TextArea {
                        id: disclaimerTextArea
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.alignment: Qt.AlignCenter
                        font.pixelSize: 18
                        readOnly: false
                        placeholderText: qsTr("All products and services are provided 'as is' without any warranties of any kind, either express or implied. We disclaim all warranties, including but not limited to implied warranties of merchantability and fitness for a particular purpose. In no event shall we be liable for any damages arising out of or in connection with the use or inability to use our products or services.")
                    }
                }

                // Return policy column
                ColumnLayout {
                    Layout.fillWidth: true
                    // Layout.fillHeight: true
                    Layout.maximumWidth: 650
                    // Layout.maximumHeight: 300
                    // Layout.preferredHeight: 400
                    spacing: 5

                    Label {
                        text: qsTr("Warranty Policy")
                        font.bold: true
                        font.pointSize: 16
                        Layout.alignment: Qt.AlignHCenter
                    }

                    TextArea {
                        id: returnPolicyTextArea
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.alignment: Qt.AlignCenter
                        font.pixelSize: 18
                        readOnly: false
                        placeholderText: qsTr("Returns are accepted within 30 days of purchase with a valid receipt. Items must be in their original condition and packaging. Some restrictions may apply for certain products. Please contact customer service for more details.")
                    }
                }


            }
        }

    }
}
}