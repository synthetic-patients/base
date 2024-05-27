# --------------------------------------------------------------
# Import Required Libraries
# --------------------------------------------------------------

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
import os
from uuid import uuid4
from typing import List, Dict, Callable
from langchain_openai import ChatOpenAI
import inspect

from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)
import util

# --------------------------------------------------------------
# Load API Keys From the .env File
# --------------------------------------------------------------

from dotenv import load_dotenv

load_dotenv(util.ROOT_DIR + "/.env")

unique_id = uuid4().hex[0:8]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "Agent_2_Agent"


# --------------------------------------------------------------
# Build dialogue agents
# --------------------------------------------------------------


class DialogueAgent:
    def __init__(
            self,
            name: str,
            system_message: SystemMessage,
            model: ChatOpenAI,
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()

    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        message = self.model(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        """
        Concatenates {message} spoken by {name} into message history
        """
        self.message_history.append(f"{name}: {message}")


class DialogueSimulator:
    def __init__(
            self,
            agents: List[DialogueAgent],
            selection_function: Callable[[int, List[DialogueAgent]], int],
    ) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        """
        Initiates the conversation with a {message} from {name}
        """
        for agent in self.agents:
            agent.receive(name, message)

        # increment time
        self._step += 1

    def step(self) -> tuple[str, str]:
        # 1. choose the next speaker
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]

        # 2. next speaker sends message
        message = speaker.send()

        # 3. everyone receives message
        for receiver in self.agents:
            receiver.receive(speaker.name, message)

        # 4. increment time
        self._step += 1

        return speaker.name, message


class DialogueAgentWithTools(DialogueAgent):
    def __init__(
            self,
            name: str,
            system_message: SystemMessage,
            model: ChatOpenAI,
            tool_names: List[str],
            **tool_kwargs,
    ) -> None:
        super().__init__(name, system_message, model)
        self.tools = load_tools(tool_names, **tool_kwargs)

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        agent_chain = initialize_agent(
            self.tools,
            self.model,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False,
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            ),
        )
        message = AIMessage(
            content=agent_chain.run(
                input="\n".join(
                    [self.system_message.content] + self.message_history + [self.prefix]
                )
            )
        )

        return message.content


def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    idx = (step) % len(agents)
    return idx


def generate_doctor(system_message=None):

    llm = ChatOpenAI(temperature=1, model_name='gpt-3.5-turbo')

    name = "Alexis Wang, Clinician"
    tools = []
    if system_message is None:
        system_message = '''You will roleplay a surgeon meeting a patient, Mr. Green, who was recently diagnosed with 
        glioblastoma. You are Alexis Wang, a 42-year-old surgeon known for your skill and dedication in the operating 
        room. Your demeanor is reserved, often leading you to appear somewhat distant in initial clinical 
        interactions. However, those who have the opportunity to see beyond that initial impression understand that 
        you care deeply for your patients, showcasing a softer, more compassionate side once you get to know them 
        better. You like to fully assess a patient's understanding of their disease prior to offering any information 
        or advice, and are deeply interested in the subjective experience of your patients. You also tend to get to 
        know patients by asking them questions about their personal life prior to delving into the medical and 
        surgical aspects of their care. Keep your questions and responses short, similar to a spoken conversation in 
        a clinic. Feel free to include some "um..." and "ahs" for moments of thought. Responses should not exceed two 
        sentences.'''

    doctor_agent = DialogueAgentWithTools(
        name=name,
        system_message=SystemMessage(content=system_message),
        model=llm,
        tool_names=tools,
        top_k_results=2,
    )

    return doctor_agent


