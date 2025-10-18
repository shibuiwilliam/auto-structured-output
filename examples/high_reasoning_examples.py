"""Examples demonstrating high reasoning mode for inferring structure from unclear prompts

High reasoning mode uses gpt-5 with enhanced reasoning capabilities to infer
optimal structured output formats when the expected structure is not clearly defined.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from auto_structured_output.extractor import StructureExtractor

# Load environment variables
load_dotenv(".envrc")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
extractor = StructureExtractor(client)


def run(prompts: list[str], file_name: str) -> None:
    T_Model = extractor.extract_structure(prompts, use_high_reasoning=True)

    print(f"Generated model: {T_Model.__name__}")
    print(f"Fields: {T_Model.model_json_schema()}")

    # Use the model with the first prompt for demonstration
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompts[0]}],
        response_format=T_Model,
    )

    data = response.choices[0].message.parsed
    if data is None:
        raise ValueError("Parsed data is None")
    data_dict = data.model_dump()
    print("\nGenerated data:")
    print(data_dict)

    extractor.save_extracted_json(T_Model, file_name)


def example_1_customer_feedback_analysis() -> None:
    """Example 1: Analyze customer feedback and extract insights

    This prompt doesn't specify exact fields, so high reasoning mode
    will infer an appropriate structure based on domain knowledge.
    """
    print("\n=== Example 1: Customer Feedback Analysis ===")

    prompt = """
Analyze customer feedback from our e-commerce platform and extract comprehensive,
actionable insights to improve our business operations. We need to understand multiple
dimensions of customer experience including:

1. Product Quality Assessment: Extract detailed feedback about product condition,
   functionality, durability, and whether it met customer expectations. Identify
   specific products mentioned and any quality issues reported.

2. Delivery Experience: Capture information about shipping speed, packaging quality,
   delivery accuracy, and any issues with the logistics process. Note whether delivery
   met promised timelines.

3. Customer Satisfaction Metrics: Determine overall satisfaction levels, likelihood
   to recommend (NPS-style), likelihood to repurchase, and emotional sentiment
   expressed in the feedback.

4. Service Quality: Evaluate interactions with customer service, responsiveness,
   problem resolution effectiveness, and staff professionalism.

5. Competitive Insights: Identify any mentions of competitors, price comparisons,
   or alternative products customers considered.

6. Actionable Recommendations: Based on the feedback, suggest specific improvements
   and prioritize areas needing immediate attention.

The extracted structure should support trend analysis over time and enable filtering
by product category, customer segment, and severity of issues raised.
    """

    run([prompt], "examples/schemas/high_reasoning_examples/customer_feedback_analysis.json")


def example_2_meeting_summary() -> None:
    """Example 2: Extract structured meeting summary

    The prompt describes a meeting scenario but doesn't specify exact fields.
    High reasoning mode will infer appropriate structure for meeting summaries.
    """
    print("\n=== Example 2: Meeting Summary ===")

    prompt = """
Extract a comprehensive, well-structured summary from team meeting discussions that
will serve as an official record and action tracking document. The summary should
capture all critical information including:

1. Meeting Metadata: Date, time, duration, location (physical/virtual), meeting type
   (standup, planning, retrospective, etc.), attendees with their roles, and any
   participants who were absent or joined late.

2. Agenda and Topics: List all agenda items discussed, with the time allocated and
   actual time spent on each topic. Note any topics that were deferred or added
   during the meeting.

3. Key Decisions Made: Document all decisions reached during the meeting, including
   who made the decision, the rationale behind it, any alternatives considered, and
   the expected impact. Include confidence level in each decision.

4. Action Items: Capture specific tasks assigned, with clear ownership (assignee),
   due dates, dependencies on other tasks or decisions, priority level, and success
   criteria for completion.

5. Discussion Points: Summarize important discussions, debates, concerns raised,
   risks identified, and any consensus or disagreements among participants.

6. Next Steps: Define follow-up meetings needed, items to be addressed before next
   meeting, and any preparatory work required from team members.

7. Blockers and Issues: Identify any obstacles, resource constraints, or escalations
   that need leadership attention.

The structure should enable easy search, filtering by participant or topic, tracking
of action item completion, and integration with project management tools.
    """

    run([prompt], "examples/schemas/high_reasoning_examples/meeting_summary.json")


def example_3_research_paper_metadata() -> None:
    """Example 3: Extract research paper metadata

    Infer what metadata would be useful for academic research papers
    without explicitly listing all fields.
    """
    print("\n=== Example 3: Research Paper Metadata ===")

    prompt = """
