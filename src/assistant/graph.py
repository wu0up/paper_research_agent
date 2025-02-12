import json

from typing_extensions import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send

from src.assistant.configuration import Configuration
from src.assistant.utils import deduplicate_and_format_sources, tavily_search, format_sources, extract_json
from src.assistant.state import SummaryState, SummaryStateInput, SummaryStateOutput, SourceState
from src.assistant.prompts import query_writer_instructions, summarizer_instructions, reflection_instructions, query_writer_instructions_update, source_summarizer_instructions
import os
from config import configs as p
from langchain_core.runnables.graph import MermaidDrawMethod
# 在ollama就沒有使用with_structured_output
## 預期:
## 1. ollama的structure output使用 -->只有指定format=json
## 2. 沒有提到怎麼細節去分析paper
## 3. 原本想改成Pdf
## 4. ollama的structure output是提供json結構，但format="json"不可用json

# Nodes   
def generate_query(state: SummaryState, config: RunnableConfig):
    """ Generate a query for web search """
    # Format the prompt
    query_writer_instructions_formatted = query_writer_instructions.format(research_topic=state.research_topic)

    # Generate a query
    configurable = Configuration.from_runnable_config(config)
    llm_json_mode = ChatOllama(model=configurable.local_llm,base_url=p.OLLAMA_BASE_URL,  temperature=0)
    result = llm_json_mode.invoke(
        [SystemMessage(content=query_writer_instructions_formatted),
        HumanMessage(content=f"Generate a query for web search:")]
    )  
    # query = json.loads(result.content)
    query = extract_json(result.content)
    
    return {"research_topic": query['query']}

def summary_each_source(state: SourceState, config: RunnableConfig):
    
    source_content = state.get("source_content")

    human_message_content = (
        "提供一篇paper的內容，生成中文摘要和中文重點，必須包含：1. 中文摘要, 2. 10 個重點, 3. 探討的問題及解決方式 "
        f"\n\n這是一篇paper的內容：\n{source_content} "
        # f"查詢主題：{state.get('research_topic')}"
    )

    # Run the LLM
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, base_url=p.OLLAMA_BASE_URL, temperature=0)
    result = llm.invoke(
        [
            SystemMessage(content=source_summarizer_instructions),
        HumanMessage(content=human_message_content)]
    )
    print('summary_each_source', result.content)

    running_summary = result.content

    # TODO: This is a hack to remove the <think> tags w/ Deepseek models 
    # It appears very challenging to prompt them out of the responses 
    while "<think>" in running_summary and "</think>" in running_summary:
        start = running_summary.find("<think>")
        end = running_summary.find("</think>") + len("</think>")
        running_summary = running_summary[:start] + running_summary[end:]

    return {"sources_summary_gathered": [running_summary]}



def summarize_sources(state: SummaryState, config: RunnableConfig):
    """ Summarize the gathered sources """
    
    # Existing summary
    existing_summary = state.running_summary

    # Most recent web research
    # most_recent_web_research = state.web_research_results[-1]
    most_recent_web_research = state.sources_summary_gathered[-1]

    # Build the human message
    if existing_summary:
        human_message_content = (
            f"Extend the existing summary: {existing_summary}\n\n"
            f"Include new search results: {state.sources_summary_gathered} "
            f"That addresses the following topic: {state.research_topic}"
        )
    else:
        human_message_content = (
            # f"Generate a summary of these search results: {most_recent_web_research} "
            f"Generate a summary of these search results: {state.sources_summary_gathered} "
            f"That addresses the following topic: {state.research_topic}"
        )

    # Run the LLM
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, base_url=p.OLLAMA_BASE_URL, temperature=0)
    result = llm.invoke(
        [SystemMessage(content=summarizer_instructions),
        HumanMessage(content=human_message_content)]
    )

    running_summary = result.content

    # TODO: This is a hack to remove the <think> tags w/ Deepseek models 
    # It appears very challenging to prompt them out of the responses 
    while "<think>" in running_summary and "</think>" in running_summary:
        start = running_summary.find("<think>")
        end = running_summary.find("</think>") + len("</think>")
        running_summary = running_summary[:start] + running_summary[end:]

    return {"running_summary": running_summary}

def reflect_on_summary(state: SummaryState, config: RunnableConfig):
    """ Reflect on the summary and generate a follow-up query """

    # Generate a query
    configurable = Configuration.from_runnable_config(config)
    # llm_json_mode = ChatOllama(model=configurable.local_llm, temperature=0, format="json")
    llm_json_mode = ChatOllama(model=configurable.local_llm,base_url=p.OLLAMA_BASE_URL,  temperature=0)
    result = llm_json_mode.invoke(
        [SystemMessage(content=reflection_instructions.format(research_topic=state.research_topic)),
        HumanMessage(content=f"Identify a knowledge gap and generate a follow-up web search query based on our existing knowledge: {state.running_summary}")]
    )   

    follow_up_query = extract_json(result.content)

    # Overwrite the search query
    return {"search_query": follow_up_query['follow_up_query']}

def continue_to_summary(state: SummaryState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [Send("summary_each_source", {"source_content": s, 'research_topic':state.research_topic}) for s in state.web_research_results]

def finalize_summary(state: SummaryState):
    """ Finalize the summary """
    
    # Format all accumulated sources into a single bulleted list
    all_sources = "\n".join(source for source in state.sources_gathered)
    state.running_summary = f"## Summary\n\n{state.running_summary}\n\n ### Sources:\n{all_sources}"
    return {"running_summary": state.running_summary}

def visulize_graph(graph_model):
        file_name ='graph.png'
        # output_dir = "/data/output/graph_image"
        output_dir = ""
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
        img_data = graph_model.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API)
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(img_data)
        return file_path

def route_research(state: SummaryState, config: RunnableConfig) -> Literal["finalize_summary", "web_research"]:
    """ Route the research based on the follow-up query """

    configurable = Configuration.from_runnable_config(config)

    return "finalize_summary" 
    
# Add nodes and edges 
builder = StateGraph(SummaryState, input=SummaryStateInput, output=SummaryStateOutput, config_schema=Configuration)
builder.add_node("generate_query", generate_query)
builder.add_node("summary_each_source", summary_each_source)
builder.add_node("summarize_sources", summarize_sources)
builder.add_node("reflect_on_summary", reflect_on_summary)
builder.add_node("finalize_summary", finalize_summary)

# Add edges
builder.add_edge(START, "generate_query")
builder.add_conditional_edges("generate_query", continue_to_summary, ["summary_each_source"]) 
builder.add_edge("summary_each_source", "summarize_sources")  
builder.add_edge("summarize_sources", "finalize_summary")
builder.add_edge("finalize_summary", END)

graph = builder.compile()
visulize_graph(graph)