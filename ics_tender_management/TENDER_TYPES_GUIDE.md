# Tender Types Guide - Single Vendor vs Product-wise Selection

## 📋 Overview

ICS Tender Management now supports **two tender execution modes** based on the flowchart workflow:

- **Path A**: Single Vendor for All Products
- **Path B**: Product-wise Vendor Selection

This feature allows you to choose the procurement strategy that best fits each tender's requirements.

---

## 🎯 Tender Type Selection

### Where to Configure

**Location**: Tender Form → Main Info Tab → **Tender Type** (Radio buttons)

**When to Set**: During tender creation or in Draft/Technical Study stages

**Options**:
1. ✅ **Single Vendor for All Products** (Default)
2. ✅ **Product-wise Vendor Selection**

---

## 📊 Path A: Single Vendor for All Products

### Description

In this mode, **ONE vendor** is selected to supply **ALL products** in the tender. This is the traditional procurement approach for consolidated purchases.

### Business Rules

| Rule | Description |
|------|-------------|
| **Vendor Selection** | ALL products must be assigned to the SAME vendor |
| **Price Requirement** | ALL product prices are **mandatory** |
| **Purchase Orders** | Creates **1 single PO** for the entire tender |
| **Validation** | System validates that all items have the same vendor before PO creation |

### When to Use

✅ **Best for**:
- Supply tenders with single source requirement
- Small to medium tenders
- When consolidation is needed for better pricing/logistics
- Tenders with delivery/quality consistency requirements
- Framework agreements with preferred vendors

❌ **Not suitable for**:
- Large diverse tenders
- Multiple specialized products
- When best price per item is critical
- Tenders requiring vendor diversification

### Workflow

```
1. Create Tender → Select "Single Vendor for All Products"
   ↓
2. Add BoQ Lines (all products)
   ↓
3. Create RFQ (Purchase Agreement) → Send to vendors
   ↓
4. Vendors submit offers for ALL products
   ↓
5. Compare Vendors Wizard:
   - Select ONE vendor for everything
   - Click "Auto-Select Best" (finds cheapest total)
   - System validates vendor has offers for ALL items
   ↓
6. Create Purchase Order → Creates 1 PO with all products
   ↓
7. Generate Quotation → One quotation for customer
```

### Vendor Comparison - Single Vendor Mode

**Interface Changes**:
- 🔵 Blue alert: "Single Vendor Mode: You must select ONE vendor for ALL products"
- Vendor Selection Dropdown (top of wizard)
- **"Auto-Select Best"** button (magic wand icon)

**How to Use**:

**Option 1: Manual Selection**
```
1. Open Compare Vendors wizard
2. Review vendor offers for each product
3. Select ONE vendor from dropdown at top
4. Click "Apply Selected Vendor"
```

**Option 2: Automatic Selection**
```
1. Open Compare Vendors wizard
2. Click "Auto-Select Best" button
3. System calculates total for each common vendor
4. Selects vendor with LOWEST total price
5. Shows notification with selected vendor and total
6. Click "Apply Selected Vendor"
```

**Validation**:
- ❌ Error if selected vendor doesn't have offers for ALL products
- ❌ Error if trying to create PO without complete vendor selection
- ✅ Success if vendor has submitted offers for 100% of items

### Creating Purchase Order

**Button**: "Create Purchase Order(s)" (in Financial/Quotation stages)

**Behavior**:
- Validates all products assigned to same vendor
- Creates **1 Purchase Order** with all BoQ lines
- PO origin shows tender reference
- Auto-populates quantities and prices from selection

**Example**:
```
Tender TND-2024-001: Supply of Office Equipment
- 10 Laptops → Vendor A @ 5,000 SAR each
- 20 Monitors → Vendor A @ 1,500 SAR each
- 5 Printers → Vendor A @ 3,000 SAR each

Result: 1 PO to Vendor A for 95,000 SAR total
```

---

## 🔀 Path B: Product-wise Vendor Selection

### Description

In this mode, **different vendors** can be selected for **different products**. Each item goes to the most competitive vendor, maximizing cost savings.

### Business Rules

| Rule | Description |
|------|-------------|
| **Vendor Selection** | Each product can have a DIFFERENT vendor |
| **Price Requirement** | Product prices are **optional** (flexible) |
| **Purchase Orders** | Creates **MULTIPLE POs** (one per vendor) |
| **Validation** | At least one product must have a vendor selected |

### When to Use

