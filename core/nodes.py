import json
import operator

from datetime import datetime
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence, List

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import FunctionMessage
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from sentence_transformers import SentenceTransformer

from elastic import es
from prompts import validate, assistant, continue_chat

load_dotenv()

model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o-mini")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def verify_information(topic: str, information: str) -> bool:
    """
    Verifies the accuracy of the provided information related to a specific topic.

    This function sends a request to a model to validate whether the given information
    about the specified topic is accurate. It constructs a system prompt and a human message,
    invokes the model, and returns `True` if the model confirms the information is true,
    otherwise returns `False`.

    Args:
        topic (str): The subject area or topic related to the information being verified.
        information (str): The specific information or statement that needs verification.

    Returns:
        bool:
            - `True` if the information is verified as accurate.
            - `False` if the information is not verified or deemed inaccurate.
    """
    system_prompt = SystemMessage(content=validate)
    query_message = HumanMessage(content=f"topic: {topic}, information: {information}")
    response = model.invoke([system_prompt, query_message], function_call="none")
    return bool(response.content.strip().lower() == "true")


@tool("store_information", return_direct=True)
def store_information(topic: str, information: str) -> str:
    """
    Stores verified information related to a specific topic.

    This function verifies the accuracy of the provided information about a given topic using the `verify_information` function.
    If the information is valid, it generates a semantic vector for the information, creates a document with relevant details,
    and indexes it into Elasticsearch under the "chatbot_info" index. It returns a confirmation message upon successful
    storage or an error message if the operation fails.

    Args:
        topic (str): The subject or area of interest related to the information.
        information (str): The specific information to be stored.

    Returns:
        str:
            - A message confirming that the information has been successfully stored.
            - An error message if verification fails or an exception occurs during storage.
    """
    try:

        if not verify_information(topic, information):
            raise Exception("False information")

        vector = embedding_model.encode(information).tolist()
        doc = {
            "topic": topic,
            "information": information,
            "vector": vector,
            "timestamp": datetime.now().timestamp(),
        }
        es.index(index="chatbot_info", document=doc)

        return f"Information stored for topic: {topic} for future reference"

    except Exception as e:
        return f"Unable to save information: {str(e)}"


@tool("retrieve_information", return_direct=True)
def retrieve_information(topic: str) -> str:
    """
    Retrieves relevant information related to a specific topic.

    This function encodes the provided topic into a semantic vector and constructs a search query
    using cosine similarity to find the most relevant information stored in the "chatbot_info" Elasticsearch index.
    It returns the retrieved information along with their corresponding scores. If no relevant information is found
    or an error occurs during the retrieval process, an appropriate message is returned.

    Args:
        topic (str): The subject or area of interest for which information is to be retrieved.

    Returns:
        str:
            - A concatenated string of relevant information entries along with their similarity scores.
            - A message indicating that no relevant information was found for the given topic.
            - An error message if an exception occurs during the retrieval process.s
    """
    try:

        query_vector = embedding_model.encode(topic).tolist()

        search_body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": query_vector},
                    },
                }
            }
        }

        res = es.search(index="chatbot_info", body=search_body)
        hits = res["hits"]["hits"]
        if not hits:
            return f"No relevant information was found for the topic: {topic}"

        information = "\n".join(
            [
                f"{hit['_source']['information']} (score: {hit['_score']:.2f})"
                for hit in hits
            ]
        )
        return information

    except Exception as e:
        return f"Error recovering information: {str(e)}"


tools = [store_information, retrieve_information]
tool_executor = ToolExecutor(tools)
functions = [convert_to_openai_function(t) for t in tools]
model = model.bind_functions(functions)


def should_continue(state):
    """
    Determines whether the conversation with the chatbot should continue or end.

    This function evaluates the content of the most recent message in the conversation
    and invokes the model to decide the next step. It uses a predefined system message
    to provide context for the model and sends the latest user message as input.
    The function then analyzes the model's response to determine if the conversation
    should continue or terminate.

    Args:
        state (dict): A dictionary representing the current state of the conversation.
                      It must contain a key "messages" with a sequence of message objects,
                      where the last message represents the latest user or assistant input.

    Returns:
        str:
            - "end" if the model's response suggests the conversation should terminate.
            - "continue" if the conversation should proceed.
    """
    messages = state["messages"]
    last_message = messages[-1]

    system_prompt = SystemMessage(content=continue_chat)
    query_message = HumanMessage(content=last_message.content)
    response = model.invoke([system_prompt, query_message], function_call="none")
    return "end" if "end" in response.content.lower() else "continue"


def call_model(state):
    """
    Invokes the model to generate a response based on the current state of the conversation.

    This function takes the conversation history stored in the `state` parameter,
    passes it to the model for processing, and returns the model's response.
    It is a core function for generating the next message in the conversation.

    Args:
        state (dict): A dictionary representing the current state of the conversation.
                      It must contain a key "messages" with a sequence of message objects
                      that represent the conversation history.

    Returns:
        dict: A dictionary containing the model's response under the key "messages".
              The response is wrapped in a list to maintain consistency with the message structure.
    """
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


def call_tool(state):
    """
    Invokes a specified tool based on the last message in the conversation state.

    This function checks if the latest message in the conversation includes a `function_call`
    in its additional keyword arguments. If a `function_call` is present, it extracts the
    tool's name and input arguments, invokes the corresponding tool, and returns the tool's
    response as a `FunctionMessage`. If no `function_call` is found, it returns an empty message list.

    Args:
        state (dict): A dictionary representing the current state of the conversation.
                      It must contain a key "messages" with a sequence of message objects,
                      where the last message may contain a `function_call`.

    Returns:
        dict: A dictionary containing the tool's response message under the key "messages".
              If no `function_call` is present in the last message, it returns an empty list
              for "messages".
    """
    messages = state["messages"]
    last_message = messages[-1]

    if not "function_call" in last_message.additional_kwargs:
        return {"messages": []}

    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(
            last_message.additional_kwargs["function_call"]["arguments"]
        ),
    )
    print(f"Call Tool --> {action}")
    response = tool_executor.invoke(action)
    function_message = FunctionMessage(content=str(response), name=action.tool)
    return {"messages": [function_message]}


def has_new_messages(state):
    """
    Determines whether the conversation should continue based on the type of the last message.

    This function inspects the last message in the conversation state and decides whether
    the conversation should proceed. If the last message is a `FunctionMessage`, it indicates
    that there is new information to process, and the conversation should continue. Otherwise,
    it assumes the conversation has reached an endpoint.

    Args:
        state (dict): A dictionary representing the current state of the conversation.
                      It must contain a key "messages" with a sequence of message objects,
                      where the last message is evaluated.

    Returns:
        str:
            - "continue" if the last message is a `FunctionMessage`, indicating new information.
            - "end" if the last message is not a `FunctionMessage`, suggesting no further steps.
    """
    messages = state["messages"]
    last_message = messages[-1]
    return "continue" if isinstance(last_message, FunctionMessage) else "end"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)
workflow.add_edge("agent", "action")

workflow.add_conditional_edges(
    "action", has_new_messages, {"continue": "agent", "end": END}
)

workflow.set_entry_point("agent")
app = workflow.compile()

system_message = SystemMessage(content=assistant)


def chatbot(messages: List[dict]):

    user_messages = []
    for message in messages:
        if message.get("role") == "user":
            user_messages.append(HumanMessage(content=message.get("content", "")))
        user_messages.append(AIMessage(content=message.get("content", "")))
    inputs = {"messages": [system_message] + user_messages}
    result = app.invoke(inputs)
    return result["messages"][-1].content
