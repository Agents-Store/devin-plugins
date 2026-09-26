---
name: salary-management
description: This skill should be used when managing employee salary contacts, creating salary payment registries, uploading or distributing payslips, generating payslip PDFs, or working with Maspay salary batches. Relevant for queries like "add an employee to salary project", "create a salary registry for March", "send payslips to employees", or "list salary contacts". Use this skill whenever the user mentions salary, payroll, employees, payslips, or any HR-related banking operation.
---

# Salary Project Management via Bank MCP

Manage salary project operations: employee contacts, salary registries (batch payments), and payslip distribution.

## Why Monobank and PrivatBank Differ

Monobank and PrivatBank have fundamentally different corporate banking architectures, which affects salary operations:

- **Monobank** uses a modern REST API with contacts, registries, and payslips as separate entities. Amounts are in kopiykas (smallest currency unit). Pagination uses limit/offset.
- **PrivatBank** uses a legacy packet-based system called **Maspay** with salary groups, receivers, and packets. Amounts are decimal strings. Pagination is page-based.

This means you cannot use the same API calls for both banks. Always check which bank the user's salary project is connected to before proceeding. For PrivatBank Maspay specifics, refer to `references/privatbank-maspay.md`.

## Practical Example

**User says:** "створи зарплатну відомість за березень"

**Workflow:**

1. **Clarify details:** The user wants to create a salary registry for March 2026. Ask:
   - Which sender account (IBAN) to use?
   - Which employees to include? (All contacts, or a subset?)
   - What amounts per employee?
   If the user has a prepared list (spreadsheet, previous registry), ask for it.

2. **Get registry types** — call the types endpoint to discover available options (e.g., "Заробітна плата", "Аванс", "Премія"). The user said "зарплатна відомість", so select the salary type.

3. **Prepare recipient list** — for each employee:
   - Full name in format "Прізвище Ім'я По батькові"
   - IBAN from salary contacts
   - Amount in kopiykas (Monobank) or decimal (PrivatBank)

4. **Show summary before creating:**
   ```
   Зарплатна відомість за березень 2026:
     Тип: Заробітна плата
     Рахунок: UA29322001...
     Період: 01.03.2026 – 31.03.2026
     Працівників: 15
     Загальна сума: ₴450 000,00

     Перші 5 записів:
     | # | ПІБ                      | Сума        |
     |---|---------------------------|-------------|
     | 1 | Петренко Петро Петрович   | ₴35 000,00  |
     | 2 | Іваненко Іван Іванович    | ₴32 000,00  |
     | 3 | Сидоренко Олена Василівна | ₴28 500,00  |
     ...

   Підтверджуєте створення? (так/ні)
   ```

5. **Create the registry** after confirmation. Return the registry ID.

6. **Poll status** until processing completes. Report results.

**Output:**
```
Відомість створено:
  ID: reg_xyz789
  Статус: Processing
  Очікуйте завершення обробки...
```

## Tool Discovery

Search for salary-related MCP tools using keywords: `salary`, `contact`, `registry`, `payslip`, `зарплат`, `контакт`, `відомість`, `розрахунковий`.

Three sub-domains:
1. **Salary Contacts** — employee registry (CRUD, search)
2. **Salary Registries** — payment batches (create, check status)
3. **Payslips** — pay stubs (upload, send, PDF generation)

## Salary Contacts

### Contact Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| firstName | Yes | First name | Петро |
| lastName | Yes | Last name | Петренко |
| middleName | No | Patronymic | Петрович |
| iban | Yes | Employee bank IBAN | UA29322001... |
| inn | Yes | ІПН (tax ID, РНОКПП) | 10 digits |
| pan | No | Card number | 16 digits |
| documentType | No | ID document type | OLD_PASSPORT, ID_CARD, FOREIGN_PASSPORT |
| documentSeries | No | Document series | 2 chars (e.g., АБ) |
| documentNumber | No | Document number | Up to 9 digits |

### Contact Operations

- **List contacts** — paginated list. Params: `limit` (1-500, default 100), `offset` (default 0).
- **Search contacts** — by name, INN, or IBAN. Params: `query` (min 3 chars), `limit`, `offset`.
- **Get contact by ID** — full details. Param: `id` (UUID).
- **Create contact** — add employee to salary project. Param: `body` with contact fields.
- **Delete contact** — remove one. Param: `id` (UUID).
- **Batch delete** — remove multiple. Param: `ids` (array of UUIDs).

