import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 720
    height: 520
    minimumWidth: 420
    minimumHeight: 340
    title: "UjwalOS Phone Panel"
    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            Label { text: "Phone Panel"; font.pixelSize: 22; Layout.fillWidth: true }
            Button {
                text: "Refresh"
                icon.name: "view-refresh"
                enabled: !phone.busy
                onClicked: phone.refresh()
            }
        }
    }
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12
        Label {
            text: phone.message
            textFormat: Text.PlainText
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        BusyIndicator { running: phone.busy; visible: running }
        Label { text: "Devices at last refresh"; font.bold: true }
        ListView {
            id: devices
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: phone.devices
            clip: true
            spacing: 12
            ScrollBar.vertical: ScrollBar {}
            delegate: ItemDelegate {
                required property var modelData
                width: devices.width
                height: details.implicitHeight + 24
                contentItem: ColumnLayout {
                    id: details
                    Label {
                        text: modelData.name
                        textFormat: Text.PlainText
                        wrapMode: Text.WrapAnywhere
                        Layout.fillWidth: true
                        font.bold: true
                    }
                    Label {
                        text: (modelData.paired ? "Paired" : "Not paired")
                            + " | " + (modelData.reachable ? "Reachable" : "Offline")
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                    Label { text: "Battery: " + modelData.battery }
                }
                Accessible.name: modelData.name
            }
        }
    }
}
