# ICS Tender Management - Implementation Blueprint

## 📋 Practical Implementation Guide from Competitive Analysis

**Document Purpose**: Extract and adapt specific code patterns from competitor modules for ICS implementation.

**Source Modules**:
- `tk_tender_management` (TechKhedut) - Dashboard, Bidding, Categories
- `sh_all_in_one_tender_bundle` (Softhealer) - Tender Types, Portal

**Target**: ICS Tender Management v18.0.3.0.0+

---

## 🎯 Phase 1: Quick Wins (1-2 weeks)

### Feature 1: Dashboard with Statistics ⭐⭐⭐

#### 1.1 Backend Model (Python)

**File**: `ics_tender_management/models/tender_dashboard.py`

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IcsTenderDashboard(models.Model):
    _name = 'ics.tender.dashboard'
    _description = "ICS Tender Dashboard"

    name = fields.Char(string="Dashboard")

    @api.model
    def get_tender_statistics(self):
        """Get comprehensive tender statistics for dashboard"""
        tender_obj = self.env['ics.tender.management']
        offer_obj = self.env['tender.vendor.offer']

        # Tender statistics
        total_tenders = tender_obj.search_count([])
        draft_tenders = tender_obj.search_count([('stage_id.sequence', '=', 1)])
        active_tenders = tender_obj.search_count([
            ('stage_id.name', 'in', ['Vendor Selection', 'Quotation Preparation', 'Quotation Review'])
        ])
        won_tenders = tender_obj.search_count([('stage_id.name', '=', 'Won')])
        lost_tenders = tender_obj.search_count([('stage_id.name', '=', 'Lost')])

        # Vendor statistics
        total_offers = offer_obj.search_count([])
        pending_offers = offer_obj.search_count([('status', '=', 'pending')])
        accepted_offers = offer_obj.search_count([('status', '=', 'accepted')])

        # Tender by type (if we implement tender types)
        tender_types = self._get_tender_by_type()

        # Tender by category
        tender_categories = self._get_tender_by_category()

        # Monthly trend (last 6 months)
        monthly_trend = self._get_monthly_trend()

        # Etimad integration stats
        etimad_stats = self._get_etimad_statistics()

        return {
            'total_tenders': total_tenders,
            'draft_tenders': draft_tenders,
            'active_tenders': active_tenders,
            'won_tenders': won_tenders,
            'lost_tenders': lost_tenders,
            'total_offers': total_offers,
            'pending_offers': pending_offers,
            'accepted_offers': accepted_offers,
            'tender_types': tender_types,
            'tender_categories': tender_categories,
            'monthly_trend': monthly_trend,
            'etimad_stats': etimad_stats,
        }

    def _get_tender_by_type(self):
        """Get tender distribution by tender type"""
        tender_obj = self.env['ics.tender.management']

        # Single vendor vs Product-wise
        single_vendor = tender_obj.search_count([('tender_type', '=', 'single_vendor')])
        multiple_vendor = tender_obj.search_count([('tender_type', '=', 'multiple_vendor')])

        return {
            'labels': ['Single Vendor', 'Product-wise'],
            'values': [single_vendor, multiple_vendor]
        }

    def _get_tender_by_category(self):
        """Get tender distribution by category"""
        tender_obj = self.env['ics.tender.management']

        categories = []
        values = []

        # Get all unique categories
        all_tenders = tender_obj.search([('tender_category', '!=', False)])
        category_dict = {}

        for tender in all_tenders:
            category = dict(tender._fields['tender_category'].selection).get(tender.tender_category, 'Other')
            category_dict[category] = category_dict.get(category, 0) + 1

        categories = list(category_dict.keys())
        values = list(category_dict.values())

        return {
            'labels': categories,
            'values': values
        }

    def _get_monthly_trend(self):
        """Get tender creation trend for last 6 months"""
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta

        tender_obj = self.env['ics.tender.management']

        months = []
        values = []

        today = datetime.today()

        for i in range(5, -1, -1):
            month_start = (today - relativedelta(months=i)).replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

            count = tender_obj.search_count([
                ('create_date', '>=', month_start.strftime('%Y-%m-%d')),
                ('create_date', '<=', month_end.strftime('%Y-%m-%d'))
            ])

            months.append(month_start.strftime('%B %Y'))
            values.append(count)

        return {
            'labels': months,
            'values': values
        }

    def _get_etimad_statistics(self):
        """Get Etimad integration statistics"""
        etimad_obj = self.env['ics.etimad.tender']

        total_etimad = etimad_obj.search_count([])
        new_tenders = etimad_obj.search_count([('status', '=', 'new')])
        imported_tenders = etimad_obj.search_count([('is_imported', '=', True)])

        return {
            'total_etimad': total_etimad,
            'new_tenders': new_tenders,
            'imported_tenders': imported_tenders,
        }
