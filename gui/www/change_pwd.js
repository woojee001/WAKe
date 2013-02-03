Ext.application({
    name: 'WAKe',
    appFolder: 'app',
    requires: ['Ext.container.Viewport'],
    
    controllers: [
        'Header',
        'Footer',
        'ChangePassword',
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [
                {
                    xtype: 'wake-header',
                    id: 'wake-header'
                },
                {
                    xtype: 'wake-change-password',
                    id: 'wake-change-password'
                },
                {
                    xtype: 'wake-footer',
                    id: 'wake-footer'
                },
            ]
        });
    }
});