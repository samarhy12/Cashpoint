from datetime import datetime, date

from flask import Blueprint, render_template, request, abort, current_app
from flask_login import login_required

from models import Staff, Repayment
from pagination_utils import paginate_items

bp = Blueprint("agents", __name__, url_prefix="/agents")


@bp.route("/")
@login_required
def list_agents():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["DEFAULT_PAGE_SIZE"]
    agents_all = Staff.query.filter_by(role="agent").order_by(Staff.full_name.asc()).all()
    pagination = paginate_items(agents_all, page, per_page)

    today = date.today()
    agent_today_totals = {}
    for agent in pagination.items:
        total = sum(
            r.amount for r in Repayment.query.filter_by(agent_id=agent.id, date=today).all()
        )
        agent_today_totals[agent.id] = round(total, 2)

    return render_template(
        "agents/list.html",
        agents=pagination.items,
        agent_today_totals=agent_today_totals,
        today=today,
        pagination=pagination,
        query_params={},
    )


@bp.route("/<int:agent_id>")
@login_required
def agent_detail(agent_id):
    agent = Staff.query.filter_by(id=agent_id, role="agent").first_or_404()

    view = request.args.get("view", "day")  # "day" or "all"
    date_str = request.args.get("date", "")

    if view == "all":
        repayments = Repayment.query.filter_by(agent_id=agent.id).order_by(Repayment.date.desc()).all()
        selected_date = None
    else:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        except ValueError:
            selected_date = date.today()
        repayments = (
            Repayment.query.filter_by(agent_id=agent.id, date=selected_date)
            .order_by(Repayment.created_at.asc()).all()
        )

    total = round(sum(r.amount for r in repayments), 2)

    return render_template(
        "agents/detail.html",
        agent=agent,
        repayments=repayments,
        total=total,
        view=view,
        selected_date=selected_date,
        today=date.today(),
    )