```

---

#### 1.2 Dashboard Action & Menu

**File**: `ics_tender_management/views/tender_dashboard_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Dashboard Client Action -->
    <record id="action_ics_tender_dashboard" model="ir.actions.client">
        <field name="name">Tender Dashboard</field>
        <field name="tag">ics_tender_dashboard</field>
    </record>

    <!-- Dashboard Menu (First in menu structure) -->
    <menuitem
        id="menu_tender_dashboard"
        name="Dashboard"
        parent="menu_tender_root"
        action="action_ics_tender_dashboard"
        sequence="0"/>
</odoo>
```

---

#### 1.3 Frontend Dashboard Component (JavaScript)

**File**: `ics_tender_management/static/src/js/tender_dashboard.js`

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class IcsTenderDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            stats: {
                total_tenders: 0,
                draft_tenders: 0,
                active_tenders: 0,
                won_tenders: 0,
                lost_tenders: 0,
                total_offers: 0,
                pending_offers: 0,
                accepted_offers: 0,
                etimad_stats: {},
            },
        });

        this.tenderTypeChart = useRef("tenderTypeChart");
        this.tenderCategoryChart = useRef("tenderCategoryChart");
        this.monthlyTrendChart = useRef("monthlyTrendChart");

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            const data = await this.orm.call(
                'ics.tender.dashboard',
                'get_tender_statistics',
                []
            );
            if (data) {
                this.state.stats = data;
            }
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    renderCharts() {
        // Tender Type Pie Chart
        if (this.tenderTypeChart.el && this.state.stats.tender_types) {
            const ctx1 = this.tenderTypeChart.el.getContext('2d');
            new Chart(ctx1, {
                type: 'pie',
                data: {
                    labels: this.state.stats.tender_types.labels,
                    datasets: [{
                        data: this.state.stats.tender_types.values,
                        backgroundColor: ['#4e73df', '#1cc88a'],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        }

        // Tender Category Bar Chart
        if (this.tenderCategoryChart.el && this.state.stats.tender_categories) {
            const ctx2 = this.tenderCategoryChart.el.getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: this.state.stats.tender_categories.labels,
                    datasets: [{
                        label: 'Tenders',
                        data: this.state.stats.tender_categories.values,
                        backgroundColor: '#4e73df',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }

        // Monthly Trend Line Chart
        if (this.monthlyTrendChart.el && this.state.stats.monthly_trend) {
            const ctx3 = this.monthlyTrendChart.el.getContext('2d');
            new Chart(ctx3, {
                type: 'line',
                data: {
                    labels: this.state.stats.monthly_trend.labels,
                    datasets: [{
                        label: 'Tenders Created',
                        data: this.state.stats.monthly_trend.values,
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    }

    openTenders(type) {
        let domain = [];
        let name = "Tenders";

        if (type === 'draft') {
            domain = [['stage_id.sequence', '=', 1]];
            name = "Draft Tenders";
        } else if (type === 'active') {
            domain = [['stage_id.name', 'in', ['Vendor Selection', 'Quotation Preparation', 'Quotation Review']]];
            name = "Active Tenders";
        } else if (type === 'won') {
            domain = [['stage_id.name', '=', 'Won']];
            name = "Won Tenders";
        } else if (type === 'lost') {
            domain = [['stage_id.name', '=', 'Lost']];
            name = "Lost Tenders";
        }

        this.action.doAction({
            name: name,
            type: 'ir.actions.act_window',
            res_model: 'ics.tender.management',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            context: {create: false},
        });
    }

    openEtimadTenders() {
        this.action.doAction({
            name: "Etimad Tenders",
            type: 'ir.actions.act_window',
            res_model: 'ics.etimad.tender',
            views: [[false, 'list'], [false, 'form']],
            context: {create: false},
        });
    }
}

IcsTenderDashboard.template = "ics_tender_management.Dashboard";

registry.category("actions").add("ics_tender_dashboard", IcsTenderDashboard);
```

