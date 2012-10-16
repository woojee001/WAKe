Ext.application({
    name: 'WAKe',
    appFolder: 'app',
    requires: ['Ext.container.Viewport'],
    
    controllers: [
    	'Header',
    	'Authentication',
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
                    xtype: 'wake-authentication',
                    id: 'wake-authentication'
                }
            ]
        });
    }
});