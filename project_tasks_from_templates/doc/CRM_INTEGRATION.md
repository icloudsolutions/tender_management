# CRM Integration - Auto-create Projects from Opportunities

## Overview

This module now supports automatic project creation from CRM opportunities when they reach specific stages. This integration allows you to streamline your workflow by automatically generating projects with predefined tasks when deals progress through your sales pipeline.

## Features

### 1. Configurable Auto-creation in Project Templates

- **Auto-create Project from CRM**: Enable/disable automatic project creation per template
- **CRM Stage Trigger**: Select which CRM stage should trigger the project creation
- **Template-based Creation**: All tasks and stages from the template are automatically created in the new project

### 2. Automatic Project Creation Flow

When a CRM opportunity reaches the configured stage:
1. The system checks for templates configured for that stage
2. Creates a new project with name: `[Opportunity Name] - [Template Name]`
3. Links the project to the CRM opportunity
4. Creates all tasks from the template automatically
5. Assigns the project to the opportunity owner (if available)
6. Links the project to the opportunity's partner/customer

### 3. Bidirectional Linking

- **From CRM to Project**: View all projects created from an opportunity
- **From Project to CRM**: See which opportunity triggered the project creation
- **Smart Button**: Projects button on CRM opportunity shows count and provides quick access

## Configuration

### Step 1: Configure Project Template

1. Go to **Project → Configuration → Project Templates**
2. Create or edit a template
3. Open the **CRM Integration** tab
4. Enable **Auto-create Project from CRM**
5. Select the **CRM Stage** that should trigger project creation
6. Save the template

### Step 2: Set Up CRM Stages (Optional)

Go to **Settings → Project Templates** to enable:
- **Auto-create Project Template from CRM Stage**: Automatically creates project templates when CRM stages are created

## Usage

### Automatic Creation

Once configured, projects are created automatically:
1. Create or update a CRM opportunity
2. Move the opportunity to the configured stage
3. A project is created automatically with all tasks from the template
4. Access the project from the "Projects" button on the opportunity

### Manual Verification

After stage change:
- Check the "Projects" smart button on the opportunity
- Click to view all related projects
- Each project shows which template was used
- Projects maintain the link back to the opportunity

## Technical Details

### Models Enhanced

1. **project.task.template**
   - `crm_stage_id`: Stage that triggers auto-creation
   - `auto_create_project`: Enable/disable flag

2. **project.project**
   - `crm_lead_id`: Link back to the CRM opportunity

3. **crm.lead**
   - `project_ids`: All projects created from this opportunity
   - `project_count`: Number of linked projects
   - `action_view_projects()`: Action to view linked projects

### Auto-creation Logic

- Only creates one project per opportunity/template combination
- Prevents duplicate projects if stage is changed multiple times
- Respects the template configuration (only creates if enabled)
- Uses `sudo()` for reliable task creation

### Views Added

1. **CRM Lead Form View**: Added Projects button and projects page
2. **Project Form View**: Shows linked CRM opportunity (if exists)
3. **Project Template Form View**: CRM Integration configuration tab

## Examples

### Use Case 1: Sales to Delivery Pipeline

**Scenario**: When a deal is won, automatically create a delivery project

**Setup**:
1. Template: "Standard Delivery Project"
2. CRM Stage: "Won"
3. Tasks: Kickoff, Requirements, Development, Testing, Delivery

**Result**: When opportunity moves to "Won", delivery project is created automatically

### Use Case 2: Onboarding Process

**Scenario**: New customer onboarding when contract is signed

**Setup**:
1. Template: "Customer Onboarding"
2. CRM Stage: "Contract Signed"
3. Tasks: Welcome Email, Account Setup, Training Session, Follow-up

**Result**: Onboarding project starts automatically when contract is signed

### Use Case 3: Multiple Projects per Stage

**Scenario**: Create both delivery and support projects

**Setup**:
1. Template 1: "Delivery Project" → CRM Stage: "Won"
2. Template 2: "Support Setup" → CRM Stage: "Won"

**Result**: Both projects are created when opportunity reaches "Won" stage

## Best Practices

1. **Naming Convention**: Use clear template names that reflect their purpose
2. **Stage Selection**: Choose stages that represent clear decision points
3. **Task Organization**: Structure templates with logical task hierarchies
4. **User Assignment**: Pre-assign users in templates when possible
5. **Testing**: Test with non-critical opportunities first

## Troubleshooting

### Projects Not Creating Automatically

**Check**:
- Template has "Auto-create Project from CRM" enabled
- Correct CRM stage is selected in template
- Opportunity actually changed to that stage (not just updated)
- CRM module is installed and active

### Duplicate Projects

- The system prevents duplicates automatically
- Each opportunity/template pair only creates one project
- Moving back and forth between stages won't create duplicates

### Missing Tasks

- Verify template has tasks defined
- Check that tasks are properly configured in template
- Ensure proper access rights for task creation

## Notes

- CRM module is optional; features only work when CRM is installed
- All CRM-related functionality gracefully degrades without CRM
- Projects can still be created manually if auto-creation is disabled
- The link between project and opportunity is permanent and read-only
