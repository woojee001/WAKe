Ext.application({
    name: 'WAKe',
    appFolder: 'app',
    requires: ['Ext.container.Viewport'],
    
    controllers: [
        'Header',
        'Footer',
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
                    xtype: 'panel',
                },
                {
                    xtype: 'wake-footer',
                    id: 'wake-footer'
                },
            ]
        });
    }
});