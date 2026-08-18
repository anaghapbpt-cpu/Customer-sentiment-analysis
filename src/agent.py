from typing import Dict, List, Tuple, Any

def generate_business_insights(
    summary: Dict[str, Any],
    themes: List[Tuple[str, int]],
    samples: List[str]
) -> Dict[str, str]:
    """
    Generates rule-based business intelligence summaries based on computed metrics.
    """
    total = summary.get("total_reviews", 0)
    pos_pct = summary.get("positive_percentage", 0.0)
    neg_pct = summary.get("negative_percentage", 0.0)
    neg_count = summary.get("negative_reviews", 0)

    # 1. Situation Assessment
    if total == 0:
        situation = "No customer reviews are currently available for assessment."
    elif pos_pct >= 80:
        situation = f"Exceptional customer satisfaction ({pos_pct:.1f}% positive across {total} reviews). Brand sentiment is highly resilient."
    elif pos_pct >= 60:
        situation = f"Healthy baseline sentiment with {pos_pct:.1f}% positive reviews, though {neg_pct:.1f}% of feedback contains critical customer friction points."
    elif pos_pct >= 40:
        situation = f"Mixed customer sentiment ({pos_pct:.1f}% positive vs {neg_pct:.1f}% negative). Immediate operational interventions are advised to protect retention."
    else:
        situation = f"Critical sentiment deficit: {neg_pct:.1f}% negative reviews detected ({neg_count} dissatisfied customers). High churn risk observed."

    # 2. Main Problems & Pain Points
    if not themes:
        if neg_count > 0:
            problems = f"Detected {neg_count} negative reviews, but feedback lacks concentrated keyword clusters. Qualitative sampling highlights individual user friction."
        else:
            problems = "No prominent operational bottlenecks or customer complaints identified in this batch."
    else:
        top_theme_strs = [f"**{theme}** ({count} incident{'s' if count > 1 else ''})" for theme, count in themes[:3]]
        problems = f"Primary customer complaints originate from: {', '.join(top_theme_strs)}."

    # 3. Recommended Actions
    actions = []
    theme_names = [t[0] for t in themes]
    
    if any("Shipping" in t for t in theme_names):
        actions.append("Audit fulfillment & carrier SLAs to reduce transit delays and enhance proactive package tracking notifications.")
    if any("Damage" in t or "Packaging" in t for t in theme_names):
        actions.append("Re-evaluate warehouse packaging standards and padding materials for fragile product lines.")
    if any("Battery" in t or "Power" in t for t in theme_names):
        actions.append("Initiate QA hardware review on battery lifecycle and clarify recommended charging guidelines in user manuals.")
    if any("Support" in t or "Refund" in t for t in theme_names):
        actions.append("Streamline ticketing queues and automate refund approval workflows to lower first-response time.")
    if any("Quality" in t or "Durability" in t for t in theme_names):
        actions.append("Liaise with manufacturing/procurement to address defect rates and inspect tier-1 supplier components.")
    if any("Pricing" in t for t in theme_names):
        actions.append("Review value-proposition messaging and consider competitive tier-based promotional discounts.")
    if any("Software" in t or "Bugs" in t for t in theme_names):
        actions.append("Prioritize regression patches for reported crashes and onboarding flow friction.")
    
    if not actions:
        if neg_count > 0:
            actions.append("Conduct direct 1-on-1 customer outreach with dissatisfied reviewers to resolve outstanding service tickets.")
        else:
            actions.append("Maintain high product standards and deploy automated loyalty / referral campaigns for delighted customers.")

    recommendations = "\n".join([f"- {act}" for act in actions])

    # 4. Priority Assessment
    if neg_pct > 40 or any(count >= max(3, int(total * 0.25)) for _, count in themes):
        priority = "🔴 **HIGH PRIORITY** — Urgent management attention required. Immediate customer experience bottlenecks detected."
    elif neg_pct > 20:
        priority = "🟡 **MEDIUM PRIORITY** — Operational monitoring and targeted workflow improvements recommended within the current sprint."
    else:
        priority = "🟢 **LOW PRIORITY** — Sentiment metrics within standard healthy tolerance thresholds. Focus on continuous improvement."

    return {
        "Situation": situation,
        "Main Problems": problems,
        "Recommended Actions": recommendations,
        "Priority": priority
    }
