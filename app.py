from datetime import date
from flask import Flask, request, redirect, url_for, render_template, abort, send_file
from flask_login import login_required, current_user

from auth import init_auth, DEMO_USER
from services.data import AREAS, CAMPS
from services.availability import (
    parse_date,
    filter_camps,
    build_card_result,
    build_csv_bytes,
    seed_availability
)
seed_availability(CAMPS)

app = Flask(__name__)
app.secret_key = "dev-secret"  # demo 用；正式環境請改成安全值
init_auth(app)


@app.route("/")
def home():
    return redirect(url_for("reserve"))


@app.route("/reserve")
@login_required
def reserve():
    counties = list(AREAS.keys())
    county = request.args.get("county") or counties[0]
    district = request.args.get("district") or ""
    checkin = request.args.get("checkin") or date.today().isoformat()
    nights = int(request.args.get("nights") or 1)
    tents = int(request.args.get("tents") or 1)

    districts = AREAS.get(county, [])
    results = None

    # 視為「有查詢」的條件：帶任一 query 參數
    if request.args:
        d_checkin = parse_date(checkin)
        camps = filter_camps(CAMPS, county, district)
        results = []
        for camp in camps:
            card = build_card_result(camp, d_checkin, nights, tents)
            if card:
                results.append(card)

        # 讓結果更穩定：可依起價、剩餘、海拔排序（你可自行調整）
        results.sort(key=lambda r: (r["price_from_per_night"], -r["units_left_total"], -r["altitude_m"]))

    q = {"county": county, "district": district, "checkin": checkin, "nights": nights, "tents": tents}

    return render_template(
        "reserve.html",
        user=current_user.id,
        counties=counties,
        districts=districts,
        q=q,
        results=results,
    )


@app.route("/download")
@login_required
def download():
    county = request.args.get("county")
    district = request.args.get("district") or ""
    checkin = request.args.get("checkin")
    nights = request.args.get("nights")
    tents = request.args.get("tents")

    if not county or not checkin or not nights or not tents:
        abort(400)

    d_checkin = parse_date(checkin)
    nights_i = int(nights)
    tents_i = int(tents)

    csv_bytes, filename = build_csv_bytes(CAMPS, county, district, d_checkin, nights_i, tents_i)
    return send_file(csv_bytes, as_attachment=True, download_name=filename, mimetype="text/csv")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)