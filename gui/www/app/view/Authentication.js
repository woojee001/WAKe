Ext.define('WAKe.view.Authentication.Form.Username', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.username',
    
    id: 'username',
    name: 'username',
    fieldLabel: 'Username'
});

Ext.define('WAKe.view.Authentication.Form.Password', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.password',
    
    id: 'password',
    name: 'password',
    fieldLabel: 'Password',
    inputType: 'password'
});

Ext.define('WAKe.view.Authentication.Form.Button', {
    extend: 'Ext.button.Button',
    alias: 'widget.log-in',
    
    action: 'login',
    
    text: 'Log in',
    width: 70
});

Ext.define('WAKe.view.Authentication.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.auth-form',
    
    region: 'center',
    padding: '25 10 10 10',
    border: false,
    
    items: [
        {
            xtype: 'username'
        },
        {
            xtype: 'password'
        }
    ],
    
    buttons: [
        {
            xtype: 'log-in'
        }
    ]
});

Ext.define('WAKe.view.Authentication.Logo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.logo',
    
    region: 'west',
    split: true,
    width: 150,
    
    border: false
});

Ext.define('WAKe.view.Authentication', {
    extend: 'Ext.window.Window',
    alias: 'widget.wake-authentication',
    
    region: 'center',
    height: 170,
    width: 450,
    autoShow: true,
    closable: false,
    resizable: false,
    layout: 'border',
    
    padding: 6,
    bodyStyle: 'background-color: #FFFFFF',
    
    title: 'Access WAKe administration interface',
    
    items: [
        {
            xtype: 'logo'
        },
        {
            xtype: 'auth-form'
        }
    ]
});