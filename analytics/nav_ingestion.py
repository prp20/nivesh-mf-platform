from sqlalchemy.orm import Session
from analytics.nav_providers.mfapi import fetch_nav_history
from backend.models.nav_data import NavData
from backend.models.mutual_fund import MutualFund


def ingest_nav_for_fund(fund, db):
    print(f"\n--- FUND: {fund.fund_name} | scheme={fund.scheme_code}")

    navs = fetch_nav_history(fund.scheme_code)
    print(f"Fetched {len(navs)} NAV records from MFAPI")

    inserted = 0

    for item in navs:
        exists = (
            db.query(NavData)
            .filter_by(fund_id=fund.id, nav_date=item["date"])
            .first()
        )
        if not exists:
            db.add(
                NavData(
                    fund_id=fund.id,
                    nav_date=item["date"],
                    nav_value=item["nav"],
                )
            )
            inserted += 1

    db.commit()
    print(f"Inserted {inserted} rows")
    return inserted


def ingest_nav_for_all_funds(db: Session) -> dict:
    funds = db.query(MutualFund).all()
    results = {}

    for fund in funds:
        try:
            count = ingest_nav_for_fund(fund, db)
            results[fund.fund_name] = count
        except Exception as e:
            results[fund.fund_name] = str(e)

    return results
