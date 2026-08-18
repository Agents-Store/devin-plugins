# PrivatBank Salary Project (Maspay)

PrivatBank uses a different salary model called **Maspay** (масові платежі — mass payments). The workflow is packet-based.

## Key Differences from Monobank

| Feature | Monobank | PrivatBank |
|---------|----------|------------|
| Model | Contacts + Registries | Groups + Receivers + Packets |
| Contact management | CRUD by UUID | Add/update by card number (PAN) |
| Payment batch | Registry with recipients[] | Maspay Packet with receivers |
| Amount format | Kopiykas (integer) | Decimal (e.g., 1000.50) |
| Groups | Registry types | SALARY, STUDENT |
| Validation | Automatic | Manual validation step |
| Pagination | offset/limit | page/page-size (max 100) |

## Salary Groups

Search for tools with keywords: `salary`, `group`.

Get available salary groups — typically `SALARY` and `STUDENT`.

## Salary Receivers

Search for tools with keywords: `salary`, `receiver`.

**List receivers** — paginated list within a group
- Parameters: `group` (e.g., "SALARY"), `page`, `page-size` (max 100), `filter`

**Add/update receiver** — by card number
- Parameters: `pan` (card number), `group`, `tabn` (employee ID), `fio` (name as array of strings), `inn` (IPN)

## Maspay Packets (Salary Batches)

Search for tools with keywords: `maspay`, `packet`, `payroll`.

**Workflow:**
```
1. getSalaryGroups() → list available groups
2. getSalaryReceivers(group) → list employees
3. createMaspayPacket({group, salary: true, packetName}) → get packet ref
4. addReceiverToMaspay(ref, {receiver, amount, comment}) → add each employee
5. validateMaspayPacket(ref) → submit for validation
6. listPayrollPackets() → monitor status
```

**Create packet:**
- `group`: "SALARY" or "STUDENT"
- `salary`: true = targeted, false = non-targeted
- `packetName`: descriptive name

**Add receiver to packet:**
- `receiver`: receiver ID from getSalaryReceivers
- `amount`: decimal number (e.g., 15000.50) — NOT kopiykas!
- `comment`: payment purpose/comment

**Remove receiver from packet:**
- `ref` (packet ref) + body.`ref` (record ref to remove)

**Validate packet:**
- Sends packet for bank validation — required before processing

**List payroll packets:**
- Optional filters: `status` (V=validated, A=accepted, F=failed, R=rejected), `from`/`to` dates
- Pagination: `page`, `page-size`

## Paysheets (PrivatBank-specific)

Search for tools with keywords: `paysheet`, `journal`.

**Get paysheet journal** — list of payslip projects
**Save paysheet files** — save uploaded paysheet files to SFTP
