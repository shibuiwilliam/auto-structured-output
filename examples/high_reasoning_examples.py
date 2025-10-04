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


def run(prompt: str, file_name: str):
    T_Model = extractor.extract_structure(prompt, use_high_reasoning=True)

    print(f"Generated model: {T_Model.__name__}")
    print(f"Fields: {T_Model.model_json_schema()}")

    # Use the model
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=T_Model,
    )

    data = response.choices[0].message.parsed
    data_dict = data.model_dump()
    print("\nGenerated data:")
    print(data_dict)

    extractor.save_extracted_json(T_Model, file_name)


def example_1_customer_feedback_analysis():
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

    run(prompt, "examples/schemas/high_reasoning_examples/customer_feedback_analysis.json")


def example_2_meeting_summary():
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

    run(prompt, "examples/schemas/high_reasoning_examples/meeting_summary.json")


def example_3_research_paper_metadata():
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

    run(prompt, "examples/schemas/high_reasoning_examples/research_paper_metadata.json")


def example_4_job_application_evaluation():
    """Example 4: Evaluate job applications

    Infer what information would be valuable when evaluating job candidates
    without prescribing exact evaluation criteria.
    """
    print("\n=== Example 4: Job Application Evaluation ===")

    prompt = """
We're building a hiring system for software engineering positions that needs to evaluate
candidates holistically and support our decision-making process. The system should capture
everything relevant about each applicant - from their basic information and how to reach
them, to where they're currently located and whether they're open to moving for the role.
We need to understand their educational journey, what they studied and where, and any
credentials or learning experiences they've accumulated over time, whether formal or
self-directed.

Their professional history is crucial - we want to know where they've worked, what they've
built, the technologies they've used in practice, the scale of teams and projects they've
been part of, and the tangible impact they've made. This includes understanding the depth
and breadth of their technical capabilities across programming languages, frameworks,
architectural patterns, infrastructure, and any specialized domains they've explored.

Beyond their resume, we're interested in their project work - what they've created, how
they approach problems, their contributions to collaborative efforts or open source, and
any recognition they've received. We also value the human aspects: how they communicate,
how they work with others, whether they've led or mentored, how they adapt to change, and
signals about whether they'd thrive in our culture.

The evaluation itself needs to be systematic yet nuanced - we need ways to rate technical
strength, assess how well their experience aligns with our needs, evaluate potential for
growth, capture interview insights if we have them, and ultimately arrive at a hiring
recommendation. At the same time, we should flag any concerns: unexplained career gaps,
patterns of short tenures, mismatches between their profile and our requirements, or
compensation expectations that don't align.

Throughout the recruiting lifecycle, we need to track operational details: where candidates
came from, when they applied, who's handling their application, what stage they're at, and
how efficiently we're moving them through the process. The entire structure should enable
us to compare candidates fairly, analyze our recruiting pipeline, measure our performance,
and integrate seamlessly with our applicant tracking tools.
    """

    run(prompt, "examples/schemas/high_reasoning_examples/job_application_evaluation.json")


def example_5_financial_transaction_analysis():
    """Example 5: Analyze financial transactions for fraud detection

    Infer what structured information would be useful for fraud detection
    without explicitly defining all risk factors.
    """
    print("\n=== Example 5: Financial Transaction Analysis ===")

    prompt = """
We need a sophisticated fraud detection system that can analyze financial transactions as
they happen and identify potentially suspicious activity before it causes damage. Every
transaction carries a wealth of signals - the basic facts about what's being transacted,
when and where it's happening, how much money is involved, what currencies are at play,
who the merchant or recipient is, how the payment is being made, and what state the
transaction is in at any given moment.

Behind each transaction is an account with its own history and characteristics - how long
it's been active, how verified the user is, their typical transaction patterns and volumes,
their current balance, and any relationships to other accounts or payment instruments. The
context matters immensely: we need to understand not just where the transaction is
originating geographically, but also what device is being used, whether there are signs
of location spoofing or anonymization, and whether the physical movements implied by the
transaction history are even plausible for a human being.

What really reveals fraud is deviation from the norm. We need to detect when someone's
behavior suddenly changes - when they're transacting more frequently than usual, at unusual
times, for unusual amounts, with unfamiliar merchants or in new categories. We need to see
how they compare to their peer group and spot the outliers. Every transaction should get a
risk assessment that considers multiple dimensions of threat - from account takeover to
synthetic identity fraud to money laundering - with some measure of confidence in that
assessment and connections to similar patterns we've seen before.

The relationships between entities matter too. Transactions don't happen in isolation -
they're part of networks where accounts, devices, and IP addresses intersect in meaningful
ways. Following the money through chains of transactions, understanding who benefits,
identifying clusters of related activity - these network patterns often expose coordinated
fraud that individual transaction analysis would miss.

Merchants themselves carry risk. Some industries are riskier than others, some merchants
have concerning chargeback rates, geographical mismatches between merchant and transaction
locations can be suspicious, and newer merchant accounts deserve extra scrutiny, especially
if they've been linked to fraud before. The way users authenticate themselves provides
crucial security signals - what methods they're using, their history of authentication
successes and failures, how they respond to security challenges, and the overall security
posture of their session.

There's also a compliance dimension we can't ignore. Certain transaction patterns trigger
anti-money laundering requirements, we need to screen against sanctions lists, politically
exposed persons require special handling, regulatory thresholds demand reporting, and
different jurisdictions impose different obligations. All of this feeds into our decision-
making process, which must track not just the automated accept or reject decision, but also
when human review is needed, who's investigating, what they're finding, how likely this is
to be a false positive, what we're telling the customer, and how each case ultimately
resolves.

The entire system needs to work in real-time, support our machine learning models, enable
pattern recognition across millions of transactions, satisfy regulatory reporting
requirements, and integrate with our case management tools for investigating and resolving
suspicious activity.
    """

    run(prompt, "examples/schemas/high_reasoning_examples/financial_transaction_analysis.json")


