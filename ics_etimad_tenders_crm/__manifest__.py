# __manifest__.py
{
    "name": "ICS Etimad Tenders CRM",
    "version": "18.0.4.2.0",
    "category": "Sales/CRM",
    "author": "iCloud Solutions",
    "website": "https://icloud-solutions.net",
    "summary": "Complete integration of Saudi Etimad Tenders platform with Odoo CRM",
    "description": """
        Etimad Tenders CRM Integration
        ===============================
        
        Complete integration with Saudi Arabia's Etimad government tenders platform.
        
        Key Features:
        -------------
        * **Automated Scraping**: Direct integration with Etimad portal API
        * **Smart Sync**: Automatic daily synchronization of new tenders
        * **CRM Integration**: Create opportunities directly from tenders
        * **Advanced Filtering**: Search by agency, type, activity, deadline, value
        * **Status Tracking**: Track tender progress from new to won/lost
        * **Favorites System**: Mark important tenders for quick access
        * **Deadline Alerts**: Visual indicators for urgent tenders
        * **Financial Tracking**: Monitor invitation costs and fees
        * **Hijri Calendar**: Support for Islamic calendar dates
        * **Mobile Responsive**: Kanban view optimized for mobile devices
        
        Workflow:
        ---------
        1. System automatically fetches tenders from Etimad portal
        2. Review tenders in list/kanban view with color-coded priorities
        3. Create CRM opportunities with one click
        4. Track tender status through qualification to won/lost
        5. Link tenders to opportunities for complete visibility
        
        Technical:
        ----------
        * Direct API integration with https://tenders.etimad.sa
        * Anti-bot protection handling with retry mechanism
        * Scheduled actions for automated synchronization
        * Full audit trail with mail integration
        * Supports multiple currencies (SAR default)
        
        Requirements:
        ------------
        * Python requests library
        * Internet connectivity for API access
        * CRM module installed
    """,
    "depends": [
        "crm",
        "base",
        "mail",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/etimad_activities_data.xml",
        "data/ir_cron_data.xml",
        "data/etimad_server_actions.xml",
        "views/etimad_menus.xml",
        "views/etimad_activity_views.xml",
        "views/etimad_tender_views.xml",
        "views/etimad_matching_rule_views.xml",
        "views/etimad_config_wizard_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "external_dependencies": {
        "python": ["requests", "lxml"],
    },
    "assets": {
        "web.assets_backend": [
            #"ics_etimad_tenders_crm/static/src/css/etimad_tenders.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    "images": ["static/description/banner.png"],
    "price": 0.00,
    "currency": "EUR",
}
