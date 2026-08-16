from .text import safe_excerpt


class ResponseGenerator:
    def __init__(self, transformer_hub, enabled: bool):
        self.transformer_hub = transformer_hub
        self.enabled = enabled

    def build_prompt(
        self,
        subject: str,
        message: str,
        analysis: dict,
        retrieval: dict,
        conversation_examples: dict | None = None,
    ) -> str:
        evidence = "\n".join(
            f"- {item['source']}: {item['text']}" for item in retrieval.get("results", [])
        ) or "- No relevant policy evidence was retrieved."
        examples = conversation_examples or {"results": []}
        example_text = "\n".join(
            f"- Customer example: {item['customer_message']}\n  Agent example: {item['agent_response']}"
            for item in examples.get("results", [])
        ) or "- No conversation examples were retrieved."

        return f"""You are a customer-support drafting assistant for a financial-services demonstration system.
Create a concise, professional draft response for a human agent to review.
Rules:
1. Do not invent refunds, compensation, transaction outcomes, legal conclusions or policy terms.
2. Use only the RETRIEVED POLICY EVIDENCE for policy-specific statements.
3. The historical conversation examples are for tone and structure only. They are NOT policy authority.
4. Acknowledge the customer's concern without admitting liability.
5. If policy evidence is insufficient, say a human agent will verify the matter.
6. Never ask for passwords, PINs, one-time passcodes or full card/account numbers.
7. End with a clear next step.

Subject: {subject}
Customer message: {message}
Predicted category: {analysis['category']['label']}
Sentiment: {analysis['sentiment']['label']}
Priority: {analysis['priority']['label']}

RETRIEVED POLICY EVIDENCE:
{evidence}

HISTORICAL SUPPORT EXAMPLES (STYLE ONLY):
{example_text}

Draft response:"""

    def generate(
        self,
        subject: str,
        message: str,
        analysis: dict,
        retrieval: dict,
        conversation_examples: dict | None = None,
    ) -> dict:
        prompt = self.build_prompt(subject, message, analysis, retrieval, conversation_examples)
        if self.enabled:
            try:
                text = self.transformer_hub.generate(prompt)
                return {
                    "text": text,
                    "backend": "local_transformer_generator",
                    "prompt_preview": safe_excerpt(prompt, 700),
                }
            except Exception as exc:
                fallback = self._template(message, analysis, retrieval)
                return {
                    "text": fallback,
                    "backend": "controlled_template_fallback",
                    "warning": str(exc),
                    "prompt_preview": safe_excerpt(prompt, 700),
                }
        return {
            "text": self._template(message, analysis, retrieval),
            "backend": "controlled_template",
            "prompt_preview": safe_excerpt(prompt, 700),
        }

    @staticmethod
    def _template(message: str, analysis: dict, retrieval: dict) -> str:
        category = analysis["category"]["label"].replace("_", " ")
        policy = retrieval.get("results", [])
        policy_sentence = (
            f"I have checked the relevant guidance in {policy[0]['source']}. "
            if policy else
            "A support agent will verify the applicable policy before confirming an outcome. "
        )
        return (
            "Thank you for contacting us. I’m sorry to hear about the difficulty you described. "
            f"Your message has been logged as a {category} case and will be reviewed by our support team. "
            + policy_sentence
            + "Please do not send passwords, PINs, one-time passcodes or full payment-card/account details. "
              "A human agent will review this draft and confirm the appropriate next step."
        )
