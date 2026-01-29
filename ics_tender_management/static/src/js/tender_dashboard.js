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
                supply_projects: 0,
                maintenance_projects: 0,
                vendor_offers: {
                    total: 0,
                    pending: 0,
                    accepted: 0,
                },
                etimad_stats: {
                    total_etimad: 0,
                    new_tenders: 0,
                    imported_tenders: 0,
                },
                financial_summary: {
                    total_budget: 0,
                    active_budget: 0,
                    won_budget: 0,
                    currency_symbol: 'SAR',
                },
            },
            isLoading: true,
        });

        this.tenderTypeChart = useRef("tenderTypeChart");
        this.tenderCategoryChart = useRef("tenderCategoryChart");
        this.monthlyTrendChart = useRef("monthlyTrendChart");
        this.stageDistributionChart = useRef("stageDistributionChart");

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call(
                'ics.tender.dashboard',
                'get_tender_statistics',
                []
            );
            if (data) {
                this.state.stats = data;
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    renderCharts() {
        this.renderTenderTypeChart();
        this.renderTenderCategoryChart();
        this.renderMonthlyTrendChart();
        this.renderStageDistributionChart();
    }

    renderTenderTypeChart() {
        if (this.tenderTypeChart.el && this.state.stats.tender_by_type) {
            const ctx = this.tenderTypeChart.el.getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: this.state.stats.tender_by_type.labels,
                    datasets: [{
                        data: this.state.stats.tender_by_type.values,
                        backgroundColor: ['#4e73df', '#1cc88a'],
                        hoverBackgroundColor: ['#2e59d9', '#17a673'],
                        borderWidth: 2,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                        }
                    }
                }
            });
        }
    }

    renderTenderCategoryChart() {
        if (this.tenderCategoryChart.el && this.state.stats.tender_by_category) {
            const ctx = this.tenderCategoryChart.el.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.state.stats.tender_by_category.labels,
                    datasets: [{
                        label: 'Tenders',
                        data: this.state.stats.tender_by_category.values,
                        backgroundColor: '#4e73df',
                        hoverBackgroundColor: '#2e59d9',
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
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }

    renderMonthlyTrendChart() {
        if (this.monthlyTrendChart.el && this.state.stats.monthly_trend) {
            const ctx = this.monthlyTrendChart.el.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.state.stats.monthly_trend.labels,
                    datasets: [{
                        label: 'Tenders Created',
                        data: this.state.stats.monthly_trend.values,
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        fill: true,
                        tension: 0.3,
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
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }

    renderStageDistributionChart() {
        if (this.stageDistributionChart.el && this.state.stats.stage_distribution) {
            const ctx = this.stageDistributionChart.el.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.state.stats.stage_distribution.labels,
                    datasets: [{
                        label: 'Tenders',
                        data: this.state.stats.stage_distribution.values,
                        backgroundColor: '#36b9cc',
                        hoverBackgroundColor: '#2c9faf',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }

    openTenders(type) {
        let domain = [];
        let name = "Tenders";

        if (type === 'all') {
            domain = [];
            name = "All Tenders";
        } else if (type === 'draft') {
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
        } else if (type === 'supply') {
            domain = [['tender_category', '=', 'supply']];
            name = "Supply Projects";
        } else if (type === 'maintenance') {
            domain = [['tender_category', '=', 'maintenance']];
            name = "Maintenance Projects";
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

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    }
}

IcsTenderDashboard.template = "ics_tender_management.Dashboard";

registry.category("actions").add("ics_tender_dashboard", IcsTenderDashboard);
