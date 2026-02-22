from dataclasses import dataclass
from random import Random
from typing import Sequence


@dataclass(frozen=True)
class Persona:
    industry: str
    role: str
    pain_point: str
    personality: str
    urgency: str
    primary_objection: str


class PersonaGenerator:
    industries = ["manufacturing", "logistics", "healthcare", "construction", "saas"]
    roles = ["operations_manager", "vp_sales", "it_director", "owner", "procurement_lead"]
    pain_points = ["manual_workflows", "slow_reporting", "high_churn", "low_conversion", "tool_sprawl"]
    personalities = ["skeptical", "direct", "friendly", "impatient", "analytical"]
    urgencies = ["this_quarter", "this_month", "no_rush", "active_project"]
    objections = ["no_budget", "busy", "send_email", "already_vendor", "no_interest"]

    def generate(self, seed: int, recent_sessions: Sequence[dict]) -> Persona:
        rnd = Random(seed)
        recent_objections = {
            session.get("primary_objection")
            for session in recent_sessions
            if session.get("primary_objection")
        }
        available_objections = [o for o in self.objections if o not in recent_objections]
        objection_pool = available_objections or self.objections

        return Persona(
            industry=rnd.choice(self.industries),
            role=rnd.choice(self.roles),
            pain_point=rnd.choice(self.pain_points),
            personality=rnd.choice(self.personalities),
            urgency=rnd.choice(self.urgencies),
            primary_objection=rnd.choice(objection_pool),
        )
