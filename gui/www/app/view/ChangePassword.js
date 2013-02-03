
Ext.define('WAKe.view.ChangePassword.Form.Password', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.password',
    
    inputType: 'password',
    
    allowBlank: false
});

Ext.define('WAKe.view.ChangePassword.Form.Button', {
    extend: 'Ext.button.Button',
    alias: 'widget.change-password',
    
    action: 'change-password',
    
    text: 'Change password',
    padding: '5 10 5 10',
    iconCls: 'change-pwd',
    
    formBind: true,
    enabled: false
});

Ext.define('WAKe.view.ChangePassword.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.change-password-form',
    id: 'change-password-form',
    
    region: 'center',
    padding: '25 10 10 10',
    border: false,
    monitorValid: true,
    defaults: {
        labelWidth: 170
    },
    
    items: [
        {
            xtype: 'password',
            id: 'password1',
            name: 'password1',
            fieldLabel: 'New password'
        },
        {
            xtype: 'password',
            id: 'password2',
            name: 'password2',
            fieldLabel: 'Re-type new password'
        }
    ],
    
    buttons: [
        {
            xtype: 'change-password'
        }
    ]
});

Ext.define('WAKe.view.ChangePassword', {
    extend: 'Ext.window.Window',
    alias: 'widget.wake-change-password',
    
    region: 'center',
    height: 170,
    width: 350,
    autoShow: true,
    closable: false,
    resizable: false,
    draggable: false,
    layout: 'border',
    
    padding: 6,
    bodyStyle: 'background-color: #FFFFFF',
    
    title: 'Chande WAKe administrator default password',
    
    items: [
        {
            xtype: 'change-password-form'
        }
    ]
});