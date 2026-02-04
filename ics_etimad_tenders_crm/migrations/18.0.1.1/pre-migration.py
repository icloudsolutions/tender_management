# -*- coding: utf-8 -*-
"""
Migration script to rename tender_type to etimad_tender_type
Fixes semantic confusion between Etimad classification and ICS vendor selection strategy
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Rename column tender_type to etimad_tender_type in ics_etimad_tender"""
    # Check if the old column exists before renaming
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='ics_etimad_tender' 
        AND column_name='tender_type'
    """)
    
    if cr.fetchone():
        # Rename the column
        cr.execute("""
            ALTER TABLE ics_etimad_tender 
            RENAME COLUMN tender_type TO etimad_tender_type
        """)
        print("✓ Successfully renamed column: tender_type → etimad_tender_type")
    else:
        print("ℹ Column 'tender_type' not found, skipping migration (already renamed or fresh install)")
