# ICS Tender Management

Complete Saudi Tender Management System for Odoo 18

## Overview

ICS Tender Management is a comprehensive module designed for Saudi Arabian businesses managing government and private tenders. It provides complete integration with the Etimad portal (portal.etimad.sa) and streamlines the entire tender lifecycle from lead creation to project execution.

## Features

### 🎯 Core Features

- **Etimad Portal Integration**: Automatic tender scraping and lead creation
- **Complete CRM Integration**: Seamless linking between opportunities and tenders
- **BoQ Management**: Upload, manage, and analyze Bill of Quantities
- **Purchase Agreements**: Send RFQs to multiple vendors via Call for Tenders
- **Vendor Comparison**: Advanced side-by-side comparison with automatic best price selection
- **Automated Quotations**: Generate sales quotations with configurable margins
- **Kanban Workflow**: Visual stage tracking from Draft to Won/Lost
- **Project Creation**: One-click project kickoff with automatic task generation

### 📋 Workflow Phases

#### Phase 1: Lead Creation & Registration
- Automatic scraping from Etimad portal
- CRM lead auto-creation
- Tender ID and category tracking
- Document purchase date management

#### Phase 2: Technical & Financial Study
- BoQ upload and analysis
- Multi-vendor RFQ creation
- Vendor quotation comparison
- Best vendor selection

#### Phase 3: Quotation & Submission
- Margin calculation and pricing
- Sales quotation generation
- Submission workflow
- Evaluation tracking

#### Phase 4: Execution
- Won tender processing
- Project creation with tasks
- Sales order integration
- Complete execution tracking

## Installation

1. Copy the `ics_tender_management` module to your Odoo addons directory
2. Ensure the `ics_etimad_tenders_crm` module is installed
3. Restart Odoo service
4. Update Apps List
5. Install "ICS Tender Management"

## Dependencies

- base
- crm
- sale_management
- purchase
- purchase_requisition
- project
- ics_etimad_tenders_crm

## Usage

### Creating a Tender

1. Navigate to **Tender Management > Tenders > All Tenders**
2. Click **Create** or link from a CRM opportunity
3. Fill in tender details (number, title, category, deadline)
4. Add BoQ lines with products and quantities

### Managing RFQs

1. Open a tender in Financial Study stage
2. Click **Create RFQ (Purchase Agreement)**
3. System creates Purchase Agreement with BoQ items
4. Send to vendors and collect quotations
5. Use **Compare Vendors** to analyze offers

### Generating Quotations

1. Click **Prepare Quotation** after vendor selection
2. Click **Generate Sales Quotation**
3. Set margin percentage and configuration
4. Review preview and generate
5. Submit to customer

### Creating Projects

1. Mark tender as **Won**
2. Click **Create Project**
3. Configure project settings
4. System creates project with tasks from BoQ

## Configuration

### Tender Stages

Configure stages at: **Tender Management > Configuration > Tender Stages**

Default stages:
- Draft
- Technical Study
- Financial Study
- Quotation Prepared
- Submitted
- Under Evaluation
- Won
- Lost
- Cancelled

### Security Groups

- **Tender User**: Can create and manage own tenders
- **Tender Manager**: Full access to all tenders and configuration

## Reports

- **Tender Report**: Complete tender information and financial summary
- **Tender BoQ**: Detailed Bill of Quantities with pricing

## Support

**iCloud Solutions**

- Website: [icloud-solutions.net](https://icloud-solutions.net)
- Email: contact@icloud-solutions.net
- WhatsApp: +216 50 271 737

## License

OPL-1 (Odoo Proprietary License)

## Price

€2,500

## Author

iCloud Solutions - Professional Odoo Implementation and Customization

---

For custom requirements, implementation support, or questions, please contact us.
