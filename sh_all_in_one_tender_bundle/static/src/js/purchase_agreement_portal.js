/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.sh_po_tender_portal = publicWidget.Widget.extend({
    selector: '#tender_content,#tender_tr',
    events: {
        'click #btn_add_bid_form': '_onClickAddBid',
        'click .btn_add_bid': '_onClickAddBidList',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    /*Click method of add/update bid and create new rfq*/
    _onClickAddBid: function (ev) {
        ev.preventDefault();
        return jsonrpc('/rfq/create', { tender_id: ev.target.dataset.id }).then((data) => {
            window.location.href = data.url;
        });
    },
    /**
     * @private
     */
    /*Click method of add/update bid and create new rfq(tender portal list view)*/
    _onClickAddBidList: function (ev) {
        ev.preventDefault();
        var $el = $(ev.target).parents("tr").find("#tender_id").attr("value");
        var tender_id = parseInt($el);
        return jsonrpc('/rfq/create', { tender_id: tender_id }).then((data) => {
            window.location.href = data.url;
        });
    },
});
