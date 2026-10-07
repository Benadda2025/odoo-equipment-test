import random
from datetime import datetime, timedelta
from psycopg2.extras import execute_values

N_EMP, N_EQ, BATCH = 2000, 50000, 5000

cats = env['equipment.category'].search([])
if not cats:
    cats = env['equipment.category'].create(
        [{'name': n} for n in ('Laptop', 'Phone', 'Monitor', 'Tool', 'Accessory')])

env['hr.employee'].create([{'name': f'Load Emp {i}'} for i in range(N_EMP)])
env.cr.commit()

for start in range(0, N_EQ, BATCH):
    env['equipment.equipment'].create([{
        'name': f'Device {i}', 'code': f'LD-{i:07d}',
        'serial_number': f'SN-{i:09d}',
        'category_id': random.choice(cats.ids),
    } for i in range(start, start + BATCH)])
    env.cr.commit()
    env.invalidate_all()

cr = env.cr
cr.execute("SELECT array_agg(id) FROM hr_employee WHERE name LIKE 'Load Emp%'")
emps = cr.fetchone()[0]
cr.execute("SELECT id FROM equipment_equipment WHERE code LIKE 'LD-%'")
eq_ids = [r[0] for r in cr.fetchall()]

now = datetime.now()
rows, opens = [], []

def flush():
    global rows, opens
    if rows:
        execute_values(cr, """INSERT INTO equipment_assignment
            (equipment_id, employee_id, date_from, date_to, is_active,
             create_uid, write_uid, create_date, write_date) VALUES %s""",
            [r + (1, 1, now, now) for r in rows])
    if opens:
        execute_values(cr, """UPDATE equipment_equipment e
            SET state='in_use', current_employee_id=v.emp
            FROM (VALUES %s) AS v(id, emp) WHERE e.id=v.id""", opens)
    rows, opens = [], []
    cr.connection.commit()

for n, eq in enumerate(eq_ids, 1):
    cursor = now - timedelta(days=random.randint(400, 1500))
    for _ in range(random.randint(0, 12)):           # returned history
        s = cursor + timedelta(days=random.randint(1, 20))
        e = s + timedelta(days=random.randint(5, 120))
        if e > now:
            break
        rows.append((eq, random.choice(emps), s, e, False))
        cursor = e
    s = cursor + timedelta(days=1)
    if random.random() < 0.6 and s < now:            # currently in use
        emp = random.choice(emps)
        rows.append((eq, emp, s, None, True))
        opens.append((eq, emp))
    if n % 5000 == 0:
        flush()
flush()
cr.execute("ANALYZE equipment_assignment; ANALYZE equipment_equipment;")
cr.connection.commit()