---

#### 1.4 Dashboard Template (XML/OWL)

**File**: `ics_tender_management/static/src/xml/tender_dashboard.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ics_tender_management.Dashboard">
        <div class="ics_tender_dashboard">
            <!-- Page Header -->
            <div class="dashboard-header mb-4">
                <h2 class="mb-0">Tender Management Dashboard</h2>
                <p class="text-muted">Real-time overview of your tender operations</p>
            </div>

            <!-- Statistics Cards Row 1 -->
            <div class="row mb-4">
                <!-- Total Tenders Card -->
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-primary shadow h-100 py-2 cursor-pointer" t-on-click="() => this.openTenders('all')">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                        Total Tenders
                                    </div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">
                                        <t t-esc="state.stats.total_tenders"/>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fa fa-file-text fa-2x text-gray-300"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Active Tenders Card -->
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-success shadow h-100 py-2 cursor-pointer" t-on-click="() => this.openTenders('active')">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                        Active Tenders
                                    </div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">
                                        <t t-esc="state.stats.active_tenders"/>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fa fa-hourglass-half fa-2x text-gray-300"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Won Tenders Card -->
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-info shadow h-100 py-2 cursor-pointer" t-on-click="() => this.openTenders('won')">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                        Won Tenders
                                    </div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">
                                        <t t-esc="state.stats.won_tenders"/>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fa fa-trophy fa-2x text-gray-300"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Etimad Tenders Card -->
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-warning shadow h-100 py-2 cursor-pointer" t-on-click="() => this.openEtimadTenders()">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                        Etimad Tenders
                                    </div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">
                                        <t t-esc="state.stats.etimad_stats.total_etimad || 0"/>
                                    </div>
                                    <div class="text-xs text-muted">
                                        <t t-esc="state.stats.etimad_stats.new_tenders || 0"/> New
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fa fa-cloud-download fa-2x text-gray-300"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="row mb-4">
                <!-- Tender Type Distribution -->
                <div class="col-xl-4 col-lg-6 mb-4">
                    <div class="card shadow">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">Tender Type Distribution</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" style="height: 250px;">
                                <canvas t-ref="tenderTypeChart"/>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tender by Category -->
                <div class="col-xl-4 col-lg-6 mb-4">
                    <div class="card shadow">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">Tenders by Category</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" style="height: 250px;">
                                <canvas t-ref="tenderCategoryChart"/>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Monthly Trend -->
                <div class="col-xl-4 col-lg-12 mb-4">
                    <div class="card shadow">
                        <div class="card-header py-3">
                            <h6 class="m-0 font-weight-bold text-primary">6-Month Trend</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" style="height: 250px;">
                                <canvas t-ref="monthlyTrendChart"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Vendor Offers Row -->
            <div class="row">
                <div class="col-xl-4 col-md-4 mb-4">
                    <div class="card border-left-info shadow h-100 py-2">
                        <div class="card-body">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                Total Offers
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">
                                <t t-esc="state.stats.total_offers"/>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-4 col-md-4 mb-4">
                    <div class="card border-left-warning shadow h-100 py-2">
                        <div class="card-body">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                Pending Offers
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">
                                <t t-esc="state.stats.pending_offers"/>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-xl-4 col-md-4 mb-4">
                    <div class="card border-left-success shadow h-100 py-2">
                        <div class="card-body">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                Accepted Offers
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">
                                <t t-esc="state.stats.accepted_offers"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
```

---