def example_6_high_reasoning():
    """Example 6: Comparison between standard and high reasoning modes

    Demonstrates the difference between standard mode (clear structure)
    and high reasoning mode (inferred structure).
    """
    print("\n=== Example 6: High Reasoning ===")

    prompt = """
Our product team needs deep insights from customer reviews to drive decisions across
development, marketing, and customer experience. We're drowning in review data but
struggling to extract actionable intelligence that different teams can actually use.

Start with the basics - we need to know what product we're even talking about, including
all its identifiers, what it costs, when people are buying it, and where it sits in its
lifecycle. From there, we need the big picture on sentiment: what are people saying
overall, how is that sentiment distributed, how has it changed over time, and can we trust
these reviews are genuine? Star ratings matter, but we need to understand what's behind
them.

The real value comes from understanding specific aspects of the product. When customers
talk about quality, design, how it works, how long it lasts, how easy it is to use, whether
it's worth the money - each of these dimensions tells a different story. We need to know
not just what they're saying about each aspect, but how often they're talking about it and
which aspects matter most to their overall satisfaction.

Who are these customers anyway? We need to read between the lines of reviews to understand
different customer segments - their ages, how they're using the product, their level of
expertise, what scenarios they're using it in, and what motivated them to buy it in the
first place. Different personas will emerge from this data if we look carefully enough.

Quality and performance issues tell us where to focus our engineering efforts. What's
actually breaking or failing? How does reality compare to what we promised? What wears out
too quickly? Are there patterns in defects or failure modes? How reliable is this product
really proving to be over time? These signals guide our quality roadmap.

We can't ignore the competitive landscape either. When customers mention other products,
when they compare us to alternatives, when they talk about why they chose us or wish they
hadn't - this is gold for positioning and strategy. We need to understand our relative
strengths and weaknesses and where we sit in the market from the customer's perspective.

The user experience journey matters from the moment they open the box. How hard is it to
get started? What's the learning curve like? Are our docs helpful? When they need support,
what happens? Even packaging and presentation influence perception. And we can't forget
accessibility - are we serving all potential customers well?

Price is always complicated. The same product at the same price can feel like a steal or a
ripoff depending on the customer and their experience. We need to understand satisfaction
with value, how different segments perceive the cost-benefit tradeoff, what discounts do to
satisfaction, whether people would recommend us or buy again, and how value perception
varies across different types of customers.

All of this should point us toward what to build or fix next. What features do customers
keep asking for? What frustrates them most? What design choices are backfiring? What's hard
to use? What's missing entirely? We need to prioritize improvements based not just on what
people say, but how often they say it and how much it matters to their experience.

Finally, not all reviews are created equal. We need to assess credibility and quality -
which reviews are actually helpful, which ones are detailed and thoughtful, which include
evidence like photos or videos, which might be fake or manipulated, and whether there are
suspicious patterns in when and how reviews appear. This meta-analysis helps us weight
everything else appropriately.

All of this intelligence should flow into concrete actions: shaping our product roadmap,
refining our marketing messages, prioritizing quality improvements, understanding our
competitive position, and making customers happier. The structure needs to support all
these different uses while being rigorous enough for data-driven decision making.
    """

    run(prompt, "examples/schemas/high_reasoning_examples/high_reasoning.json")


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
