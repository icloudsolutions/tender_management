# ICS Tender Management - BPMN 2.0 Guide

**Version**: 18.0.2.0.0
**Date**: January 29, 2026
**Standard**: BPMN 2.0 (Business Process Model and Notation)

---

## 📋 What is BPMN?

**BPMN (Business Process Model and Notation)** is an international standard for modeling business processes. It provides a graphical notation that is:

- ✅ **Standardized**: ISO/IEC 19510:2013
- ✅ **Universal**: Understood by business and technical teams
- ✅ **Executable**: Can be deployed to workflow engines
- ✅ **Comprehensive**: Covers all process aspects

---

## 📁 BPMN Files Provided

### 1. TENDER_MANAGEMENT_BPMN.xml
**Type**: Full BPMN 2.0 XML Process Definition
**Size**: Complete workflow with all phases
**Use**: Import into BPMN tools, workflow engines, or documentation

**Contains**:
- ✅ Complete tender lifecycle (9 stages)
- ✅ Supply projects workflow (6 phases)
- ✅ O&M services workflow (6 phases)
- ✅ Decision gateways
- ✅ Message flows between participants
- ✅ Data objects
- ✅ Sequence flows
- ✅ Full documentation

---

## 🎯 Process Overview

### Main Process Elements

**Total Activities**: 35 tasks
**Gateways**: 3 decision points
**End Events**: 4 outcomes
**Participants**: 4 (Company, Customer, Vendors, Etimad)
**Message Flows**: 11 interactions

---

## 📊 Process Structure

```
START: Opportunity Identified
  ↓
PRE-AWARD PHASE (9 stages)
  ├─ Draft: Register Tender
  ├─ Technical Study: Create BoQ
  ├─ Financial Study: Collect Vendor Offers
  ├─ Quotation: Prepare Customer Quote
  ├─ Submission: Submit to Customer
  ├─ Evaluation: Under Review
  └─ Decision: Won/Lost/Cancelled
     ↓
  ┌──────────────┬─────────────┬────────────────┐
  │              │             │                │
  WON           LOST      CANCELLED          │
  │              │             │                │
  ↓              ↓             ↓                │
PROJECT TYPE   DOCUMENT    DOCUMENT            │
  │            LOSS      CANCELLATION          │
  ↓              │             │                │
  ├─────────┬────┼─────────────┘                │
  │         │    END         END                │
  │         │                                   │
SUPPLY    O&M                                  │
PROJECT   SERVICE                              │
  │         │                                   │
  ↓         ↓                                   │
6 PHASES  6 PHASES                             │
  │         │                                   │
  ↓         ↓                                   │
 END       END                                 │
```

---

## 🚀 How to Use This BPMN File

### Option 1: Visual Modeling Tools

**Free Tools**:
1. **Camunda Modeler** (Recommended)
   - Download: https://camunda.com/download/modeler/
   - Open: TENDER_MANAGEMENT_BPMN.xml
   - View: Visual diagram with all elements
   - Edit: Customize for your needs

2. **bpmn.io**
   - Website: https://demo.bpmn.io
   - Import: Upload XML file
   - View: Interactive diagram
   - Export: SVG, PNG images

3. **Visual Paradigm**
   - Website: https://online.visual-paradigm.com
   - Import: BPMN 2.0 file
   - View: Professional diagrams

**Commercial Tools**:
- Bizagi Modeler
- ARIS Express
- Enterprise Architect
- Signavio Process Manager

---

### Option 2: Workflow Engines (Executable)

**Deploy to Process Engines**:

#### Camunda BPM
```bash
# 1. Install Camunda
# 2. Deploy BPMN file
camunda-bpm-platform/webapps/camunda/app/

# 3. Start process instance
POST /process-definition/key/TenderManagementProcess/start

# 4. Monitor through Cockpit
http://localhost:8080/camunda/app/cockpit
```

#### Flowable
```bash
# 1. Install Flowable
# 2. Deploy via API
POST /repository/deployments
Content-Type: multipart/form-data
File: TENDER_MANAGEMENT_BPMN.xml

# 3. Start process
POST /runtime/process-instances
{
  "processDefinitionKey": "TenderManagementProcess",
  "variables": []
}
```

