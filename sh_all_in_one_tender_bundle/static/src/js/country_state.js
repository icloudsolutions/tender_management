/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.js_cls_sh_vendor_signup_country_state_wrapper = publicWidget.Widget.extend({
    selector: ".js_cls_sh_vendor_signup_country_state_wrapper",
    events: {
        'change select[name="country_id"]': '_onChangeCountry',
    },

    /**
     * @private
     * @param {Event} ev
     */
    _onChangeCountry: function (ev) {
        var self = this;
        if (!$(ev.currentTarget).val()){
            return;
        }
        var url = "/vendor-sign-up/" + $(ev.currentTarget).val()

        jsonrpc(url).then(function (data) {
            // populate states and display
            var selectStates = self.$el.find("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
            if (selectStates.data('init') === 0 || selectStates.find('option').length === 1) {
                if (data.states.length || data.state_required) {
                    selectStates.html('');
                    jQuery.each(data.states, function (key, value) {
                        var opt = $('<option>').text(value[1])
                            .attr('value', value[0])
                            .attr('data-code', value[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                } else {
                    selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            } else {
                selectStates.data('init', 0);
            }
        });		
        

    },
});
