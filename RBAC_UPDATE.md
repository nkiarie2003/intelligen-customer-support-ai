# Role-Based Interface Update

## Customer
Customer navigation and pages are deliberately non-technical.

Available:
- My complaints
- Submit complaint
- Case reference and submitted complaint
- Simple progress tracker
- Case status
- Human-approved response only

Not available:
- AI draft before human approval
- Complaint category/model confidence
- Sentiment output
- AI-derived priority score
- XAI explanations
- RAG evidence
- AI backend diagnostics
- Analytics/model metrics/system status
- User/knowledge/audit administration

## Support agent
Available:
- Case queue
- Customer complaint details
- Internal response draft needed for review
- Edit/approve/reject response
- Close case

Not available:
- Per-case technical AI diagnostics
- Complaint intelligence page
- Analytics/model metrics/system status
- Model re-analysis
- Administrative tools

## Administrator
Available:
- Admin dashboard
- Complaint Intelligence (per-case protected analysis)
- Complaint analytics
- Model metrics
- System/model status
- Model re-analysis
- Users
- RAG knowledge base
- Audit log

The application enforces these boundaries server-side with `staff_required` and `admin_required`, not only through navigation visibility.