#### Activiti
```bash
# 1. Deploy to Activiti
# 2. Use Activiti Explorer
# 3. Start process instance
```

---

### Option 3: Documentation & Analysis

**Generate Documentation**:

#### Using Camunda Modeler
1. Open TENDER_MANAGEMENT_BPMN.xml
2. File → Export → SVG/PNG
3. Use images in presentations

#### Using BPMN Analytics
1. Import to analysis tool
2. Calculate:
   - Process complexity
   - Average completion time
   - Bottleneck identification
   - Resource requirements

#### Using Documentation Generators
1. **BPMN to HTML**:
   ```bash
   # Use bpmn-to-html converter
   npm install bpmn-to-html
   bpmn-to-html TENDER_MANAGEMENT_BPMN.xml
   ```

2. **BPMN to PDF**:
   - Use Camunda Modeler → Print → PDF
   - High-quality documentation

---

## 📖 Understanding the Process

### Key Elements Explained

#### 1. Start Event (Circle)
- **Symbol**: ⭕ Empty circle
- **Name**: "Opportunity Identified"
- **Trigger**: New tender opportunity discovered

#### 2. User Tasks (Rounded Rectangle)
- **Symbol**: 📋 Rectangle with person icon
- **Examples**:
  - "Register Tender"
  - "Conduct Technical Study"
  - "Compare Vendor Offers"
- **Action**: Requires human interaction

#### 3. Service Tasks (Rounded Rectangle with Gear)
- **Symbol**: ⚙️ Rectangle with gear icon
- **Example**: "Send RFQ to Vendors"
- **Action**: Automated system task

#### 4. Exclusive Gateway (Diamond)
- **Symbol**: ◇ Diamond with X
- **Examples**:
  - "Quotation Approved?"
  - "Tender Decision?"
  - "Project Type?"
- **Action**: Makes decisions (only one path)

#### 5. End Events (Circle with Thick Border)
- **Symbol**: ⭕ Thick circle
- **Examples**:
  - "Supply Project Complete"
  - "O&M Project Complete"
  - "Tender Lost"
  - "Tender Cancelled"

#### 6. Sequence Flows (Arrows)
- **Symbol**: → Solid arrow
- **Action**: Shows process flow direction

#### 7. Message Flows (Dashed Arrows)
- **Symbol**: ⇢ Dashed arrow
- **Examples**:
  - Company → Vendors: "RFQ"
  - Vendors → Company: "Quotations"
  - Company → Etimad: "Tender Submission"

---

## 🎨 Visual Representation

### Process Swimlanes

```
┌─────────────────────────────────────────────────────────────┐
│ COMPANY (Internal)                                          │
├─────────────────────────────────────────────────────────────┤
│ [Register] → [Technical] → [Financial] → [Quotation] →     │
│ [Submit] → [Evaluation] → [Decision]                       │
│            ↓                                                │
│    [Supply Project] or [O&M Service]                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ VENDORS/SUPPLIERS                                           │
├─────────────────────────────────────────────────────────────┤
│ [Receive RFQ] → [Submit Quotation] → [Receive PO] →       │
│ [Deliver Materials]                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CUSTOMER (Government Entity)                                │
├─────────────────────────────────────────────────────────────┤
│ [Receive Tender] → [Evaluate] → [Make Decision] →         │
│ [Award Letter] → [Receive Delivery] → [Make Payment]      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ETIMAD PLATFORM                                             │
├─────────────────────────────────────────────────────────────┤
│ [Receive Submission] → [Track Evaluation] →                │
│ [Process Invoice] → [Facilitate Payment]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Process Metrics

### Complexity Analysis

**Total Activities**: 35
- User Tasks: 32
- Service Tasks: 1
- Gateways: 3

**Process Paths**: 3 main outcomes
1. Won → Supply Project (6 phases) → Complete
2. Won → O&M Service (6 phases) → Complete
3. Lost/Cancelled → Archive

**Average Duration**:
- Pre-Award Phase: 2-8 weeks
- Supply Project: 3-12 months
- O&M Service: 6-36 months

**Participants**: 4
- Internal (Company)
- External (Customer, Vendors, Platform)

**Message Exchanges**: 11 interactions

---

## 🔄 Process Variations

### Supply Projects (6 Phases)

```
Phase 1: Project Receipt          [2-4 weeks]
Phase 2: Contracting              [2-4 weeks]
Phase 3: Supply Execution         [4-20 weeks]
Phase 4: Preliminary Handover     [1-2 weeks]
Phase 5: Final Handover           [1-4 weeks]
Phase 6: Invoicing & Closure      [2-8 weeks]

