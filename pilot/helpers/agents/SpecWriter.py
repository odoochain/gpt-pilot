from helpers.AgentConvo import AgentConvo
from helpers.Agent import Agent
from utils.files import count_lines_of_code
from utils.style import color_green_bold, color_green
from prompts.prompts import ask_user


class SpecWriter(Agent):
    def __init__(self, project):
        super().__init__('spec_writer', project)
        self.save_dev_steps = True

    def analyze_project(self, initial_prompt):
        print(color_green_bold("Let's start by refining your project idea:"))

        convo = AgentConvo(self)
        convo.construct_and_add_message_from_prompt('spec_writer/ask_questions.prompt', {})

        user_response = initial_prompt
        while True:
            llm_response = convo.send_message('utils/python_string.prompt', {
                "content": user_response,
            })
            if not llm_response:
                continue

            llm_response = llm_response.strip()
            if len(llm_response) > 500:
                user_response = ask_user(
                    self.project,
                    "Can we proceed with this project description? If so, just press ENTER. Otherwise, please provide a comment, addition or change you want in this specification.",
                    hint="Does this sound good, and does it capture all the information about your project?",
                    require_some_input=False
                )
                if user_response:
                    user_response = user_response.strip()
                if user_response.lower() in ["", "yes", "ok", "y", "continue"]:
                    break
            else:
                user_response = ask_user(self.project, llm_response)

        return llm_response


    def review_spec(self, initial_prompt, spec):
        convo = AgentConvo(self, temperature=0)
        llm_response = convo.send_message('spec_writer/review_spec.prompt', {
            "brief": initial_prompt,
            "spec": spec,
        })
        if not llm_response:
            return None
        return llm_response.strip()

    def create_spec(self, initial_prompt):
        if len(initial_prompt) > 2000:
            return initial_prompt

        spec = self.analyze_project(initial_prompt)
        missing_info = self.review_spec(initial_prompt, spec)
        if missing_info:
            spec += "\nAdditional info/examples:\n" + missing_info

        return spec
