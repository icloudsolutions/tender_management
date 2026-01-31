# Project Templates Integration Guide

## Overview

The `ics_tender_management` module integrates seamlessly with the `project_tasks_from_templates` module to provide flexible project creation from templates.

---

## Integration Architecture

### **Dual Template System**

The module supports **two template systems**:

1. **ICS Native Templates** (`ics.project.task.template`)
   - Custom templates designed for tender categories
   - Direct integration with tender management
   - Category-specific (توريد, صيانة و تشغيل, etc.)

2. **Project Tasks From Templates** (`project.task.template`)
   - Third-party module templates
   - More advanced features (stages, subtasks)
   - Used as fallback when ICS templates not available

---

## Template Selection Priority

When a tender is marked as "Won", the system follows this priority:

```
1. ICS Template (Exact Category Match)
   ↓ If not found
2. ICS Template (General/No Category)
   ↓ If not found
3. Project Tasks From Templates (Category Match)
   ↓ If not found
4. Project Tasks From Templates (Any Template)
   ↓ If not found
5. Create Project Without Tasks
```

---

## Category Mapping

### **Tender Categories → Template Names**

| Tender Category | Template Search Terms |
|----------------|----------------------|
| **Supply (توريد)** | supply, توريد, توريدات |
| **Maintenance (صيانة و تشغيل)** | maintenance, صيانة, تشغيل, صيانة و تشغيل |
| **Services** | service, services, خدمات |
| **Construction** | construction, إنشاء, بناء |
| **Consulting** | consulting, استشار, استشارات |

---

## How It Works

### **Scenario 1: ICS Template Available**

```
Tender Won (Category: Supply)
    ↓
Search: ics.project.task.template (category='supply')
    ↓
Found: "Supply Projects Template"
    ↓
Create Project
    ↓
Create Tasks from ICS Template
    ↓
✅ Project with 9 predefined tasks
```

### **Scenario 2: Using Project Tasks From Templates**

```
Tender Won (Category: Maintenance)
    ↓
Search: ics.project.task.template (category='maintenance')
    ↓
Not Found
    ↓
Search: project.task.template (name ilike 'maintenance')
    ↓
Found: "Maintenance & Operation Template"
    ↓
Create Project with project_template_id
    ↓
Call: project.action_create_project_from_template()
    ↓
✅ Project with tasks from project_tasks_from_templates
```

---

## Code Integration

### **Key Methods**

#### `_auto_create_project()`
Main method that orchestrates template selection and project creation.

```python
def _auto_create_project(self):
    # Priority 1: ICS template (exact category)
    template = self.env['ics.project.task.template'].search([
        ('tender_category', '=', self.tender_category),
        ('active', '=', True)
    ], limit=1)
    
    # Priority 2: ICS template (general)
    if not template:
        template = self.env['ics.project.task.template'].search([
            ('tender_category', '=', False),
            ('active', '=', True)
        ], limit=1)
    
    # Priority 3: Project Tasks From Templates
    if not template and 'project.task.template' in self.env:
        project_template = self._find_project_template()
        if project_template:
            return self._create_project_with_template_module(project_template)
    
    # Create project with ICS template
    # ...
```

#### `_create_project_with_template_module()`
Creates project using `project_tasks_from_templates` module.

```python
def _create_project_with_template_module(self, template):
    project_vals = {
        'name': f"Project - {self.tender_title}",
        'partner_id': self.partner_id.id,
        'user_id': self.user_id.id,
        'tender_id': self.id,
        'project_template_id': template.id,  # Link to template
        'date_start': fields.Date.today(),
    }
    
    project = self.env['project.project'].create(project_vals)
    
    # Use module's method to create tasks
    if hasattr(project, 'action_create_project_from_template'):
        project.action_create_project_from_template()
    
    return project
```

---

## Template Features Comparison

