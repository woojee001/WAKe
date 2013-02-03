function confirmDuplicate(btn){
    console.dir(btn);
    if(btn == 'yes'){
        Ext.Ajax.request({
            url: 'confirmDuplicate',
            success: function(response){
                window.location = '/';
            },
            failure: function(response){
                alert('ERROR')
            }
        });
    }
}

Ext.define('WAKe.controller.Authentication', {
    extend: 'Ext.app.Controller',
    
    views: [
    	'Authentication',
    ],
    
    init: function() {
        this.control({
            'button[action=login]': {
                click: function(){
                    var form = Ext.getCmp('auth-form').getForm();
                    if (form.isValid()){
                        form.submit({
                            url: 'connect',
                            success: function(form, action) {
                                console.dir(action);
                                if(!action.result.duplicate){
                                    window.location = '/';
                                }
                                else{
                                    Ext.Msg.show({
                                        title:'DUPLICATE SESSION',
                                        buttons: Ext.Msg.YESNO,
                                        msg: action.result.msg,
                                        icon: Ext.Msg.WARNING,
                                        fn: confirmDuplicate
                                   });
                                }
                            },
                            failure: function(form, action) {
                                switch (action.failureType) {
                                    case Ext.form.action.Action.CLIENT_INVALID:
                                        Ext.Msg.alert('Failure', 'Form fields may not be submitted with invalid values');
                                        break;
                                    case Ext.form.action.Action.CONNECT_FAILURE:
                                        Ext.Msg.show({
                                            title:'ERROR',
                                            buttons: Ext.Msg.OK,
                                            msg: 'Could not reach web server !',
                                            icon: Ext.Msg.ERROR
                                        });
                                        break;
                                    case Ext.form.action.Action.SERVER_INVALID:
                                        Ext.Msg.show({
                                            title:'ERROR',
                                            buttons: Ext.Msg.OK,
                                            msg: action.result.msg,
                                            icon: Ext.Msg.ERROR
                                        });
                                        break;
                               }
                            }
                        });
                    }
                }
            }
        });
    }
});