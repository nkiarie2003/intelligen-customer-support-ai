# Customer-safe UI and administrator-only AI analysis

This revision applies least-privilege presentation rules to the SHU cloud-training/local-inference application.

## Customer view
Customers can see only information needed to use the support service:

- case reference;
- complaint subject and message they submitted;
- submission date/time;
- simple case progress (received, support review, response, closed);
- case status;
- a human-approved response, once available.

Customers do **not** receive the internal AI draft or any model/analysis fields.

## Support-agent view
Support agents can see the complaint, workflow state and the internal draft needed to prepare a customer response. They can edit/approve/reject a draft and close a case.

Agents cannot access model confidence, sentiment scores, priority model scores, XAI cues, RAG evidence, backend diagnostics, model metrics, system status, analytics or model re-analysis.

## Administrator view
Administrators have a separate protected Complaint Intelligence route for:

- predicted category and confidence;
- sentiment and score;
- AI-derived priority and rationale;
- Explainable AI feature contributions;
- privacy-minimisation notices;
- RAG retrieval evidence;
- internal AI draft and approved comparison;
- backend diagnostics.

Administrators also retain access to Analytics, Model Metrics, System Status, Users, Knowledge Base and Audit Log.

## Security principle
Technical information is not merely hidden with CSS. Administrator-only routes use the server-side `admin_required` decorator, and model re-analysis is also restricted to administrators. Direct URL attempts by customers or agents return HTTP 403.
