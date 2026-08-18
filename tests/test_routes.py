def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Customer Support" in response.data
    assert b"model confidence" not in response.data.lower()
    assert b"explainable ai" not in response.data.lower()


def test_register_and_dashboard(client):
    response = client.post(
        "/auth/register",
        data={"username": "demo_user", "password": "StrongPass123!", "confirm": "StrongPass123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"My complaints" in response.data
    assert b"Model metrics" not in response.data
    assert b"System status" not in response.data


def _login(client, username, password):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def _create_case(app, username="case_customer"):
    from app.extensions import db
    from app.models import Complaint, User

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role="customer")
            user.set_password("StrongPass123!")
            db.session.add(user)
            db.session.flush()
        complaint = Complaint(
            user_id=user.id,
            subject="Unauthorised card transaction",
            message="There is an unauthorised credit card transaction on my account and I need urgent help.",
            ai_category="credit_card",
            ai_category_confidence=0.94,
            ai_sentiment="negative",
            ai_sentiment_score=-0.83,
            ai_priority="critical",
            ai_priority_score=92,
            ai_explanation={
                "top_positive_cues": [{"token": "unauthorised", "contribution": 1.9}],
                "priority_reasons": ["Possible fraud or unauthorised transaction"],
                "privacy_minimisation": [],
            },
            ai_retrieval={"results": [{"source": "Card policy", "score": 0.88, "text": "Internal policy evidence."}]},
            ai_reply="Internal AI draft that must never be shown to the customer before approval.",
            ai_backends={"classifier": "tfidf_logistic_regression"},
        )
        db.session.add(complaint)
        db.session.commit()
        return complaint.public_id


def test_customer_only_sees_customer_safe_case_information(app, client):
    public_id = _create_case(app)
    _login(client, "case_customer", "StrongPass123!")

    response = client.get(f"/complaints/{public_id}")
    assert response.status_code == 200
    assert b"Your complaint" in response.data
    assert b"Case progress" in response.data
    assert b"being reviewed" in response.data
    assert b"Internal AI draft" not in response.data
    assert b"Classification" not in response.data
    assert b"model confidence" not in response.data
    assert b"Sentiment" not in response.data
    assert b"Explainable AI" not in response.data
    assert b"RAG" not in response.data
    assert b"AI backends" not in response.data

    assert client.get(f"/admin-tools/complaints/{public_id}/analysis").status_code == 403


def test_customer_sees_only_human_approved_response(app, client):
    from app.extensions import db
    from app.models import Complaint

    public_id = _create_case(app, "approved_customer")
    with app.app_context():
        complaint = Complaint.query.filter_by(public_id=public_id).first()
        complaint.reply_status = "approved"
        complaint.status = "reviewed"
        complaint.human_reply = "This is the human-approved support response."
        db.session.commit()

    _login(client, "approved_customer", "StrongPass123!")
    response = client.get(f"/complaints/{public_id}")
    assert b"This is the human-approved support response." in response.data
    assert b"Internal AI draft" not in response.data


def test_agent_gets_operational_workspace_but_not_ai_diagnostics(app, client):
    from app.extensions import db
    from app.models import User

    public_id = _create_case(app)
    with app.app_context():
        agent = User(username="support_agent", role="agent")
        agent.set_password("StrongPass123!")
        db.session.add(agent)
        db.session.commit()

    _login(client, "support_agent", "StrongPass123!")
    dashboard = client.get("/dashboard")
    assert b"Case queue" in dashboard.data
    assert b"Analytics" not in dashboard.data
    assert b"Model metrics" not in dashboard.data
    assert b"System status" not in dashboard.data

    detail = client.get(f"/complaints/{public_id}")
    assert detail.status_code == 200
    assert b"Staff response workspace" in detail.data
    assert b"Internal AI draft that must never be shown" in detail.data
    assert b"model confidence" not in detail.data
    assert b"Explainable AI" not in detail.data
    assert b"RAG" not in detail.data
    assert b"AI backends" not in detail.data
    assert b"Open complaint intelligence" not in detail.data

    assert client.get("/analytics").status_code == 403
    assert client.get("/model-metrics").status_code == 403
    assert client.get("/system/status").status_code == 403
    assert client.get(f"/admin-tools/complaints/{public_id}/analysis").status_code == 403
    assert client.post(f"/complaints/{public_id}/reanalyze").status_code == 403


def test_admin_can_access_restricted_intelligence(app, client):
    from app.extensions import db
    from app.models import User

    public_id = _create_case(app)
    with app.app_context():
        admin = User(username="admin_user", role="admin")
        admin.set_password("StrongPass123!")
        db.session.add(admin)
        db.session.commit()

    _login(client, "admin_user", "StrongPass123!")
    dashboard = client.get("/dashboard")
    assert b"Analytics" in dashboard.data
    assert b"Model metrics" in dashboard.data
    assert b"System status" in dashboard.data
    assert b"Users" in dashboard.data
    assert b"Knowledge" in dashboard.data
    assert b"Audit" in dashboard.data

    analysis = client.get(f"/admin-tools/complaints/{public_id}/analysis")
    assert analysis.status_code == 200
    assert b"Complaint intelligence" in analysis.data
    assert b"Classification" in analysis.data
    assert b"model confidence" in analysis.data
    assert b"Explainable AI" in analysis.data
    assert b"Retrieved policy evidence" in analysis.data
    assert b"AI backends" in analysis.data

    assert client.get("/analytics").status_code == 200
    assert client.get("/model-metrics").status_code == 200
    assert client.get("/system/status").status_code == 200
    assert client.get("/admin-tools/users").status_code == 200
    assert client.get("/admin-tools/knowledge").status_code == 200
    assert client.get("/admin-tools/audit").status_code == 200
    assert client.post(f"/complaints/{public_id}/reanalyze").status_code in {302, 303}