#### 1.5 Dashboard Styles (SCSS)

**File**: `ics_tender_management/static/src/scss/tender_dashboard.scss`

```scss
.ics_tender_dashboard {
    padding: 20px;
    background-color: #f8f9fc;

    .dashboard-header {
        h2 {
            color: #5a5c69;
            font-weight: 700;
        }
    }

    .card {
        border-radius: 0.35rem;

        &.border-left-primary {
            border-left: 0.25rem solid #4e73df !important;
        }

        &.border-left-success {
            border-left: 0.25rem solid #1cc88a !important;
        }

        &.border-left-info {
            border-left: 0.25rem solid #36b9cc !important;
        }

        &.border-left-warning {
            border-left: 0.25rem solid #f6c23e !important;
        }
    }

    .cursor-pointer {
        cursor: pointer;
        transition: transform 0.2s;

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
        }
    }

    .chart-container {
        position: relative;
    }

    .text-gray-800 {
        color: #5a5c69 !important;
    }

    .text-gray-300 {
        color: #dddfeb !important;
    }
}
```

---

#### 1.6 Assets Registration

**File**: `ics_tender_management/__manifest__.py` (add to assets)

```python
'assets': {
    'web.assets_backend': [
        'ics_tender_management/static/src/scss/tender_dashboard.scss',
        'ics_tender_management/static/src/js/tender_dashboard.js',
        'ics_tender_management/static/src/xml/tender_dashboard.xml',
    ],
},
```

---

### Feature 2: Tender Category as Model ⭐⭐⭐

#### 2.1 Create Tender Category Model

**File**: `ics_tender_management/models/tender_category.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TenderCategory(models.Model):
    _name = 'ics.tender.category'
    _description = 'Tender Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='Category Code',
        size=10,
        help='Short code for the category'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    description = fields.Text(
        string='Description',
        translate=True
    )

    terms_conditions = fields.Html(
        string='Default Terms & Conditions',
        translate=True,
        help='Default terms and conditions for tenders of this category'
    )

    color = fields.Integer(
        string='Color Index',
        help='Color for kanban view'
    )

    tender_count = fields.Integer(
        string='Tender Count',
        compute='_compute_tender_count'
    )

    # Site specific settings
    is_site_specific = fields.Boolean(
        string='Site-Specific Category',
        help='Requires site/location information'
    )

    # Approval settings
    requires_special_approval = fields.Boolean(
        string='Requires Special Approval',
        help='Tenders in this category require special approval'
    )

    approval_user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
        help='Users who can approve tenders in this category'
    )

    @api.depends('name')
    def _compute_tender_count(self):
        """Compute number of tenders in this category"""
        for record in self:
            record.tender_count = self.env['ics.tender.management'].search_count([
                ('category_id', '=', record.id)
            ])

    def action_view_tenders(self):
        """Smart button action to view tenders in this category"""
        self.ensure_one()
        return {
            'name': f'Tenders - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.management',
            'view_mode': 'tree,form,kanban',
            'domain': [('category_id', '=', self.id)],
            'context': {
                'default_category_id': self.id,
                'create': True,
            },
        }
```

---

#### 2.2 Update Tender Model

**File**: `ics_tender_management/models/tender.py` (modify existing)

```python
# Change from:
tender_category = fields.Selection([...])

# To:
category_id = fields.Many2one(
    'ics.tender.category',
    string='Tender Category',
    required=True,
    tracking=True
)

# Add related fields for easy access
category_code = fields.Char(
    related='category_id.code',
    string='Category Code',
    store=True
)

is_site_specific = fields.Boolean(
    related='category_id.is_site_specific',
    string='Site Specific',
    store=True
)

# Auto-fill terms and conditions from category
@api.onchange('category_id')
def _onchange_category_id(self):
    if self.category_id and self.category_id.terms_conditions:
        if not self.terms_conditions:
            self.terms_conditions = self.category_id.terms_conditions
```

---

#### 2.3 Category Views