Extract comprehensive, richly-structured metadata from academic research papers to
build a sophisticated research database and citation management system. The metadata
should support advanced search, bibliometric analysis, and research discovery.

Essential metadata to capture includes:

1. Publication Information: Full paper title, subtitle if present, publication date,
   journal or conference name, volume, issue, page numbers, DOI, ISBN/ISSN, publisher,
   and publication status (preprint, published, in review).

2. Author Details: Complete author list with full names, affiliations (institution,
   department, country), ORCID identifiers, corresponding author designation, author
   contribution statements, and contact information.

3. Research Classification: Primary and secondary research fields, keywords (author-
   provided and indexed), subject categories, research methodology type (experimental,
   theoretical, computational, etc.), and relevant classification codes (ACM, MSC, etc.).

4. Abstract and Content: Structured abstract with background, methods, results, and
   conclusions sections. Extract key findings, novel contributions, and research gaps
   addressed.

5. Citations and References: Count of references cited, citation types (theory,
   methodology, comparison), key papers cited, and datasets or tools referenced.

6. Research Artifacts: Links to supplementary materials, source code repositories,
   datasets, experimental protocols, and reproducibility information.

7. Funding and Ethics: Funding sources, grant numbers, conflict of interest statements,
   ethics approval numbers, and data availability statements.

8. Impact Metrics: Citation count, h-index relevance, alternative metrics (Altmetric),
   download statistics, and social media mentions.

9. Version Control: Version history, preprint versions, amendments, errata, and
   retraction status if applicable.

The structure should enable bibliometric analysis, research trend identification,
collaboration network mapping, and integration with reference management software.
    """

    run([prompt], "examples/schemas/high_reasoning_examples/research_paper_metadata.json")


def example_4_job_application_evaluation() -> None:
    """Example 4: Evaluate job applications

    Demonstrates multi-prompt unified schema generation for different candidate levels.
    The system infers a comprehensive structure that works for both junior and senior
    software engineering candidates.
    """
    print("\n=== Example 4: Job Application Evaluation ===")

    prompts = [
        """
We're building a hiring system for junior software engineering positions. We need to evaluate
entry-level candidates who may have limited professional experience but show strong potential.
The system should capture their educational background, internships, bootcamp experience,
personal projects, coding skills, problem-solving ability, learning agility, and cultural fit.
We need to assess their foundational technical knowledge, enthusiasm for software development,
ability to work in teams, and growth mindset. Track their application source, interview
performance on coding challenges, behavioral assessments, and mentor feedback. The evaluation
should consider that they're early in their career and focus on potential rather than proven
track record.
        """,
        """
We're building a hiring system for senior software engineering positions. We need to evaluate
experienced candidates who can lead technical initiatives and mentor teams. The system should
capture their career progression, major projects delivered, architectural decisions made,
technical leadership experience, and impact on business outcomes. We need to assess their
expertise in system design, their ability to navigate ambiguity, their track record of
delivering complex projects, code quality standards, and technical mentorship. The evaluation
should measure their strategic thinking, cross-functional collaboration, ability to influence
technical direction, and experience scaling systems and teams.
        """,
        """
We're building a hiring system for specialized software engineering roles like machine learning
engineers, security engineers, or platform engineers. We need to evaluate candidates with deep
domain expertise. The system should capture their specialized technical skills, relevant
certifications, contributions to the field (publications, patents, open source), and experience
with domain-specific tools and methodologies. We need to assess the depth of their expertise,
their ability to solve complex domain-specific problems, their understanding of best practices
in their specialty, and their ability to translate technical concepts to non-specialists. The
evaluation should consider both breadth of general software engineering skills and depth in
their specialized domain.
        """,
    ]

    run(prompts, "examples/schemas/high_reasoning_examples/job_application_evaluation.json")


def example_5_financial_transaction_analysis() -> None:
    """Example 5: Analyze financial transactions for fraud detection

    Demonstrates multi-prompt unified schema generation for different transaction types.
    The system infers a comprehensive fraud detection structure that works across
    e-commerce purchases, wire transfers, and recurring subscription payments.
    """
    print("\n=== Example 5: Financial Transaction Analysis ===")

    prompts = [
        """
We need a fraud detection system for e-commerce transactions - online purchases made with
credit cards or digital wallets. These transactions happen quickly, involve varying amounts,
and target a wide range of merchants. We need to capture transaction details (amount, currency,
merchant, items purchased), payment method information, shipping vs billing address comparison,
device fingerprinting, IP geolocation, and velocity checks (how many transactions in recent
time periods). Assess risk based on card verification results, AVS matching, unusual purchase
patterns, first-time buyer behavior, high-value items, digital goods purchases, and mismatches
between customer location and shipping destination. Track merchant category risk, time-of-day
patterns, and whether the transaction follows typical user behavior. Flag account takeover
signals like sudden password changes, new devices, or shipping address changes.
        """,
        """
