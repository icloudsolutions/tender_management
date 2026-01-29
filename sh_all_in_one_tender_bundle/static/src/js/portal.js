/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.sh_rfq_portal = publicWidget.Widget.extend({
    selector: '#rfq_content,#quote_content',
    events: {
        'click .cancel_2': '_onClickCancelBid',
        'click .btn_cancel_bid_new_modal':'_onClickYesButton',
        'click .cancel_and_create_new':'_onClickCancelUpdated'
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    /*Click method of cancel bid button to open bootstrap cancel modal*/
    _onClickCancelBid: function (ev) {
        ev.preventDefault();
        $('.cancel_bid_update').modal('show');
    },
    /**
     * @private
     */
    /*Click method of cancel bid button to open bootstrap cancel modal*/
    _onClickCancelUpdated: function (ev) {
        ev.preventDefault();
        $('.cancel_bid_new').modal('show');
    },
    /**
     * @private
     */
    /*Click method of cancel old rfq and create new from bootstrap modal*/
    _onClickYesButton: function (ev) {
        ev.preventDefault();
        return jsonrpc('/rfq/cancel/new', { order_id: $('#order_id').val() }).then((data) => {
            window.location.href = data.url;
        });
    },
});
