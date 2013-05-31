openerp.account_streamline = function(instance)
{
    var _t = instance.web._t;
    var _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.web.account_streamline = instance.web.account_streamline || {};
    instance.web.views.add('tree_account_streamline_reconciliation', 'instance.web.account_streamline.ReconcileListView');

    instance.web.account_streamline.ReconcileListView = instance.web.ListView.extend({
        init: function()
        {
            this._super.apply(this, arguments);
            var self = this;
            this.current_partner = null;
            this.on('record_selected', this, function() {
                if (self.get_selected_ids().length >= 2) {
                    self.$(".oe_account_streamline_recon_reconcile").removeAttr("disabled");
                    console.log("Button Clickable");
                } else {
                    self.$(".oe_account_streamline_recon_reconcile").attr("disabled", "");
                    console.log("Button Unclickable");
                }
            });
        },
        load_list: function()
        {
            var self = this;
            var tmp = this._super.apply(this, arguments);
            this.$el.prepend(QWeb.render("AccountStreamlineReconciliation", {widget: this}));
            this.$(".oe_account_streamline_recon_reconcile").click(function() {
                console.log("RECON RECONCILE");
                self.reconcile();
            });
            this.$(".oe_account_streamline_search_wizard").click(function() {
                self.call_search_wizard();
            });
            return tmp;
        },
        call_search_wizard: function()
        {
            var self = this;
            new instance.web.Model("ir.model.data").call("get_object_reference", ["account_streamline", "action_view_account_streamline_filter"]).then(function(result)
            {
                return self.rpc("/web/action/load", {
                    action_id: result[1]
                }).done(function (result) {
                    result.flags = result.flags || {};
                    result.flags.new_window = true;
                    return self.do_action(result, {
                        on_close: function () {
                            self.do_search(self.last_domain, self.last_context, self.last_group_by);
                        }
                    });
                });
            });
        },
        reconcile: function()
        {
            var self = this;
            var ids = this.get_selected_ids();

            new instance.web.Model("ir.model.data").call("get_object_reference", ["account", "action_view_account_move_line_reconcile"]).then(function(result)
            {
                var additional_context = _.extend({
                    active_id: ids[0],
                    active_ids: ids,
                    active_model: self.model
                });
                return self.rpc("/web/action/load", {
                    action_id: result[1],
                    context: additional_context
                }).done(function (result) {
                    result.context = instance.web.pyeval.eval('contexts', [result.context, additional_context]);
                    result.flags = result.flags || {};
                    result.flags.new_window = true;
                    return self.do_action(result, {
                        on_close: function () {
                            self.do_search(self.last_domain, self.last_context, self.last_group_by);
                        }
                    });
                });
            });
        },
        do_search: function(domain, context, group_by)
        {
            var self = this;
            var advanced_filter_mod = new instance.web.Model("account.streamline.advanced_filter", context, domain);
            
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            self.old_search = _.bind(this._super, this);
            return advanced_filter_mod.call("get_elements_filtered", []).then(function(result)
            {
                var new_domain
                
                if (result)
                    new_domain = new instance.web.CompoundDomain(self.last_domain, [["id", "in", result]]);
                else
                    new_domain = self.last_domain;
                return self.old_search(new_domain, self.last_context, self.last_group_by);
            });
        },
        do_select: function (ids, records)
        {
            if (ids.length != 0)
            {
                this.trigger('record_selected');
                this._super.apply(this, arguments);
            }
        },
    });
};
