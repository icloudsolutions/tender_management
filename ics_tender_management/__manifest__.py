{
    'name': 'ICS Tender Management',
    'version': '18.0.2.5.0',
    'category': 'Sales/CRM',
    'summary': 'Complete Tender Management System for Saudi Etimad Portal Integration',
    'description': """
        ICS Tender Management - Complete Saudi Tender Solution
        =======================================================

        100% COMPLIANT with ICS Project Management Procedures

        Professional tender management system for Saudi Arabia with:

        COMPREHENSIVE DASHBOARD (NEW in v18.0.2.0.0)
        - 14 Real-time statistics cards
        - 4 Interactive charts (Chart.js)
        - Project execution tracking
        - ICS procedure compliance monitoring
        - Win/loss ratio analysis
        - Financial summary with multi-currency
        - Etimad platform integration stats
        - Vendor offer tracking
        - Bilingual interface (English/Arabic)

        PRE-AWARD PHASE (Tender Lifecycle)
        Phase 1: Draft
        - Integration with Etimad tender scraper
        - Automatic lead creation from portal.etimad.sa
        - Tender ID and category tracking
        - Team assignment

        Phase 2: Technical Study
        - BoQ (Bill of Quantities) management
        - Excel import/export for large BoQs
        - Technical specifications documentation
        - Requirements analysis

        Phase 3: Financial Study
        - Vendor RFQ management
        - Multi-vendor quotation comparison
        - Side-by-side vendor offer analysis
        - Automated RFQ email sending

        Phase 4: Quotation Prepared
        - Final quotation with margin calculation
        - Professional quotation generation
        - Sale order creation
        - Internal approval workflow

        Phase 5: Submitted & Under Evaluation
        - Submission tracking
        - Customer clarification management
        - Status monitoring

        Phase 6: Won/Lost/Cancelled
        - Award letter management
        - Loss reason documentation
        - Lessons learned tracking

        POST-AWARD PHASE - SUPPLY PROJECTS (مشاريع التوريد)
        Fully aligned with ICS Supply Projects Procedure:
        **WITH AUTOMATIC TASK TEMPLATE CREATION:**

        1. بدء المشروع (Kick-Off)
        2. التخطيط التشغيلي (Operational Planning)
        3. تنفيذ الأعمال وفق كراسة الشروط (Execution per Specs)
        4. نقل البضاعة (Transport & Logistics)
        5. التسليم الابتدائي (Preliminary Handover)
        6. استلام البضاعة من العميل (Customer Receipt)
        7. المستخلصات المالية (Financial Invoicing)
        8. المتابعة والتقارير (Monitoring & Reporting)
        9. التسليم والإقفال (Final Handover & Closure)

        POST-AWARD PHASE - O&M SERVICES (مشاريع الصيانة والتشغيل)
        Fully aligned with ICS O&M Services Procedure:
        **WITH AUTOMATIC TASK TEMPLATE CREATION:**

        1. بدء المشروع (Project Kick-off)
        2. التخطيط التشغيلي (Operational Planning)
        3. تنفيذ أعمال الصيانة الدورية (Preventive Maintenance)
        4. التشغيل والمراقبة (Operation & Monitoring)
        5. إدارة قطع الغيار (Spare Parts Management)
        6. المستخلصات المالية (Financial Invoicing)
        7. المتابعة والتقارير (Monitoring & Reporting)
        8. مراجعة الأداء الدورية (Performance Reviews)

        KEY FEATURES
        - Professional dashboard with 14 metrics + 4 charts
        - Complete Etimad platform integration
        - CRM opportunity to tender conversion
        - Vendor comparison wizard
        - Purchase order generation
        - One-click project creation from won tenders
        - **AUTO-PROJECT CREATION with predefined task templates**
        - Project execution tracking (Supply & O&M)
        - ICS procedure compliance monitoring
        - Win/loss performance analysis
        - Financial tracking and invoicing
        - Complete audit trail
        - Bilingual support (English/Arabic)

        COMPREHENSIVE DOCUMENTATION (7,000+ lines)
        - Complete workflow guide (2,500 lines)
        - Dashboard user guide (320 lines)
        - Quick reference card (350 lines)
        - Technical implementation guide (650 lines)
        - Compliance certification report (550 lines)
        - Procedure compliance guide (450 lines)
        - Competitive analysis (450 lines)
        - Complete documentation index

        TRAINING MATERIALS INCLUDED
        - Learning paths for all roles
        - Step-by-step workflows
        - Real-world scenarios
        - Troubleshooting guides
        - Best practices

        CERTIFIED 100% COMPLIANT
        - Supply Projects: All 6 phases tracked
        - O&M Services: All 6 phases tracked
        - ICS Procedures: Full alignment
        - Quality Assurance: Complete validation

        Perfect for:
        - Government contractors in Saudi Arabia
        - Companies bidding on Etimad tenders
        - Organizations requiring ICS compliance
        - Large-scale tender management
        - Multi-vendor tender scenarios

        Support: contact@icloud-solutions.net
        Website: https://icloud-solutions.net
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
    'external_dependencies': {
        'python': [],
    },
    # Optional dependency - works with or without project_tasks_from_templates
    # If installed, will use their template system as fallback
    'data': [
        'security/tender_security.xml',
        'security/ir.model.access.csv',
        'data/tender_sequence.xml',
        'data/tender_stage_data.xml',
        'data/mail_template_data.xml',
        'data/project_task_templates.xml',
        'data/tender_decline_reason_data.xml',
        'views/tender_decline_reason_views.xml',
        'views/tender_approval_rule_views.xml',
        'views/tender_menus.xml',
        'views/tender_dashboard_views.xml',
        'views/tender_views.xml',
        'views/tender_boq_views.xml',
        'views/crm_lead_views.xml',
        'views/etimad_tender_views.xml',
        'views/purchase_requisition_views.xml',
        'views/sale_order_views.xml',
        'wizard/vendor_comparison_wizard_views.xml',
        'wizard/generate_quotation_wizard_views.xml',
        'wizard/create_project_wizard_views.xml',
        'wizard/import_boq_wizard_views.xml',
        'wizard/mark_lost_wizard_views.xml',
        'wizard/decline_tender_wizard_views.xml',
        'report/tender_report.xml',
        'report/tender_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ics_tender_management/static/src/css/tender_kanban.css',
            'ics_tender_management/static/src/scss/tender_dashboard.scss',
            'ics_tender_management/static/src/js/tender_dashboard.js',
            'ics_tender_management/static/src/xml/tender_dashboard.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}