✅ **Best for**:
- Large tenders with diverse products
- Maximum cost optimization required
- Products from different categories (IT, Furniture, Supplies)
- Multiple specialized vendors
- When vendor diversification is strategic
- Split-award tenders

❌ **Not suitable for**:
- Single-source requirements
- When vendor consolidation is mandated
- Framework agreements
- Small simple purchases

### Workflow

```
1. Create Tender → Select "Product-wise Vendor Selection"
   ↓
2. Add BoQ Lines (diverse products)
   ↓
3. Create RFQ (Purchase Agreement) → Send to multiple vendors
   ↓
4. Vendors submit offers (each vendor can quote some/all items)
   ↓
5. Compare Vendors Wizard:
   - System auto-selects BEST vendor per product
   - Review and adjust if needed
   - Can leave some products without vendor (optional)
   ↓
6. Create Purchase Orders → Creates MULTIPLE POs
   - One PO per vendor
   - Each PO contains only that vendor's products
   ↓
7. Generate Quotation → One consolidated quotation for customer
```

### Vendor Comparison - Product-wise Mode

**Interface Changes**:
- 🟢 Green alert: "Product-wise Mode: You can select different vendors for each product"
- No single vendor dropdown
- Best vendor auto-selected per line

**How to Use**:

```
1. Open Compare Vendors wizard
2. System automatically shows BEST vendor per product
3. Review the automatic selections:
   - Green rows: Best offer selected
   - Savings column shows cost reduction
4. Optional: Click "View All Offers" on any line to:
   - See competing offers
   - Manually select different vendor
   - Override automatic selection
5. Click "Apply Best Vendors per Product"
```

**Features**:
- 📊 Automatic best price selection
- 💰 Savings calculation per product
- 🔍 "View All Offers" button per line
- ✅ Optional product selection (can skip items)

### Creating Purchase Orders

**Button**: "Create Purchase Order(s)" (in Financial/Quotation stages)

**Behavior**:
- Groups products by selected vendor
- Creates **MULTIPLE Purchase Orders**
- One PO per vendor
- Each PO contains only that vendor's products
- Opens tree view if multiple POs created

**Example**:
```
Tender TND-2024-002: Supply of Mixed Equipment
- 10 Laptops → Vendor A @ 4,500 SAR each = 45,000 SAR
- 20 Monitors → Vendor B @ 1,200 SAR each = 24,000 SAR
- 5 Printers → Vendor C @ 2,500 SAR each = 12,500 SAR

Result:
- PO-001 to Vendor A: 45,000 SAR (Laptops)
- PO-002 to Vendor B: 24,000 SAR (Monitors)
- PO-003 to Vendor C: 12,500 SAR (Printers)
Total: 81,500 SAR (vs 95,000 SAR in single vendor mode = 14% savings!)
```

---

## 🎨 Visual Indicators

### BoQ Lines Tree View

The BoQ list uses color coding to show vendor selection status:

| Color | Meaning | Tender Type |
|-------|---------|-------------|
| 🟢 **Green** | Vendor selected | Both modes |
| 🟡 **Yellow/Warning** | No vendor (required!) | Single Vendor mode |
| 🔵 **Blue/Info** | No vendor (optional) | Product-wise mode |

**Columns**:
- Selected Vendor
- Selected Vendor Price
- **Offers** (NEW) - Number of vendor offers received

### Tender Form View

**Tender Type Field**:
- Radio buttons (horizontal layout)
- Shown prominently in main info group
- Read-only after Technical Study stage
- Clear labels with descriptions

---

## 🔄 Comparison Matrix

| Feature | Single Vendor | Product-wise |
|---------|--------------|--------------|
| **Vendors per Tender** | 1 | Multiple |
| **Price Requirements** | All Mandatory | Optional |
| **Purchase Orders** | 1 PO | Multiple POs |
| **Best for Savings** | ❌ | ✅ |
| **Best for Consolidation** | ✅ | ❌ |
| **Vendor Comparison** | Select one for all | Select best per product |
| **Logistics** | Simpler (one delivery) | Complex (multiple deliveries) |
| **Risk Diversification** | Low | High |
| **Setup Complexity** | Simple | Medium |

---

## 📝 Step-by-Step Examples

### Example 1: Single Vendor Mode

**Scenario**: Government office supply tender - need consistent supplier

