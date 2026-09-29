import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 720
    height: 520
    minimumWidth: 420
    minimumHeight: 340
    title: "UjwalOS Phone Panel"
    Dialog {
        id: confirmation
        objectName: "pairingConfirmation"
        property string deviceId: ""
        property string deviceName: ""
        anchors.centerIn: parent
        width: Math.min(window.width - 32, 440)
        implicitHeight: Math.min(window.height - 32, 300)
        modal: true
        title: "Revoke pairing?"
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: phone.act(deviceId, "unpair")
        contentItem: ScrollView {
            implicitHeight: Math.min(consentText.implicitHeight, window.height - 160)
            contentWidth: availableWidth
            clip: true
            Label {
                id: consentText
                width: confirmation.width - confirmation.leftPadding - confirmation.rightPadding
                text: confirmation.deviceName
                    + "\n\nRemove this computer's trust for this device, including when it is offline?"
                textFormat: Text.PlainText
                wrapMode: Text.Wrap
            }
        }
    }
    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            Label { text: "Phone Panel"; font.pixelSize: 22; Layout.fillWidth: true }
            Button {
                text: "Refresh"
                icon.name: "view-refresh"
                enabled: !phone.busy && !confirmation.visible
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
        Button {
            objectName: "openKdeConnect"
            text: "Open KDE Connect"
            icon.name: "kdeconnect"
            enabled: !phone.busy && !confirmation.visible
            onClicked: phone.openSettings()
        }
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
                    Label {
                        visible: !!modelData.requested || !!modelData.incoming
                        text: modelData.incoming ? "Incoming request: review in KDE Connect"
                                                 : "Pairing request pending"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                    Label {
                        visible: !!modelData.verification
                        text: "Verification code: " + (modelData.verification || "")
                        textFormat: Text.PlainText
                        wrapMode: Text.WrapAnywhere
                        Layout.fillWidth: true
                    }
                    Button {
                        text: "Unpair"
                        visible: !!modelData.paired
                        icon.name: "edit-delete"
                        enabled: !phone.busy && !confirmation.visible && !!modelData.id
                            && !!modelData.paired
                        onClicked: {
                            confirmation.deviceId = modelData.id
                            confirmation.deviceName = modelData.name
                            confirmation.open()
                        }
                    }
                }
                Accessible.name: modelData.name
            }
        }
    }
}
