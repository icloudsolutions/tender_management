{
    'name': 'ICS Tender Management',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Complete Tender Management System for Saudi Etimad Portal Integration',
    'description': """
        Saudi Tender Management Workflow (ICS Standard)
        ================================================

        Complete tender lifecycle management:

        Phase 1: Lead Creation & Registration
        - Integration with Etimad tender scraper
        - Automatic lead creation from portal.etimad.sa
        - Tender ID and category tracking

        Phase 2: Technical & Financial Study
        - BoQ (Bill of Quantities) analysis and upload
        - Vendor RFQ management via Purchase Agreements
        - Multi-vendor quotation comparison
        - Side-by-side vendor offer analysis

        Phase 3: Quotation & Submission
        - Final quotation generation with margin calculation
        - Kanban stage tracking: Draft → Technical Study → Financial Study →
          Submitted → Under Evaluation → Won/Lost
        - Automated submission workflow

        Phase 4: Execution
        - One-click project creation from won tenders
        - Seamless integration with Odoo Project Management
        - Complete tender history and documentation

        Key Features:
        - Full CRM integration
        - Purchase Agreement (Call for Tenders) workflow
        - Vendor comparison and selection tools
        - Automated quotation generation
        - Project kickoff automation
        - Complete audit trail
    """,
    'author': 'iCloud Solutions',
    'website': 'https://icloud-solutions.net',
    'maintainer': 'iCloud Solutions',
    'support': 'contact@icloud-solutions.net',
    'license': 'OPL-1',
    'price': 2500.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'crm',
        'sale_management',
        'purchase',
        'purchase_requisition',
        'project',
        'ics_etimad_tenders_crm',
    ],
    'data': [
        'security/tender_security.xml',
        'security/ir.model.access.csv',
        'data/tender_sequence.xml',
        'data/tender_stage_data.xml',
        'views/tender_views.xml',
        'views/tender_boq_views.xml',
        'views/crm_lead_views.xml',
        'views/purchase_requisition_views.xml',
        'views/sale_order_views.xml',
        'views/tender_menus.xml',
        'wizard/vendor_comparison_wizard_views.xml',
        'wizard/generate_quotation_wizard_views.xml',
        'wizard/create_project_wizard_views.xml',
        'report/tender_report.xml',
        'report/tender_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ics_tender_management/static/src/css/tender_kanban.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
