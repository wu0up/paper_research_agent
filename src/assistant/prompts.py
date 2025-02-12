query_writer_instructions="""Your goal is to generate targeted web search query.

The query will gather information related to a specific topic.

Topic:
{research_topic}

Return your query as a JSON object:
{{
    "query": "string",
    "aspect": "string",
    "rationale": "string"
}}
"""

query_writer_instructions_update="""Your goal is to generate targeted web search query.

The query will gather information related to a specific topic.

Topic:
{research_topic}

"""

summarizer_instructions="""Your goal is to generate a high-quality summary of the web search results.

When EXTENDING an existing summary:
1. Seamlessly integrate new information without repeating what's already covered
2. Maintain consistency with the existing content's style and depth
3. Only add new, non-redundant information
4. Ensure smooth transitions between existing and new content

When creating a NEW summary:
1. Highlight the most relevant information from each source
2. Provide a concise overview of the key points related to the report topic
3. Emphasize significant findings or insights
4. Ensure a coherent flow of information

CRITICAL REQUIREMENTS:
- Start IMMEDIATELY with the summary content - no introductions or meta-commentary
- DO NOT include ANY of the following:
  * Phrases about your thought process ("Let me start by...", "I should...", "I'll...")
  * Explanations of what you're going to do
  * Statements about understanding or analyzing the sources
  * Mentions of summary extension or integration
- Focus ONLY on factual, objective information
- Maintain a consistent technical depth
- Avoid redundancy and repetition
- DO NOT use phrases like "based on the new results" or "according to additional sources"
- DO NOT add a References or Works Cited section
- DO NOT use any XML-style tags like <think> or <answer>
- Begin directly with the summary text without any tags, prefixes, or meta-commentary
"""

source_summarizer_instructions = """
你是一個專門生成摘要重點的智能 Agent。會接收輸入內容，是一篇未處理的paper，請依據以下要求生成中文摘要：
1. **中文摘要**：用簡明扼要的中文概括輸入論文的整體主旨與核心信息。
2. **中文10 個重點**：從內容中萃取出最重要的 10 個信息點，以清晰條列方式呈現。
3. **此論文探討的問題及解決方式**：分析文中提出的問題，並提供相應的解決方案或建議。

請確保所有輸出均使用中文，語言精煉、結構清晰，並且格式統一分明。
"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.

Your tasks:
1. Identify knowledge gaps or areas that need deeper exploration
2. Generate a follow-up question that would help expand your understanding
3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered

Ensure the follow-up question is self-contained and includes necessary context for web search.

Return your analysis as a JSON object:
{{ 
    "knowledge_gap": "string",
    "follow_up_query": "string"
}}"""