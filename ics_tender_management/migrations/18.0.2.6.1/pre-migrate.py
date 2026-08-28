from odoo.tools import sql


def migrate(cr, version):
    """Add etimad_financial_fees and etimad_total_fees columns to ics_tender."""
    if not sql.column_exists(cr, 'ics_tender', 'etimad_financial_fees'):
        cr.execute("""
            ALTER TABLE ics_tender
            ADD COLUMN etimad_financial_fees double precision DEFAULT 0.0
        """)
    if not sql.column_exists(cr, 'ics_tender', 'etimad_total_fees'):
        cr.execute("""
            ALTER TABLE ics_tender
            ADD COLUMN etimad_total_fees double precision DEFAULT 0.0
        """)
