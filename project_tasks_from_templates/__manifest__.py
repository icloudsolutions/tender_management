# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Project Templates',
    'version': '18.0.1.0.0',
    'category': "Project",
    'summary': "Create projects from templates with CRM integration and "
                "automatic project creation from opportunities",
    'description': "When faced with the need to create multiple projects that "
                   "share similar tasks, manually inputting data such as task "
                   "names, descriptions, and assigned individuals can be "
                   "time-consuming. This module offers assistance in creating "
                   "and managing projects based on pre-defined templates.\n\n"
                   "Key Features:\n"
                   "* Create project templates with tasks and stages\n"
                   "* Auto-create projects from CRM opportunities\n"
                   "* Configure which CRM stage triggers project creation\n"
                   "* Link projects to opportunities for full traceability\n"
                   "* Multiple templates per CRM stage support\n"
                   "* Automatic task creation from templates",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_sub_task_views.xml',
        'views/project_stage_views.xml',
        'views/project_task_template_views.xml',
        'views/res_config_settings_views.xml',
        'views/project_project_views_crm.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
