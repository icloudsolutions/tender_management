{
    'name': 'ICS SMB Management',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'SMB Division workflow: Sales, Credit Control, Logistics, Collection (SMB-SOP-1)',
    'description': """
ICS SMB Management - SMB-SOP-1 Compliance
=========================================

Implements the SMB Division Standard Operating Procedure for:
- Sales: RFQ → Quotation → Send to Credit Control → Handle approved/rejected P.O.
- Credit Control: Review P.O. by payment history & credit limit → Approve or Reject
- Logistics: Use standard Delivery Orders and Invoicing (delivered quantities)
- Collection: Statement of Account, follow-up, escalation to Sales

Features:
- Credit approval workflow on Sale Orders (sent_to_credit → approved/rejected)
- Credit Control group with Approve/Reject actions
- Critical order flag for logistics coordination
- Optional: integrate with ics_tender_management for orders from won tenders
    """,
    'author': 'iCloud Solutions',
    'website': 'https://icloud-solutions.net',
    'license': 'OPL-1',
    'depends': [
        'base',
        'sale_management',
        'stock',
        'account',
        'crm',
        'sale_crm',
        'project',
    ],
    'data': [
        'security/ics_smb_security.xml',
        'security/ir.model.access.csv',
        'data/smb_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/smb_project_task_template_views.xml',
        'views/smb_credit_reject_reason_views.xml',
        'views/smb_menus.xml',
        'views/crm_lead_views.xml',
        'views/project_project_views.xml',
        'wizard/smb_credit_reject_wizard_views.xml',
        'wizard/smb_create_project_wizard_views.xml',
        'data/smb_project_task_template_data.xml',
        'data/smb_credit_reject_reason_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ics_smb_management/static/src/scss/smb_dashboard.scss',
            'ics_smb_management/static/src/js/smb_dashboard.js',
            'ics_smb_management/static/src/xml/smb_dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 800.00,
    'currency': "EUR",
}