```
Step 1: Create Tender
- Tender Number: TND-2024-100
- Title: "Annual Office Supplies"
- Category: Supply
- Tender Type: ✅ "Single Vendor for All Products"

Step 2: Add BoQ
- Paper A4 (100 boxes)
- Pens (500 pieces)
- Folders (200 pieces)
- Staplers (50 pieces)

Step 3: Create RFQ
- Send to: Vendor A, Vendor B, Vendor C
- All vendors quote ALL items

Step 4: Vendor Offers Received
Vendor A Total: 15,000 SAR
Vendor B Total: 14,500 SAR ← Best
Vendor C Total: 15,800 SAR

Step 5: Compare Vendors
- Open wizard
- Click "Auto-Select Best"
- System selects: Vendor B (14,500 SAR)
- Review and confirm
- Click "Apply Selected Vendor"

Step 6: Create PO
- Click "Create Purchase Order(s)"
- System creates: PO-001 to Vendor B
- All 4 products in one PO
- Total: 14,500 SAR

Step 7: Generate Quotation
- Add margin 20%
- Customer quotation: 17,400 SAR
- Submit tender
```

### Example 2: Product-wise Mode

**Scenario**: IT Infrastructure tender - specialized vendors

```
Step 1: Create Tender
- Tender Number: TND-2024-200
- Title: "IT Infrastructure Upgrade"
- Category: Supply
- Tender Type: ✅ "Product-wise Vendor Selection"

Step 2: Add BoQ
- Servers (5 units) - Dell/HP specialized
- Network Switches (10 units) - Cisco/Juniper specialized
- Workstations (50 units) - Various brands
- Software Licenses (50 units) - Software vendors

Step 3: Create RFQ
- Send to:
  - Server Vendor (Dell)
  - Network Vendor (Cisco)
  - Workstation Vendor (Local distributor)
  - Software Vendor (Microsoft partner)

Step 4: Vendor Offers
Each vendor quotes their specialty items:
- Dell: Servers only @ 50,000 SAR total
- Cisco: Switches only @ 80,000 SAR total
- HP competitor: Servers @ 55,000 SAR (higher)
- Juniper: Switches @ 85,000 SAR (higher)
- Local: Workstations @ 125,000 SAR total
- Software: Licenses @ 45,000 SAR total

Step 5: Compare Vendors (Auto)
- System auto-selects BEST per product:
  ✅ Servers → Dell @ 50,000 SAR (5K savings vs HP)
  ✅ Switches → Cisco @ 80,000 SAR (5K savings vs Juniper)
  ✅ Workstations → Local @ 125,000 SAR
  ✅ Licenses → Software @ 45,000 SAR
- Total: 300,000 SAR
- Savings: 10,000 SAR vs non-optimal selection
- Click "Apply Best Vendors per Product"

Step 6: Create POs
- Click "Create Purchase Order(s)"
- System creates 4 POs:
  - PO-001 to Dell: 50,000 SAR
  - PO-002 to Cisco: 80,000 SAR
  - PO-003 to Local: 125,000 SAR
  - PO-004 to Software: 45,000 SAR
- Total: 300,000 SAR across 4 vendors

Step 7: Generate Quotation
- Add margin 15%
- Customer quotation: 345,000 SAR
- Submit tender

Result: Maximum savings + Best quality per category!
```

---

## ⚙️ Configuration & Settings

### No Additional Configuration Required!

The tender type feature works out-of-the-box with default settings.

### Permissions

**User Access**:
- Tender Users: Can view and select tender type
- Tender Managers: Can change tender type until Technical Study
- System Admin: Can change anytime (not recommended)

**Security**:
- Tender type read-only after Technical Study stage
- Prevents accidental changes mid-process
- Validation enforced at PO creation

---

## 🚨 Common Errors & Solutions

### Error: "Single Vendor Mode requires all products to be assigned"

**Cause**: Not all BoQ lines have a selected vendor

**Solution**:
1. Open Compare Vendors wizard
2. Ensure vendor selected for ALL items
3. Use "Auto-Select Best" button
4. Verify selection applied to all lines

### Error: "Single Vendor Mode requires all products to use the same vendor"

**Cause**: Different vendors selected for different products

**Solution**:
1. Open Compare Vendors wizard
2. Select ONE vendor at top
3. Click "Apply Selected Vendor"
4. All products now use same vendor

### Error: "Vendor X has no offer for product: Y"

**Cause**: Selected vendor didn't quote all products (Single Vendor mode)

**Solution**:
- Option 1: Request vendor to quote missing items
- Option 2: Select different vendor with complete offer
- Option 3: Switch to Product-wise mode

### Error: "Please select vendors for at least one product"