**File**: `ics_tender_management/views/tender_category_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_ics_tender_category_tree" model="ir.ui.view">
        <field name="name">ics.tender.category.tree</field>
        <field name="model">ics.tender.category</field>
        <field name="arch" type="xml">
            <tree string="Tender Categories">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="code"/>
                <field name="is_site_specific"/>
                <field name="requires_special_approval"/>
                <field name="tender_count"/>
                <field name="active"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_ics_tender_category_form" model="ir.ui.view">
        <field name="name">ics.tender.category.form</field>
        <field name="model">ics.tender.category</field>
        <field name="arch" type="xml">
            <form string="Tender Category">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_tenders" type="object"
                                class="oe_stat_button" icon="fa-file-text">
                            <field name="tender_count" widget="statinfo" string="Tenders"/>
                        </button>
                    </div>

                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            invisible="active"/>

                    <group>
                        <group>
                            <field name="name" placeholder="e.g., IT Equipment Supply"/>
                            <field name="code" placeholder="e.g., IT-EQUIP"/>
                            <field name="sequence"/>
                            <field name="color" widget="color_picker"/>
                        </group>
                        <group>
                            <field name="active"/>
                            <field name="is_site_specific"/>
                            <field name="requires_special_approval"/>
                            <field name="approval_user_ids" widget="many2many_tags"
                                   invisible="not requires_special_approval"/>
                        </group>
                    </group>

                    <notebook>
                        <page string="Description" name="description">
                            <field name="description" placeholder="Category description..."/>
                        </page>
                        <page string="Default Terms &amp; Conditions" name="terms">
                            <field name="terms_conditions" widget="html"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Kanban View -->
    <record id="view_ics_tender_category_kanban" model="ir.ui.view">
        <field name="name">ics.tender.category.kanban</field>
        <field name="model">ics.tender.category</field>
        <field name="arch" type="xml">
            <kanban>
                <field name="color"/>
                <field name="tender_count"/>
                <templates>
                    <t t-name="kanban-box">
                        <div t-attf-class="oe_kanban_color_#{kanban_getcolor(record.color.raw_value)} oe_kanban_card oe_kanban_global_click">
                            <div class="o_kanban_card_content">
                                <div class="o_kanban_primary_left">
                                    <div class="o_primary">
                                        <strong><field name="name"/></strong>
                                    </div>
                                    <div>
                                        <field name="code"/>
                                    </div>
                                </div>
                            </div>
                            <div class="o_kanban_card_manage_pane">
                                <div class="o_kanban_card_manage_section o_kanban_manage_reports">
                                    <div>
                                        <a type="object" name="action_view_tenders">
                                            <span><t t-esc="record.tender_count.value"/> Tenders</span>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ics_tender_category" model="ir.actions.act_window">
        <field name="name">Tender Categories</field>
        <field name="res_model">ics.tender.category</field>
        <field name="view_mode">tree,form,kanban</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first tender category
            </p>
            <p>
                Categories help organize tenders by type (Construction, IT, Services, etc.)
            </p>
        </field>
    </record>

    <!-- Menu -->
    <menuitem
        id="menu_tender_category"
        name="Categories"
        parent="menu_tender_configuration"
        action="action_ics_tender_category"
        sequence="10"/>
</odoo>
```

---

#### 2.4 Security (Access Rights)

**File**: `ics_tender_management/security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ics_tender_category_user,ics.tender.category.user,model_ics_tender_category,tender_group_user,1,0,0,0
access_ics_tender_category_manager,ics.tender.category.manager,model_ics_tender_category,tender_group_manager,1,1,1,1
```

---

#### 2.5 Default Data (Categories)