Total Duration: 3-12 months
```

### O&M Services (6 Phases + Loop)

```
Phase 1: Kickoff                  [2-4 weeks]
Phase 2: Planning                 [2-3 weeks]
Phase 3: Execution                [Ongoing]
Phase 4: Monitoring               [Parallel with Phase 3]
Phase 5: Invoicing                [Monthly/Quarterly]
         ↓
    [Contract End?]
         ↓ No: Loop to Phase 3
         ↓ Yes: Phase 6
Phase 6: Handover & Closure       [4-8 weeks]

Total Duration: 6-36 months
```

---

## 🛠️ Customization Guide

### How to Modify the BPMN

#### 1. Add New Task
```xml
<userTask id="Task_NewActivity" name="New Activity Name">
  <incoming>Flow_In</incoming>
  <outgoing>Flow_Out</outgoing>
  <documentation>Activity description</documentation>
</userTask>

<sequenceFlow id="Flow_In" sourceRef="PreviousTask" targetRef="Task_NewActivity"/>
<sequenceFlow id="Flow_Out" sourceRef="Task_NewActivity" targetRef="NextTask"/>
```

#### 2. Add New Gateway
```xml
<exclusiveGateway id="Gateway_NewDecision" name="Decision Name?">
  <incoming>Flow_In</incoming>
  <outgoing>Flow_Path1</outgoing>
  <outgoing>Flow_Path2</outgoing>
</exclusiveGateway>

<sequenceFlow id="Flow_Path1" name="Option 1" sourceRef="Gateway_NewDecision" targetRef="Task1">
  <conditionExpression xsi:type="tFormalExpression">
    condition == 'option1'
  </conditionExpression>
</sequenceFlow>
```

#### 3. Add New End Event
```xml
<endEvent id="EndEvent_NewOutcome" name="New Outcome">
  <incoming>Flow_In</incoming>
</endEvent>
```

#### 4. Add Message Flow
```xml
<messageFlow id="MessageFlow_NewMessage"
             name="Message Name"
             sourceRef="Task_Source"
             targetRef="Participant_Target"/>
```

---

## 📚 Integration with Odoo

### How This BPMN Maps to Odoo

#### BPMN Elements → Odoo Implementation

| BPMN Element | Odoo Implementation |
|--------------|---------------------|
| **Process** | `ics.tender` model with workflow |
| **User Tasks** | Form views with buttons |
| **Gateways** | State transitions with conditions |
| **Data Objects** | Related models (BoQ, Offers, etc.) |
| **Message Flows** | Email templates, notifications |
| **Participants** | User groups, partners |
| **Sequence Flows** | State field changes |

#### Example Mapping

**BPMN Task**: "Register Tender (Draft Stage)"
**Odoo Implementation**:
```python
# Model: ics.tender
# State: 'draft'
# View: tender_form_view
# Button: "Start Technical Study"
# Transition: draft → technical
```

**BPMN Gateway**: "Quotation Approved?"
**Odoo Implementation**:
```python
# Method: action_approve_quotation()
# If approved:
#     self.state = 'quotation'
# Else:
#     self.state = 'financial'  # Revise
```

---

## 📊 Analytics & Reporting

### Process Analytics

**Key Performance Indicators (KPIs)**:

1. **Cycle Time**
   - Pre-Award: Draft → Won/Lost
   - Post-Award: Won → Project Complete

2. **Throughput**
   - Number of tenders processed per month
   - Number of projects completed per quarter

3. **Success Rate**
   - Win rate percentage
   - Loss rate percentage
   - Cancellation rate

4. **Resource Utilization**
   - User task duration
   - Bottleneck identification
   - Team productivity

5. **Compliance**
   - Procedure adherence percentage
   - Phase completion rate

**Export Process Data**:
```sql
-- Example: Get average tender duration by stage
SELECT
    stage_id.name,
    AVG(EXTRACT(DAY FROM (write_date - create_date))) as avg_days
