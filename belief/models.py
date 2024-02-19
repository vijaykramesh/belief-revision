import abc
import textwrap
from typing import List

import autogen
import dotenv


class Experiment:
    def __init__(self, truth_box: str):
        self.truth_box = truth_box
        self.evidence_instances: List[EvidenceInstance] = []
        config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")
        self.llm_config = {"config_list": config_list, "cache_seed": None}

        self.subject = autogen.AssistantAgent(
            "subject",
            system_message=self.subject_system_message(),
            llm_config=self.llm_config,
        )

    def add_evidence(self, evidence_strength, evidence_box):
        if evidence_strength not in ["weak", "medium", "strong"]:
            raise ValueError("Evidence strength must be weak, medium, or strong")
        if evidence_box not in ["A", "B"]:
            raise ValueError("Evidence box must be A or B")
        if evidence_strength == "weak":
            strength = WeakEvidence(evidence_box)
        elif evidence_strength == "medium":
            strength = MediumEvidence(evidence_box)
        else:
            strength = StrongEvidence(evidence_box)

        self.evidence_instances.append(
            EvidenceInstance(strength, evidence_box, self.truth_box)
        )

    def researcher_system_message(self):
        if len(self.evidence_instances) == 1:
            # filler trial
            return "TODO"
        elif len(self.evidence_instances) == 2:
            first_modifier = (
                "does"
                if self.evidence_instances[0].evidence_box == self.truth_box
                else "does not"
            )
            first_evidence = f"This first {self.evidence_instances[0].strength} evidence will come from Box {self.evidence_instances[0].evidence_box} that {first_modifier} have the reward in it."
            second_modifier = (
                "does"
                if self.evidence_instances[1].evidence_box == self.truth_box
                else "does not"
            )
            second_evidence = f"This second {self.evidence_instances[1].strength} evidence will come from Box {self.evidence_instances[1].evidence_box} that {second_modifier} have the reward in it."
            return textwrap.dedent(
                f"""
                            You are a researcher who will conduct an experiment into belief revision.
                            You are going to present the subject with a simple task (hiding a reward in one of two boxes).
                            You have hidden the reward in Box {self.truth_box} but the subject does not know this.
                            You are now going to present some evidence to the subject.  You should never tell them the strength of the evidence.
                            {first_evidence}
                            After they consider their options you should then present the second piece of evidence.
                            {second_evidence}
                            To present the second evidence you should tell them "{self.evidence_instances[1].strength.describe()}"

                            After you have provided the second piece of evidence they will decide which box to choose.
                            Only after they do this should you report whether they were correct or not and whether they revised their belief.
                            For this final message you should output one of the following: "SUCCESS_REVISED" "SUCCESS_NOREVISE" "FAILURE_REVISED" "FAILURE_NOREVISE" and then TERMINATE.
                            Make sure you do not output one of those "SUCCESS_REVISED" "SUCCESS_NOREVISE" "FAILURE_REVISED" "FAILURE_NOREVISE" messages until after the subject has made their decision.
                            """
            )
        else:
            raise ValueError("Too many evidence instances")

    def subject_system_message(self):
        return textwrap.dedent(
            """
            You are a problem solving agent who will take part in an experiment.
            You should try to solve the task given by the researcher to the best of your ability.
            You cannot interact with any of the objects but can only tell the researcher what to do.
            """
        )

    def initial_message(self):
        first_evidence = self.evidence_instances[0].strength.describe()
        return textwrap.dedent(
            f"""
            I have hidden a reward in one of these two boxes (Box A and Box B).
            I will give you some evidence as to which box the reward is in.
            You should not yet take it but think about the evidence you got.
            Then I am going to provide some other evidence as to which box the reward is in.
            Only then should you pick which box you think the reward is in.
            {first_evidence}
            """
        )

    def run_experiment(self):
        researcher = autogen.UserProxyAgent(
            "researcher",
            system_message=self.researcher_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config=False,
        )
        groupchat = autogen.GroupChat(
            agents=[self.subject, researcher],
            messages=[],
            max_round=5,
            allow_repeat_speaker=False,
            speaker_selection_method="round_robin",
        )
        manager = autogen.GroupChatManager(
            groupchat=groupchat, llm_config=self.llm_config
        )

        response = researcher.initiate_chat(manager, message=self.initial_message())
        summary = response.summary.lower()
        if "success_revised" in summary:
            return {"correct": True, "revised": True}
        elif "success_norevise" in summary:
            return {"correct": True, "revised": False}
        elif "failure_revised" in summary:
            return {"correct": False, "revised": True}
        elif "failure_norevise" in summary:
            return {"correct": False, "revised": False}
        else:
            raise ValueError("Unexpected summary")


class EvidenceStrength(abc.ABC):
    def __init__(self, strength_type, box):
        self.strength_type: str = strength_type
        self.box: str = box

    def describe(self):
        raise NotImplementedError


class WeakEvidence(EvidenceStrength):
    def __init__(self, box):
        super().__init__("weak", box)

    def describe(self):
        return f"I shake Box {self.box} and you hear a noise."


class StrongEvidence(EvidenceStrength):
    def __init__(self, box):
        super().__init__("strong", box)

    def describe(self):
        return f"I turn around Box {self.box} and you see a reward inside."


class MediumEvidence(EvidenceStrength):
    def __init__(self, box):
        super().__init__("strong", box)

    def describe(self):
        return f"You see a glittering trail that leads up to Box {self.box}."


class EvidenceInstance:
    def __init__(
        self, evidence_strength: EvidenceStrength, evidence_box: str, truth_box: str
    ):
        self.strength: EvidenceStrength = evidence_strength
        self.evidence_box = evidence_box
        self.truth_box = truth_box