**File**: `ics_tender_management/data/tender_category_data.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Default Tender Categories -->
        <record id="category_construction" model="ics.tender.category">
            <field name="name">Construction &amp; Infrastructure</field>
            <field name="code">CONST</field>
            <field name="sequence">10</field>
            <field name="color">1</field>
            <field name="description">Construction projects, building, infrastructure development</field>
            <field name="is_site_specific">1</field>
        </record>

        <record id="category_it_equipment" model="ics.tender.category">
            <field name="name">IT Equipment &amp; Software</field>
            <field name="code">IT</field>
            <field name="sequence">20</field>
            <field name="color">2</field>
            <field name="description">IT hardware, software, networking equipment</field>
        </record>

        <record id="category_services" model="ics.tender.category">
            <field name="name">Professional Services</field>
            <field name="code">SERV</field>
            <field name="sequence">30</field>
            <field name="color">3</field>
            <field name="description">Consulting, training, maintenance services</field>
        </record>

        <record id="category_supplies" model="ics.tender.category">
            <field name="name">Supplies &amp; Materials</field>
            <field name="code">SUPPLY</field>
            <field name="sequence">40</field>
            <field name="color">4</field>
            <field name="description">Office supplies, materials, consumables</field>
        </record>

        <record id="category_maintenance" model="ics.tender.category">
            <field name="name">Maintenance &amp; Operations</field>
            <field name="code">MAINT</field>
            <field name="sequence">50</field>
            <field name="color">5</field>
            <field name="description">Facility maintenance, operations, support services</field>
            <field name="is_site_specific">1</field>
        </record>
    </data>
</odoo>
```

---

### Feature 3: Tender Cancellation Wizard ⭐⭐

**File**: `ics_tender_management/wizard/tender_cancel_wizard.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TenderCancelWizard(models.TransientModel):
    _name = 'ics.tender.cancel.wizard'
    _description = 'Tender Cancellation Wizard'

    tender_id = fields.Many2one(
        'ics.tender.management',
        string='Tender',
        required=True,
        readonly=True
    )

    reason = fields.Html(
        string='Cancellation Reason',
        required=True,
        help='Explain why this tender is being cancelled'
    )

    notify_vendors = fields.Boolean(
        string='Notify Vendors',
        default=True,
        help='Send cancellation notification to all vendors who submitted offers'
    )

    def action_cancel_tender(self):
        """Cancel tender and optionally notify vendors"""
        self.ensure_one()

        # Update tender
        self.tender_id.write({
            'cancellation_reason': self.reason,
            'state': 'cancelled',
        })

        # Move to Lost stage
        lost_stage = self.env.ref('ics_tender_management.stage_lost', False)
        if lost_stage:
            self.tender_id.stage_id = lost_stage

        # Notify vendors if requested
        if self.notify_vendors:
            self._notify_vendors()

        # Log in chatter
        self.tender_id.message_post(
            body=f"<p>Tender cancelled.</p><p><strong>Reason:</strong></p>{self.reason}",
            message_type='notification',
        )

        return {'type': 'ir.actions.act_window_close'}

    def _notify_vendors(self):
        """Send email to vendors about cancellation"""
        template = self.env.ref('ics_tender_management.mail_template_tender_cancelled', False)
        if not template:
            return

        # Get all vendors with offers
        vendor_ids = self.tender_id.boq_line_ids.mapped('vendor_offer_ids.vendor_id')

        for vendor in vendor_ids:
            if vendor.email:
                template.with_context(
                    vendor_name=vendor.name,
                    cancellation_reason=self.reason
                ).send_mail(self.tender_id.id, force_send=True, email_values={
                    'email_to': vendor.email,
                })
```