## Salary Registries

A registry is a batch payment instruction for distributing salary to multiple employees at once.

### Registry Fields

| Field | Required | Description | Format |
|-------|----------|-------------|--------|
| registryName | Yes | Descriptive name | "Заробітна плата за березень 2026" |
| senderIban | Yes | Company source IBAN | UA + 27 digits |
| salaryRegistryType | Yes | Type code | Get from types endpoint |
| from | Yes | Period start | YYYY-MM-DD |
| to | Yes | Period end | YYYY-MM-DD |
| recipients | Yes | Payment recipients | See below |

### Recipient Fields

| Field | Required | Description |
|-------|----------|-------------|
| fullName | Yes | "Прізвище Ім'я По батькові" |
| iban | Yes | Recipient IBAN |
| amount | Yes | Amount in **kopiykas** (Monobank) |
| inn | No | ІПН (tax ID) |
| documentType | No | OLD_PASSPORT / ID_CARD / FOREIGN_PASSPORT |

### Registry Workflow

```
1. Get available registry types (call types endpoint)
2. Prepare recipient list with amounts (kopiykas for Monobank)
3. Create registry with name, IBAN, type, period, recipients
4. Receive registry ID
5. Poll status until processing completes
6. Report results to user
```

### Registry Status

Track by ID after creation. Typical states: Created / Processing / Completed / Partially completed / Failed.

## Payslips (Розрахункові листки)

Payslips are detailed salary breakdowns sent to employees via their mobile banking app. They help employees understand their pay composition — base salary, bonuses, deductions, net pay.

### Payslip Structure

Each payslip is tied to a **period** (YYYY-MM) and an **employee** (ІПН).

Payslip attributes are key-value pairs:

| Field | Description | Example |
|-------|-------------|---------|
| attributeName | Component name | "Базова зарплата" |
| value | Component value | "50000" |
| attributeSuffix | Unit/suffix | "грн" |
| sortOrder | Display order | 1, 2, 3... |

Example:
```
1. Базова зарплата — 50000 грн
2. Премія — 5000 грн
3. Відпускні — 0 грн
4. ПДФО (18%) — -9900 грн
5. Військовий збір (5%) — -2750 грн
6. ЄСВ — -12100 грн
7. До виплати — 30250 грн
```

### Payslip Operations

- **Batch upload** — upload payslips for a period. Max 1000 employees per batch. Params: `period` (YYYY-MM), `employees` array.
- **Get import status** — check upload progress. Param: `period`.
- **Send to mobile** — distribute to employees' banking apps. Param: `period`.
- **Generate PDF** — create PDF for one employee. Params: `identification` (ІПН), `period`.
- **Delete payslips** — remove specific employees'. Params: `period`, `identifications` (array of ІПН).
- **Delete entire import** — remove all payslips for a period. Param: `period`.

### Payslip Distribution Workflow

```
1. Prepare payslip data (attributes per employee)
2. Upload batch: batchUploadPayslips(period, employees)
3. Check status: getImportStatus(period)
4. When ready, send: sendToMobile(period)
5. Optionally generate individual PDFs for records
```

## PrivatBank Salary Project (Maspay)

PrivatBank uses a packet-based model called Maspay. Key differences from Monobank:

| Aspect | Monobank | PrivatBank (Maspay) |
|--------|----------|---------------------|
| Structure | Contacts + Registries | Groups + Receivers + Packets |
| Amounts | Kopiykas (integer) | Decimal strings |
| Pagination | limit/offset | Page-based |
| Workflow | Create registry directly | Create packet, validate, then process |

For the complete Maspay workflow (groups, receivers, packets, validation), read `references/privatbank-maspay.md`.

## Safety Rules

1. **Mask ІПН in output** — show only last 4 digits (`******1234`). Tax IDs are sensitive personal data.
2. **Mask IBAN and card numbers** — show only last 4 digits. Protects account information.
3. **Confirm before batch operations** — especially delete and registry creation. These affect real money.
4. **Double-check recipient list** before creating registries. Show total count and total amount for verification.
5. **Verify amount format** — kopiykas (Monobank) vs. decimal strings (PrivatBank). A mixup means employees get 100x too much or too little. See the payments skill for detailed conversion rules.
