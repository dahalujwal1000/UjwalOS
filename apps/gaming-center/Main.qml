import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 840
    height: 600
    minimumWidth: 560
    minimumHeight: 500
    title: "UjwalOS Gaming Center"
    property int selected: -1

    function edit(index) {
        selected = index
        const row = index >= 0 ? center.rows[index] : null
        nameField.text = row ? row.name : ""
        mode.checked = row ? row.gamemode : false
        overlay.checked = row ? row.overlay : false
    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            Label { text: "Gaming Center"; font.pixelSize: 22; Layout.fillWidth: true }
            ToolButton {
                icon.name: "view-refresh"
                text: "Refresh"
                display: center.hasIcon(icon.name) ? AbstractButton.IconOnly : AbstractButton.TextOnly
                Accessible.name: text
                ToolTip.visible: hovered
                ToolTip.text: text
                onClicked: center.refresh()
            }
        }
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        contentWidth: availableWidth
        ColumnLayout {
            width: parent.width
            spacing: 16
            Label {
                text: center.toolStatus
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            Label {
                text: center.error
                visible: text.length > 0
                wrapMode: Text.WrapAnywhere
                Layout.fillWidth: true
                color: "#b83a32"
            }
            RowLayout {
                Layout.fillWidth: true
                ComboBox {
                    id: profileList
                    objectName: "profileList"
                    Layout.fillWidth: true
                    model: center.rows
                    textRole: "name"
                    currentIndex: window.selected
                    displayText: window.selected < 0 ? "New profile" : currentText
                    Accessible.name: "Profile"
                    onActivated: window.edit(currentIndex)
                }
                ToolButton {
                    text: "New profile"
                    icon.name: "list-add"
                    display: center.hasIcon(icon.name) ? AbstractButton.IconOnly : AbstractButton.TextOnly
                    Accessible.name: text
                    ToolTip.visible: hovered
                    ToolTip.text: text
                    enabled: center.canEdit
                    onClicked: window.edit(-1)
                }
            }
            Label { text: "Game name" }
            TextField {
                id: nameField
                objectName: "nameField"
                Layout.fillWidth: true
                maximumLength: 120
                enabled: center.canEdit
                Accessible.name: "Game name"
            }
            Label { text: "Requested settings"; font.bold: true }
            CheckBox {
                id: mode
                objectName: "mode"
                text: "GameMode"
                enabled: center.canEdit
            }
            CheckBox {
                id: overlay
                text: "MangoHud overlay"
                enabled: center.canEdit
            }
            Label { text: "Launch options preview" }
            TextField {
                Layout.fillWidth: true
                readOnly: true
                selectByMouse: true
                text: (mode.checked ? "gamemoderun " : "")
                    + (overlay.checked ? "mangohud " : "") + "%command%"
                Accessible.name: "Launch options preview"
            }
            Label { text: "Applied state: not monitored" }
            RowLayout {
                Button {
                    objectName: "saveButton"
                    text: "Save profile"
                    icon.name: "document-save"
                    enabled: center.canEdit && nameField.text.trim().length > 0
                    onClicked: {
                        const index = window.selected < 0 ? center.rows.length : window.selected
                        if (center.save(window.selected, nameField.text, mode.checked, overlay.checked))
                            window.edit(index)
                    }
                }
                Button {
                    text: "Reset settings"
                    icon.name: "edit-undo"
                    enabled: center.canEdit && window.selected >= 0
                    onClicked: {
                        if (center.reset(window.selected)) window.edit(window.selected)
                    }
                }
                ToolButton {
                    text: "Delete profile"
                    icon.name: "edit-delete"
                    display: center.hasIcon(icon.name) ? AbstractButton.IconOnly : AbstractButton.TextOnly
                    Accessible.name: text
                    ToolTip.visible: hovered
                    ToolTip.text: text
                    enabled: center.canEdit && window.selected >= 0
                    onClicked: deletion.open()
                }
            }
        }
    }
    Dialog {
        id: deletion
        title: "Delete profile?"
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: {
            if (center.remove(window.selected)) window.edit(-1)
        }
    }
}