**File**: `ics_tender_management/wizard/tender_cancel_wizard_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_tender_cancel_wizard_form" model="ir.ui.view">
        <field name="name">ics.tender.cancel.wizard.form</field>
        <field name="model">ics.tender.cancel.wizard</field>
        <field name="arch" type="xml">
            <form string="Cancel Tender">
                <group>
                    <field name="tender_id" invisible="1"/>
                    <field name="notify_vendors"/>
                </group>

                <group>
                    <field name="reason" widget="html" placeholder="Please explain the reason for cancellation..."/>
                </group>

                <footer>
                    <button name="action_cancel_tender" string="Confirm Cancellation"
                            type="object" class="btn-primary"/>
                    <button string="Discard" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

---

### Feature 4: Vendor Management Enhancement ⭐⭐

**File**: `ics_tender_management/models/res_partner.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Vendor flags
    is_tender_vendor = fields.Boolean(
        string='Is Tender Vendor',
        help='Check if this partner is a tender vendor'
    )

    # Vendor categories
    tender_category_ids = fields.Many2many(
        'ics.tender.category',
        'partner_tender_category_rel',
        'partner_id',
        'category_id',
        string='Tender Categories',
        help='Categories this vendor specializes in'
    )

    # Vendor statistics
    tender_count = fields.Integer(
        string='Tender Count',
        compute='_compute_tender_stats'
    )

    offer_count = fields.Integer(
        string='Offer Count',
        compute='_compute_tender_stats'
    )

    won_tender_count = fields.Integer(
        string='Won Tenders',
        compute='_compute_tender_stats'
    )

    # Vendor qualification
    vendor_qualification = fields.Selection([
        ('not_qualified', 'Not Qualified'),
        ('pre_qualified', 'Pre-Qualified'),
        ('qualified', 'Qualified'),
        ('blacklisted', 'Blacklisted'),
    ], string='Qualification Status', default='not_qualified')

    qualification_date = fields.Date(
        string='Qualification Date'
    )

    qualification_notes = fields.Text(
        string='Qualification Notes'
    )

    # Performance rating
    vendor_rating = fields.Float(
        string='Vendor Rating',
        digits=(3, 2),
        help='Average performance rating (0-5)'
    )

    @api.depends('name')
    def _compute_tender_stats(self):
        """Compute vendor tender statistics"""
        for partner in self:
            # Count offers
            offers = self.env['tender.vendor.offer'].search_count([
                ('vendor_id', '=', partner.id)
            ])
            partner.offer_count = offers

            # Count tenders with offers
            tender_ids = self.env['tender.vendor.offer'].search([
                ('vendor_id', '=', partner.id)
            ]).mapped('tender_id')
            partner.tender_count = len(tender_ids)

            # Count won tenders
            won_tenders = tender_ids.filtered(
                lambda t: t.selected_vendor_id == partner
            )
            partner.won_tender_count = len(won_tenders)

    def action_view_vendor_tenders(self):
        """Smart button: View tenders where this vendor participated"""
        self.ensure_one()

        tender_ids = self.env['tender.vendor.offer'].search([
            ('vendor_id', '=', self.id)
        ]).mapped('tender_id').ids

        return {
            'name': f'Tenders - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'ics.tender.management',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', tender_ids)],
            'context': {'create': False},
        }
```

---

## 📋 Implementation Checklist

### Phase 1: Dashboard (Week 1)
- [ ] Create `tender_dashboard.py` model
- [ ] Implement statistics methods
- [ ] Create dashboard JavaScript component
- [ ] Design dashboard template (OWL)
- [ ] Add dashboard styles (SCSS)
- [ ] Register assets in manifest
- [ ] Create menu item
- [ ] Test all statistics
- [ ] Test all charts
- [ ] Update documentation

### Phase 2: Categories (Week 1-2)
- [ ] Create `tender_category.py` model
- [ ] Update `tender.py` model
- [ ] Create category views (tree, form, kanban)
- [ ] Add security rules
- [ ] Create default category data
- [ ] Migration script (convert selection → model)
- [ ] Test category functionality
- [ ] Update documentation

### Phase 3: Cancellation (Week 2)
- [ ] Create cancellation wizard
- [ ] Create wizard views
- [ ] Add email template
- [ ] Add menu action
- [ ] Test cancellation workflow
- [ ] Update documentation

### Phase 4: Vendor Enhancement (Week 2)
- [ ] Extend `res.partner` model
- [ ] Add vendor statistics
- [ ] Add qualification fields
- [ ] Create vendor views
- [ ] Add smart buttons
- [ ] Test vendor features
- [ ] Update documentation

---

## 🚀 Next Steps

1. **Get approval** for Phase 1 implementation
2. **Create branch** for development
3. **Start with dashboard** (highest value)
4. **Test incrementally** after each feature
5. **Update documentation** continuously
6. **Deploy to staging** for user testing
7. **Collect feedback** before production

---

*Implementation Blueprint v1.0*
*Created: January 29, 2024*
*ICS Tender Management - iCloud Solutions*