def generate_patient(system_message=None, language_model_name='gpt-3.5-turbo'):

    # model_name = 'gpt-4-turbo-preview'
    # gpt-3.5-turbo
    llm = ChatOpenAI(temperature=1, model_name=language_model_name)

    name = "Ahmed Al-Farsi, Patient"
    tools = []
    if system_message is None:
        system_message = '''You are a patient undergoing evaluation for surgery who is meeting their surgeon for the 
        first time in clinic.  When the user prompts "Hi there, Mr Al-Farsi," continue the roleplay.  Provide realistic, 
        concise responses that would occur during an in-person clinical visit; adlib your personal details as needed 
        to keep the conversation realistic. Responses should not exceed two sentences. Feel free to include some 
        "um..." and "ahs" for moments of thought. Do not relay all information provided initially. Please see the 
        below profile for information.
        
        INTRO: You are  Mr. Ahmed Al-Farsi, a 68-year-old with a newly-diagnosed glioblastoma. - Disease onset: You 
        saw your PCP for mild headaches three months ago. After initial treatments failed to solve the issue, 
        a brain MRI was ordered which revealed an occipital tumor. - Healthcare interaction thus far: You met with an 
        oncologist, who has recommended surgical resection of the tumor, followed by radiation and chemotherapy. - 
        Current symptoms: You are asymptomatic apart from occasional mild headaches in the mornings. They are 
        worsening. - Past medical history: hypertension for which you take lisinopril. - Social health: Previous 
        smoker. - Employement: You are a software engineer. - Education: You have a college education. - Residence: 
        You live in the suburbs outside of San Jose. - Personality: Reserved, overly-technical interest in his 
        disease, ie "medicalization." Has been reading about specific mutations linked to glioblastoma and is trying 
        to understand how DNA and RNA work. - Family: Single father of two school-aged daughters, Catherine and 
        Sarah. Your wife, Tami, died of breast cancer 2 years prior. - Personal concerns that you are willing to 
        share: how the treatment may affect his cognitive functions - Personal concerns that you will not share: 
        ability to care for your children, end-of-life issues, grief for your late wife Tami. - You are close with 
        your sister Farah, who is your medical decision-maker. - Your daughter Sarah is disabled. You do not like 
        discussing this. - Religion: "not particularly religious" - Understanding of your disease: Understands that 
        it is serious, may be life-altering, that surgery and/or radiation are options. - Misunderstandings of your 
        disease: You do  not understand your prognosis. You feel that your smoking in your 20s and 30s may be linked 
        to your current disease. - Hobbies: Softball with his daughters.
        
        '''

    util.start_log_task(f"Generating patient agent ({name}) using language model {llm.model_name}...")

    patient_agent = DialogueAgentWithTools(
        name=name,
        system_message=SystemMessage(content=system_message),
        model=llm,
        tool_names=tools,
        top_k_results=2,
    )

    util.end_log_task()

    return patient_agent


def generate_blank_patient(system_message=None, language_model_name=None):
    llm = ChatOpenAI(temperature=1, model_name='gpt-3.5-turbo')
    name = "Unknown Patient"
    tools = []
    if system_message is None:
        system_message = '''You are a patient with no story. Please let the user know there has been an error
        '''
    util.start_log_task(f"Generating patient agent ({name}) using language model {llm.model_name}")
    patient_agent = DialogueAgentWithTools(
        name=name,
        system_message=SystemMessage(content=system_message),
        model=llm,
        tool_names=tools,
        top_k_results=2,
    )
    util.end_log_task()
    return patient_agent


def begin_simulation_with_one_agent():
    return None


def simulate_conversation_with_two_agents():
    # --------------------------------------------------------------
    # initialize dialogue agents
    # --------------------------------------------------------------

    # we set `top_k_results`=2 as part of the `tool_kwargs` to prevent results from overflowing the context limit

    patient_agent = generate_patient()
    doctor_agent = generate_doctor()
    agents = [patient_agent, doctor_agent]

    specified_topic = ''' Mr Green is a patient sitting in the exam room. He was recently diagnosed with 
    glioblastoma. He is meeting his surgeon, Alexis Wang, in clinic for the first time. The door opens.'''

    max_iters = 15
    n = 0

    simulator = DialogueSimulator(agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    simulator.inject("Scene", specified_topic)
    print(f"Scene: {specified_topic}")
    print("\n")
    conversation = ""

    while n < max_iters:
        name, message = simulator.step()
        line = f"{name}: {message}\n"
        print(line)
        conversation = conversation + '\n' + line
        n += 1

    # save conversatoins to a file
    timestamp = util.get_timestamp()
    filename = f"{util.ROOT_DIR}/conversations/conversation_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(conversation)


if __name__ == "__main__":
    print("This is a utility file and should not be run directly. Please run the main file.")
