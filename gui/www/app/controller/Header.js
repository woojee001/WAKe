Ext.define('WAKe.controller.Header', {
    extend: 'Ext.app.Controller',
    
    views: [
    	'Header',
    ],
    
    init: function() {
        this.control({
            'wake-header': {
                render: this.getHeaderHtml
            }
        });
    },

    getHeaderHtml: function() {
        Ext.Ajax.request({
		    url: 'getPageHeader',
		    method: 'POST',
		    success: function(response, opts) {
		        var data = Ext.decode(response.responseText);
		        Ext.getCmp('wake-header').update(data['html']);
		    }
		});
    }
});