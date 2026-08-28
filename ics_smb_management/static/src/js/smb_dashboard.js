/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class SmbDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            stats: {
                pending_credit: 0,
                credit_approved: 0,
                credit_rejected: 0,
                total_quotations: 0,
                confirmed_orders: 0,
                overdue_invoices: 0,
                delivery_projects: 0,
                credit_distribution: { labels: [], values: [] },
                monthly_trend: { labels: [], values: [] },
            },
            isLoading: true,
        });

        this.creditChart = useRef("creditChart");
        this.monthlyTrendChart = useRef("monthlyTrendChart");

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
                "smb.dashboard",
                "get_smb_statistics",
                []
            );
            if (data) {
                this.state.stats = data;
            }
        } catch (error) {
            console.error("Error loading SMB dashboard data:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    renderCharts() {
        this.renderCreditChart();
        this.renderMonthlyTrendChart();
    }

    renderCreditChart() {
        if (
            this.creditChart.el &&
            this.state.stats.credit_distribution &&
            this.state.stats.credit_distribution.values.length > 0
        ) {
            const ctx = this.creditChart.el.getContext("2d");
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: this.state.stats.credit_distribution.labels,
                    datasets: [
                        {
                            data: this.state.stats.credit_distribution.values,
                            backgroundColor: ["#f6c23e", "#1cc88a", "#e74a3b"],
                            hoverBackgroundColor: ["#dda20a", "#17a673", "#be2617"],
                            borderWidth: 2,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: "bottom" },
                    },
                },
            });
        }
    }

    renderMonthlyTrendChart() {
        if (
            this.monthlyTrendChart.el &&
            this.state.stats.monthly_trend &&
            this.state.stats.monthly_trend.labels.length > 0
        ) {
            const ctx = this.monthlyTrendChart.el.getContext("2d");
            new Chart(ctx, {
                type: "line",
                data: {
                    labels: this.state.stats.monthly_trend.labels,
                    datasets: [
                        {
                            label: "Confirmed Orders",
                            data: this.state.stats.monthly_trend.values,
                            borderColor: "#4e73df",
                            backgroundColor: "rgba(78, 115, 223, 0.1)",
                            fill: true,
                            tension: 0.3,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                        },
                    },
                    plugins: {
                        legend: { display: false },
                    },
                },
            });
        }
    }

    openPendingCredit() {
        this.action.doAction({
            name: "Credit Approval Queue",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["smb_credit_state", "=", "sent_to_credit"]],
            context: { search_default_sent_to_credit: 1 },
        });
    }

    openCreditApproved() {
        this.action.doAction({
            name: "Credit Approved",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["smb_credit_state", "=", "credit_approved"]],
        });
    }

    openCreditRejected() {
        this.action.doAction({
            name: "Credit Rejected",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["smb_credit_state", "=", "credit_rejected"]],
        });
    }

    openOverdueInvoices() {
        this.action.doAction({
            name: "Overdue Invoices",
            type: "ir.actions.act_window",
            res_model: "account.move",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
            ],
        });
    }

    openQuotations() {
        this.action.doAction({
            name: "Quotations",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "in", ["draft", "sent"]]],
        });
    }

    openConfirmedOrders() {
        this.action.doAction({
            name: "Confirmed Orders",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "in", ["sale", "done"]]],
        });
    }

    openDeliveryProjects() {
        this.action.doAction({
            name: "Delivery Projects",
            type: "ir.actions.act_window",
            res_model: "project.project",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["sale_order_id", "!=", false]],
        });
    }
}

SmbDashboard.template = "ics_smb_management.SmbDashboard";

registry.category("actions").add("ics_smb_management.smb_dashboard", SmbDashboard);