**Cause**: No vendor selected for any product (Product-wise mode)

**Solution**:
1. Open Compare Vendors wizard
2. System auto-selects best vendors
3. Click "Apply Best Vendors per Product"
4. Or manually select vendors per line

---

## 🎓 Best Practices

### For Single Vendor Mode

✅ **Do**:
- Request complete quotes from vendors
- Verify vendor can supply ALL items
- Use "Auto-Select Best" for objective selection
- Consider total cost of ownership (TCO)
- Negotiate volume discounts

❌ **Don't**:
- Mix vendor selection (system prevents this)
- Skip vendor validation
- Forget to check delivery capabilities
- Ignore vendor capacity constraints

### For Product-wise Mode

✅ **Do**:
- Allow specialized vendors per category
- Use automatic best price selection
- Review savings calculations
- Coordinate deliveries across vendors
- Set clear delivery schedules per PO

❌ **Don't**:
- Over-complicate for small tenders
- Ignore logistics complexity
- Skip vendor capability assessment
- Forget to consolidate customer quotation

---

## 📊 Reporting & Analytics

### Available Reports

**Vendor Comparison Report**:
- Shows all offers per product
- Highlights best prices
- Calculates savings
- Export to Excel

**Purchase Order Summary**:
- Lists all POs per tender
- Groups by vendor
- Shows totals per vendor
- Tender type indicator

**Savings Analysis**:
- Estimated cost vs selected vendor cost
- Savings amount and percentage
- Per product breakdown
- Overall tender savings

---

## 🔌 Integration Points

### With Existing Modules

**CRM Integration**:
- Tender type captured from lead/opportunity
- Historical tender type analysis per customer
- Win rate by tender type

**Purchase Module**:
- RFQ creation respects tender type
- PO creation follows tender type rules
- Vendor performance tracking per type

**Project Module**:
- Project tasks created from POs
- Task grouping by vendor (product-wise mode)
- Delivery tracking per PO

**Sales Module**:
- Quotation consolidated regardless of tender type
- Customer sees one unified quote
- Internal costs tracked separately

---

## 🚀 Future Enhancements

### Planned Features (Next Version)

1. **Hybrid Mode**:
   - Group products into lots
   - Single vendor per lot
   - Best of both worlds

2. **Advanced Auto-Selection**:
   - Consider delivery time
   - Factor in vendor rating
   - Weight quality vs price
   - Multi-criteria decision analysis (MCDA)

3. **Vendor Portal**:
   - Vendors see tender type
   - Guided bidding per type
   - Completeness validation

4. **Analytics Dashboard**:
   - Tender type trends
   - Success rates per type
   - Average savings comparison
   - Vendor performance matrix

---

## 📞 Support & Questions

### Need Help?

**Documentation**:
- Full user guide: README.md
- Technical docs: DOCUMENTATION.md
- Workflow guide: WORKFLOW_IMPLEMENTATION_STATUS.md

**Support Channels**:
- 📧 Email: contact@icloud-solutions.net
- 📱 WhatsApp: +216 50 271 737
- 🌐 Website: https://icloud-solutions.net

**Training**:
- 2 hours included with purchase
- Video tutorials available
- On-site training available (additional cost)

---

## 📄 Appendix

### Technical Details

**Models Modified**:
- `ics.tender` - Added `tender_type` field
- `ics.tender.boq.line` - Added `tender_type` related field, `offer_count` computed field
- `ics.tender.vendor.comparison.wizard` - Added mode-specific logic

**New Methods**:
- `action_create_purchase_orders()` - Smart PO creation
- `_create_single_purchase_order()` - Single vendor logic
- `_create_multiple_purchase_orders()` - Product-wise logic
- `_validate_vendor_selection()` - Validation helper
- `action_select_best_common_vendor()` - Auto-selection for single vendor mode

**Views Modified**:
- Tender form: Added tender type radio buttons
- Vendor comparison wizard: Mode-aware interface
- BoQ tree: Color decorations for vendor status

**Business Rules Enforced**:
- Tender type immutable after Technical Study
- Single vendor validation at PO creation
- Product-wise requires minimum one vendor
- Common vendor must have complete offers

---

*Document Version: 1.0*
*Date: 2024-01-29*
*Author: iCloud Solutions*
*Module: ICS Tender Management v18.0.2.0.0*

**Last Updated**: January 29, 2024
**Status**: Production Ready
**Tested**: ✅ Yes
**Documented**: ✅ Yes