FROM ics_tender
GROUP BY stage_id;
```

---

## 🎓 Training Materials

### Using BPMN for Training

#### 1. Process Walkthrough
- Print BPMN diagram (large format)
- Use in training sessions
- Walk through each path
- Explain decision points

#### 2. Role-Based Training
- Highlight relevant tasks per role
- Show message flows
- Explain hand-offs

#### 3. Scenario Exercises
- Use BPMN to simulate scenarios
- "What if" analysis
- Exception handling

---

## 🔍 Validation & Testing

### Process Validation

**Validate BPMN File**:

#### Using Camunda Modeler
1. Open file
2. Check for errors (red markers)
3. Validate against BPMN 2.0 schema
4. Fix any issues

#### Using Online Validators
1. Visit: https://www.bpmn-sketch-miner.ai/
2. Upload XML
3. Check validation results

#### Using Command Line
```bash
# Install bpmn-js validator
npm install -g bpmn-js-cli

# Validate file
bpmn-js validate TENDER_MANAGEMENT_BPMN.xml
```

---

## 📞 Support

### Getting Help

**BPMN Standard**:
- Official Spec: https://www.omg.org/spec/BPMN/2.0/
- Tutorial: https://camunda.com/bpmn/

**Tools Support**:
- Camunda Forum: https://forum.camunda.io/
- BPMN.io: https://github.com/bpmn-io

**ICS Implementation**:
- Email: contact@icloud-solutions.net
- Website: https://icloud-solutions.net

---

## 📝 Change Log

### Version 18.0.2.0.0 (January 29, 2026)
- ✅ Initial BPMN 2.0 creation
- ✅ Complete tender lifecycle
- ✅ Supply projects workflow (6 phases)
- ✅ O&M services workflow (6 phases)
- ✅ All decision gateways
- ✅ Message flows
- ✅ Data objects
- ✅ Full documentation

---

## 🎯 Next Steps

1. **Download BPMN Tool**
   - Get Camunda Modeler (free)
   - Install on your computer

2. **Open BPMN File**
   - Open TENDER_MANAGEMENT_BPMN.xml
   - Explore the diagram
   - Read task documentation

3. **Customize (Optional)**
   - Modify for your specific needs
   - Add company-specific tasks
   - Adjust timelines

4. **Use for Training**
   - Print diagram
   - Use in training sessions
   - Create training materials

5. **Consider Automation**
   - Evaluate workflow engines
   - Plan automation strategy
   - Implement if needed

---

## 🏆 Best Practices

### BPMN Modeling Tips

1. **Keep It Simple**
   - Start with main flow
   - Add complexity gradually
   - Use sub-processes for detail

2. **Use Clear Names**
   - Verb + Object format
   - "Approve Quotation" not "Quotation"
   - Be specific and descriptive

3. **Document Everything**
   - Add documentation to all tasks
   - Explain decision criteria
   - Note business rules

4. **Validate Regularly**
   - Check syntax
   - Test logic
   - Get stakeholder feedback

5. **Version Control**
   - Track changes
   - Use meaningful commit messages
   - Maintain change log

---

## 📦 Deliverables

### What You Have

```
✅ TENDER_MANAGEMENT_BPMN.xml
   - Full BPMN 2.0 XML file
   - 35 activities
   - 3 gateways
   - 4 end events
   - 11 message flows
   - Complete documentation

✅ BPMN_GUIDE.md (this file)
   - How to use BPMN file
   - Tool recommendations
   - Customization guide
   - Integration guide
   - Best practices

✅ Compatible with:
   - Camunda BPM
   - Flowable
   - Activiti
   - jBPM
   - Any BPMN 2.0 tool
```

---

## 🎉 Conclusion

You now have a **professional, standards-compliant BPMN 2.0 process model** that:

✅ Documents complete workflow
✅ Meets international standards
✅ Can be imported to tools
✅ Executable in workflow engines
✅ Perfect for training
✅ Great for documentation
✅ Supports process improvement

**Start exploring your BPMN process model today!** 🚀

---

**BPMN 2.0 Process Model**
**ICS Tender Management v18.0.2.0.0**
**iCloud Solutions**

*Professional Business Process Modeling* ⭐
