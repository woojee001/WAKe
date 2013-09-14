Ext.Loader.setConfig({
    enabled : true,
});

Ext.application({

    name: 'WAKe',
    
    appFolder: 'app',
    
    controllers: [
    	'Authentication'
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [
            	{
			        xtype: 'box',
			        id: 'wake-header',
			        region: 'north',
			        html: [
			            '<table id="header-table">',
                            '<tr>',
                                '<td id="header-cell">',
                                    '<span id="header-pgm-name">Web Application Keeper</span>',
                                    ' - Open source Web Application Firewall',
                                '</td>',
                            '</tr>',
                        '</table>'
                    ]
			    },
            	{
                    xtype: 'wake-authentication',
                    id: 'wake-authentication',
                    region: 'center'
                },
                {
                    xtype: 'box',
                    id: 'wake-footer',
                    region: 'south',
                    html: [
                        '<div id="footer">',
                            '<div id="powered-by">',
                                'Powered by <a href="https://github.com/acrozatier">Aur&eacute;lien CROZATIER</a>',
                            '</div>',
                        '</div>'
                    ]
                },
            ]
        });
    }
});