We need a fraud detection system for wire transfers and bank-to-bank payments. These are
high-value, irreversible transactions that require extra scrutiny. We need to capture sender
and recipient bank details, routing information, transfer amounts, purpose codes, beneficiary
information, and international vs domestic indicators. Assess risk based on transfer size
relative to account history, frequency of international transfers, transfers to high-risk
countries, structuring patterns (amounts just below reporting thresholds), and relationships
between sender and recipient. Track compliance requirements like AML screening, sanctions list
checking, politically exposed persons (PEP) identification, and regulatory reporting thresholds.
The system needs to handle both same-day processing decisions and post-transaction monitoring
for suspicious patterns.
        """,
        """
We need a fraud detection system for recurring subscription and membership payments. These
involve ongoing relationships, automatic billing, and subscription lifecycle management. We
need to capture subscription details (service type, billing frequency, amount), payment method
updates, cancellation and reactivation patterns, failed payment attempts, and churn signals.
Assess risk based on unusual subscription stacking (multiple subscriptions in short time),
payment method testing (small charges followed by larger ones), stolen card usage patterns,
friendly fraud indicators (chargebacks after service use), and account sharing across different
locations. Track subscription value changes, upgrade/downgrade patterns, and correlation with
trial period abuse. The system should identify both fraud at signup and ongoing account abuse
while minimizing false positives that could disrupt legitimate long-term customers.
        """,
    ]

    run(prompts, "examples/schemas/high_reasoning_examples/financial_transaction_analysis.json")


def example_6_high_reasoning() -> None:
    """Example 6: Customer review analysis across different product categories

    Demonstrates multi-prompt unified schema generation for analyzing reviews across
    different product types. The system infers a comprehensive structure that works
    for physical products, digital services, and hospitality experiences.
    """
    print("\n=== Example 6: High Reasoning ===")

    prompts = [
        """
Our product team needs to analyze customer reviews for physical consumer electronics products
like smartphones, laptops, and smart home devices. We need to extract insights about product
quality, build materials, design aesthetics, performance benchmarks, battery life, durability
over time, and technical specifications meeting expectations. Understand customer sentiment
about features, ease of setup, software updates, compatibility with other devices, and value
for money. Identify common failure modes, warranty claims patterns, comparison with competitor
products, and whether customers would recommend or repurchase. Track review authenticity,
verified purchase status, reviewer expertise level, and time since purchase. The analysis
should help engineering prioritize quality improvements, marketing understand key selling
points, and product management decide on next generation features.
        """,
        """
Our customer success team needs to analyze reviews for digital subscription services like
streaming platforms, SaaS tools, and online learning platforms. We need to extract insights
about service reliability, content quality and variety, user interface and experience, customer
support responsiveness, subscription value perception, and ease of cancellation. Understand
sentiment about feature updates, content additions or removals, pricing changes, platform
performance across devices, and integration with other tools. Identify reasons for churn,
common complaints, feature requests, comparison with competing services, and likelihood to
recommend. Track subscriber tenure, usage frequency, plan tier, and whether reviews come from
active or cancelled subscribers. The analysis should inform product roadmap, pricing strategy,
content acquisition decisions, and customer retention initiatives.
        """,
        """
Our hospitality team needs to analyze customer reviews for hotels, restaurants, and travel
experiences. We need to extract insights about service quality, staff friendliness and
professionalism, cleanliness and maintenance, ambiance and atmosphere, food quality and
presentation, location convenience, and value for price paid. Understand sentiment about
specific amenities, accessibility, handling of special requests, problem resolution, and
overall experience meeting expectations. Identify peak complaint areas, standout positive
experiences, comparison with nearby competitors, demographic patterns in satisfaction, and
likelihood to return or recommend. Track reviewer travel purpose (business, leisure, family),
group size, season of visit, and booking channel. The analysis should guide staff training,
facility improvements, service protocol updates, and targeted marketing to specific customer
segments.
        """,
    ]

    run(prompts, "examples/schemas/high_reasoning_examples/high_reasoning.json")


if __name__ == "__main__":
    print("Auto-Structured-Output: High Reasoning Examples")
    print("=" * 60)

    # Run examples
    example_1_customer_feedback_analysis()
    example_2_meeting_summary()
    example_3_research_paper_metadata()
    example_4_job_application_evaluation()
    example_5_financial_transaction_analysis()
    example_6_high_reasoning()

    print("=" * 60)
    print("All examples completed!")
