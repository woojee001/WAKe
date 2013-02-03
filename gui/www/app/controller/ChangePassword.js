Ext.define('WAKe.controller.ChangePassword', {
    extend: 'Ext.app.Controller',
    
    views: [
        'ChangePassword',
    ],
    
    init: function() {
        this.control({
            'button[action=change-password]': {
                click: function(){
                    var form = Ext.getCmp('change-password-form').getForm();
                    if (form.isValid()){
                        form.submit({
                            url: 'changeDefaultPassword',
                            success: function(form, action) {
                                console.dir(action);
                                if(action.result.duplicate || !action.result.msg){
                                    window.location = '/';
                                }
                                else{
                                    Ext.Msg.show({
                                        title:'NO MATCH',
                                        buttons: Ext.Msg.YESNO,
                                        msg: action.result.msg,
                                        icon: Ext.Msg.WARNING,
                                        fn: confirmDuplicate
                                   });
                                }
                            },
                            failure: function(form, action) {
                                form.reset();
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