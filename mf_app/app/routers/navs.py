from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_session
from .. import schemas, crud
import csv, io
from datetime import datetime

router = APIRouter(prefix="/navs", tags=["navs"])

@router.post("/", response_model=schemas.NAVRead)
async def post_nav(nav: schemas.NAVCreate, session: AsyncSession = Depends(get_session)):
    # Optionally verify fund exists...
    row = await crud.insert_nav(session, nav)
    return row[0]

@router.post("/bulk-csv")
async def upload_nav_csv(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    # Expect CSV with headers: scheme_code,nav_time,nav_value,source
    text_data = await file.read()
    s = text_data.decode()
    reader = csv.DictReader(io.StringIO(s))
    rows = []
    for r in reader:
        # parse nav_time
        r_parsed = {
            "scheme_code": r["scheme_code"],
            "nav_time": datetime.fromisoformat(r["nav_time"]),
            "nav_value": float(r["nav_value"]),
            "source": r.get("source")
        }
        rows.append(r_parsed)
    await crud.bulk_insert_nav(session, rows)
    return {"inserted": len(rows)}

@router.get("/{scheme_code}")
async def get_navs(scheme_code: str, start: str | None = Query(None), end: str | None = Query(None),
                   session: AsyncSession = Depends(get_session)):
    q = "SELECT * FROM nav WHERE scheme_code = :code"
    params = {"code": scheme_code}
    if start:
        q += " AND nav_time >= :start"
        params["start"] = start
    if end:
        q += " AND nav_time <= :end"
        params["end"] = end
    q += " ORDER BY nav_time ASC"
    res = await session.execute(text(q), params)
    rows = res.fetchall()
    # convert to list of dicts
    return [dict(r._mapping) for r in rows]