| Feature | ICS Templates | Project Tasks From Templates |
|---------|---------------|------------------------------|
| **Model** | `ics.project.task.template` | `project.task.template` |
| **Task Lines** | `ics.project.task.template.line` | `project.sub.task` |
| **Stages** | ❌ No | ✅ Yes (`project.stage`) |
| **Subtasks** | ❌ No | ✅ Yes (recursive) |
| **Category Filter** | ✅ Yes | ❌ No |
| **Delay Days** | ✅ Yes | ❌ No |
| **Priority** | ✅ Yes | ✅ Yes |
| **Assignees** | ✅ Yes | ✅ Yes |
| **Description** | ✅ HTML | ✅ HTML |

---

## Configuration

### **Using ICS Templates (Recommended)**

1. Go to: **Tender Management → Configuration → Project Task Templates**
2. Create templates for each category:
   - Supply Projects Template (category: Supply)
   - Maintenance & Operation Template (category: Maintenance)
   - General Project Template (no category)
3. Add task lines with:
   - Task name
   - Description
   - Planned hours
   - Delay days
   - Priority
   - Assignee

### **Using Project Tasks From Templates**

1. Install `project_tasks_from_templates` module
2. Go to: **Project → Configuration → Project Templates**
3. Create templates with names matching tender categories:
   - "Supply" or "توريد"
   - "Maintenance" or "صيانة و تشغيل"
   - etc.
4. Add tasks and stages as needed
5. System will automatically use these as fallback

---

## Benefits

### **Flexibility**
- ✅ Works with or without `project_tasks_from_templates`
- ✅ Supports both template systems
- ✅ Automatic fallback mechanism

### **Compatibility**
- ✅ No breaking changes if module not installed
- ✅ Graceful degradation
- ✅ Version-independent

### **User Experience**
- ✅ Automatic template selection
- ✅ No manual intervention needed
- ✅ Consistent project structure

---

## Troubleshooting

### **Issue: Templates Not Found**

**Symptoms:**
- Project created without tasks
- No template selected

**Solutions:**
1. Check if templates exist in ICS system
2. Verify template is active
3. Check category matching
4. If using `project_tasks_from_templates`, verify module installed
5. Check template names match search terms

### **Issue: Tasks Not Created**

**Symptoms:**
- Project created but no tasks

**Solutions:**
1. Verify template has task lines
2. Check `action_create_project_from_template()` method exists
3. Review logs for errors
4. Try manual task creation to test

### **Issue: Wrong Template Selected**

**Symptoms:**
- Project uses incorrect template

**Solutions:**
1. Check template category matches tender category
2. Verify template sequence/priority
3. Review template search logic
4. Check for multiple templates with same category

---

## Best Practices

### **Template Naming**

**ICS Templates:**
- Use descriptive names: "Supply Projects Template"
- Set category correctly
- Mark as active

**Project Tasks From Templates:**
- Include category keywords in name
- Use both English and Arabic terms
- Keep names consistent

### **Template Organization**

1. **Create category-specific templates first**
   - Supply → Supply template
   - Maintenance → Maintenance template

2. **Create general template as fallback**
   - No category → General template

3. **Use Project Tasks From Templates for advanced needs**
   - Complex stage workflows
   - Subtask hierarchies
   - Advanced task management

---

## Version Compatibility

| Odoo Version | ICS Templates | Project Tasks From Templates |
|--------------|---------------|------------------------------|
| **18.0** | ✅ Full Support | ✅ Full Support |
| **17.0** | ✅ Full Support | ✅ Full Support |
| **16.0** | ✅ Full Support | ✅ Full Support |

---

## Related Documentation

- `PROJECT_AUTOMATION_SUMMARY.md` - ICS template system details
- `project_tasks_from_templates/README.rst` - Third-party module docs
- `TENDER_WORKFLOW_STRUCTURE.md` - Tender workflow phases

---

## Summary

The integration provides:

✅ **Dual template system** - ICS native + third-party  
✅ **Automatic selection** - Smart priority-based matching  
✅ **Category mapping** - Arabic/English support  
✅ **Graceful fallback** - Works with or without module  
✅ **Full compatibility** - No breaking changes  

**Result:** Seamless project creation from templates regardless of which system is used! 🚀
