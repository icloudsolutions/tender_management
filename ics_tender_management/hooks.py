# -*- coding: utf-8 -*-
from odoo import api

def post_init_hook(env):
    """
    Odoo 18: Normalize any remaining 'tree' occurrences to 'list' safely.
    """

    # Fonction utilitaire pour vérifier l'existence d'une table
    def table_exists(table_name):
        env.cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                 WHERE table_name = %s
            )
        """, (table_name,))
        return env.cr.fetchone()[0]

    if table_exists('ir.actions.act_window'):
        env.cr.execute("""
            UPDATE "ir.actions.act_window"
               SET view_mode = REPLACE(view_mode, 'tree', 'list')
             WHERE view_mode ILIKE '%tree%';
        """)

    if table_exists('ir.actions.act_window.view'):
        env.cr.execute("""
            UPDATE "ir.actions.act_window.view"
               SET view_mode = 'list'
             WHERE view_mode = 'tree';
        """)