# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """
    Odoo 18: 'tree' is no longer a valid view type in act_window actions.
    Some databases may still have stale actions created in earlier installs/upgrades.

    This hook normalizes any remaining 'tree' occurrences to 'list' so menus/actions
    don't crash the web client.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Normalize ir.actions.act_window.view_mode (table name: ir_act_window)
    env.cr.execute(
        """
        UPDATE ir_act_window
           SET view_mode = REPLACE(view_mode, 'tree', 'list')
         WHERE view_mode ILIKE '%tree%';
        """
    )

    # Normalize ir.act_window.view (per-view mode)
    env.cr.execute(
        """
        UPDATE ir_act_window_view
           SET view_mode = 'list'
         WHERE view_mode = 'tree';
        """
    )
