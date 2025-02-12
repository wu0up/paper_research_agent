import operator
from dataclasses import dataclass, field
from typing_extensions import TypedDict, Annotated

@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None) # Report topic     
    search_query: str = field(default=None) # Search query
    web_research_results:list = field(default_factory=list) 
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list) 
    research_loop_count: int = field(default=0) # Research loop count
    running_summary: str = field(default=None) # Final report
    sources_summary_gathered: Annotated[list, operator.add] = field(default_factory=list) 

@dataclass(kw_only=True)
class SummaryStateInput(TypedDict):
    research_topic: str = field(default=None) # Report topic     
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list) 
    web_research_results:list = field(default_factory=list) 

@dataclass(kw_only=True)
class SummaryStateOutput(TypedDict):
    running_summary: str = field(default=None) # Final report

@dataclass(kw_only=True)
class SourceState(TypedDict):
    source_content: str = field(default=None)
    research_topic: str = field(default=None) # Report topic     