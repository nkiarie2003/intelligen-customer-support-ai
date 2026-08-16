# IntelliGen assignment mapping

## AI/ML components demonstrated
1. **Natural Language Processing:** text normalisation, TF-IDF vectorisation, policy chunking and semantic retrieval.
2. **Classification:** supervised multiclass Logistic Regression over TF-IDF features.
3. **Sentiment analysis:** VADER/local lexicon baseline with optional transformer sentiment.
4. **Neural networks / deep learning:** optional Hugging Face zero-shot classifier and transformer sentiment/generator.
5. **Explainable AI:** token-level local feature contributions from the linear classifier plus transparent priority reasons.
6. **Prompt engineering:** a constrained response-generation prompt prohibits invented policy, guarantees, passwords and unsupported legal conclusions.
7. **Cloud AI/ML:** the real-data classifier can be trained and evaluated interactively on an existing Azure ML compute instance; the resulting artifact is served by local Flask inference. Optional online-endpoint files are retained only as a production architecture reference.
8. **Advanced component:** RAG retrieves relevant policy passages with Sentence Transformer embeddings before drafting a response.

## Business benefits
- Automatically triages large volumes of support messages.
- Routes complaints to appropriate teams using category and priority.
- Reduces manual reading while preserving human control over final responses.
- Surfaces recurrent complaint themes for service improvement.
- Provides auditable model outputs and evidence used by the RAG component.
- Can be exposed as a REST API for CRM or help-desk integration.

## Ethical issues
- Bias: training data may encode uneven language patterns across customer groups.
- Automation bias: agents may over-trust confident predictions or generated drafts.
- Misclassification: an urgent complaint could be incorrectly assigned low priority.
- Hallucination: a generative model could invent policy or outcomes; RAG and human approval reduce but do not remove this risk.
- Accessibility: sentiment models can misunderstand dialect, sarcasm, disability-related communication or non-native English.

## Legal issues
- UK GDPR/data protection: establish lawful basis, purpose limitation, data minimisation, retention periods, access controls and data-subject processes.
- Automated decisions: do not let the prototype make solely automated decisions that have significant effects on customers.
- Security: secrets must be stored in environment variables; avoid collecting passwords and full card details.
- Copyright/licensing: verify training datasets and model licences before commercial deployment.
- Consumer protection: generated messages must not invent contractual rights, refunds, compensation or service guarantees.

## Environmental issues
- Large transformer models consume more compute and energy than linear baselines.
- The application therefore keeps lightweight models as the default and loads transformer models only when explicitly enabled.
- Reuse pretrained models rather than retraining large language models from scratch where suitable.
- Measure latency and compute usage as part of model selection, not accuracy alone.
- Cloud deployments should be right-sized and shut down when not required for development demonstrations.

## IDE versus non-IDE demonstration
### VS Code advantages
- Integrated terminal, debugger, Git, Python interpreter selection and extensions.
- Easier navigation across Flask templates, services, tests and model scripts.
- Breakpoints make request/AI pipeline debugging easier.

### VS Code disadvantages
- Extensions can hide the exact commands being executed.
- Interpreter confusion can occur when several virtual environments exist.
- Resource-heavy extensions can affect low-spec machines.

### Command-line advantages
- Reproducible commands are easy to document and automate.
- Makes environment, dependency and process behaviour explicit.
- Skills transfer well to Linux servers, containers and CI/CD.

### Command-line disadvantages
- Less visual guidance for beginners.
- Debugging multi-module web applications can be slower without an interactive debugger.

## Code-generation tools
Generative coding assistants can accelerate boilerplate, tests, refactoring and documentation. However, generated code must be reviewed for insecure defaults, obsolete APIs, invented functions, licence concerns and hidden logical errors. IntelliGen should use code review, automated tests, dependency scanning and human accountability rather than accepting AI-generated code uncritically.


## Real-data methodology update
The current version replaces the bundled synthetic classifier data with locally downloaded CFPB complaint narratives and adds the Customer Support on Twitter corpus for non-authoritative conversational examples. Discuss the CFPB Product-to-category mapping as a modelling choice, the effect of class balancing, US/financial-services domain limitations, and the fact that public complaint data may still create privacy and representativeness concerns.


## SHU cloud-governance case study
The university lab environment applied an Allowed Resource Types policy that prevented creation of additional Azure ML online-endpoint/job child resources. The implementation therefore adapts to an existing compute instance rather than attempting to bypass organisational governance. This is useful interview material: enterprise AI engineering must work within security, cost and resource-governance controls. The limitation should be documented transparently rather than disguised as an application failure.

## Responsible data lifecycle implemented in the prototype
- Obvious card/PIN/OTP-style values are masked before complaint text is persisted or analysed.
- AI replies remain drafts until a human agent approves, edits or rejects them.
- Staff can re-analyse a case after a model update, making model lifecycle changes observable.
- Training provenance records platform, host, Python/scikit-learn versions, dataset size and Azure workspace/compute metadata.
- A retention CLI can delete old closed cases after an explicit confirmation flag.
