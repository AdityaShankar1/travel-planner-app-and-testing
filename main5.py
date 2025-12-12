from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Travel Planner CRUD API")

# --- Database setup ---
conn = sqlite3.connect("travel.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    destination TEXT NOT NULL,
    notes TEXT
)
""")
conn.commit()

# --- Pydantic models ---
class Plan(BaseModel):
    name: str
    type: str   # "solo" or "group"
    destination: str
    notes: str | None = None

class PlanUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    destination: str | None = None
    notes: str | None = None

# --- CRUD Endpoints ---
@app.post("/plans")
def create_plan(plan: Plan):
    cursor.execute(
        "INSERT INTO plans (name, type, destination, notes) VALUES (?, ?, ?, ?)",
        (plan.name, plan.type, plan.destination, plan.notes)
    )
    conn.commit()
    return {"message": f"Plan '{plan.name}' created"}

@app.get("/plans")
def read_plans(type: str | None = None):
    if type in ("solo", "group"):
        cursor.execute("SELECT * FROM plans WHERE type=?", (type,))
    else:
        cursor.execute("SELECT * FROM plans")
    return cursor.fetchall()

@app.get("/plans/{plan_id}")
def get_plan(plan_id: int):
    cursor.execute("SELECT * FROM plans WHERE id=?", (plan_id,))
    plan = cursor.fetchone()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.put("/plans/{plan_id}")
def update_plan(plan_id: int, updates: PlanUpdate):
    cursor.execute("SELECT * FROM plans WHERE id=?", (plan_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Plan not found")

    if updates.name:
        cursor.execute("UPDATE plans SET name=? WHERE id=?", (updates.name, plan_id))
    if updates.type:
        cursor.execute("UPDATE plans SET type=? WHERE id=?", (updates.type, plan_id))
    if updates.destination:
        cursor.execute("UPDATE plans SET destination=? WHERE id=?", (updates.destination, plan_id))
    if updates.notes is not None:
        cursor.execute("UPDATE plans SET notes=? WHERE id=?", (updates.notes, plan_id))

    conn.commit()
    return {"message": f"Plan {plan_id} updated"}

@app.delete("/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: int):
    cursor.execute("SELECT * FROM plans WHERE id=?", (plan_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Plan not found")

    cursor.execute("DELETE FROM plans WHERE id=?", (plan_id,))
    conn.commit()
    return None
