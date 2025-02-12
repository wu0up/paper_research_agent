from fastapi import Request, FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.assistant.graph import graph
from langfuse.callback import CallbackHandler
from urllib.parse import unquote
from src.assistant.folder_manage import TempFileManager
from src.assistant.utils import doc_to_text_unstructured
import asyncio
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# 使用ollama的效果不太好，不確定是ollama的model對於pydamic的能力不好，還是tool使用能力...
# 有一些開源模型，沒有tool的能力
public_key="pk-lf-0dc69e48-63af-4c3e-beeb-b322d4bcb3ca"
secret_key="sk-lf-5b0e6991-b8c5-451b-86d3-0156648c2c7e"
host = "https://langfuse.datafabric.iii-ei-stack.com"

langfuse_handler = CallbackHandler(
            public_key=public_key,
            secret_key=secret_key, 
            host=host,
        )

TempFolder = TempFileManager()
config = {"callbacks": [langfuse_handler]}

tags_metadata = []

app = FastAPI(
        title="TEST",
        summary="Base on LangChain API Documentation(https://python.langchain.com/docs).",
        description=f"""
        IAPP_NAME::: TEST
        IAPP_API_URL:::TEST
        """,
        version="3.0.0",
        openapi_tags=tags_metadata,
        servers=[{
            "url": ""
        }])


@app.post("/start")
async def preprocess_doc(
    text: str,
    files: List[UploadFile] = File(...),
    
):
    """
   Processes the uploaded documents and returns the results.

   Args:
       files (List[UploadFile]): A list of uploaded files to be processed.
       kdb_id (str, optional): The ID of the knowledge database to use. Defaults to "default".

   Returns:
       result: The result of processing the uploaded documents.
   """
    query =text
    # temp_file_paths=[]
    web_research_results=[]
    sources_gathered=[]

    #TODO:改併行
    # for file in files:
    #     file_name = unquote(file.filename)
    #     # file_name = file.filename
    #     content = await file.read()
    #     temp_file_path = TempFolder.create_temp_files(file_name, content, "default")
    #     content =  await doc_to_text_unstructured(temp_file_path)
    #     content_str = f'Sources:{file_name} relevant content from source: {content}'
    #     web_research_results.append(content_str)
    #     sources_gathered.append(file_name)
    web_research_results, sources_gathered = await process_files_parallel(files, TempFolder)
    input_content = {"messages": ("human", query), "research_topic":query, "sources_gathered": sources_gathered, "web_research_results": web_research_results}
    async for event in graph.astream_events(input = input_content,version="v2" , config = config):
            
            # print('event', event)
            result  = event
            # chunk["messages"][-1].pretty_print()
            # if 'structure_output' in event:
            #     response = event["structure_output"]
            # else:
            #     response = event["messages"][-1].content
        #     final_chunk = event
        # # print('final_chunk', final_chunk)
        # if "structure_output" in final_chunk["data"]["output"]:
        #     response = final_chunk["data"]["output"]['structure_output']
        # else:
        #     response = final_chunk["data"]["output"]['messages'][-1].content

    return result

async def process_single_file(file, temp_folder):
    """處理單一檔案的非同步函式"""
    file_name = unquote(file.filename)
    content = await file.read()
    
    # 創建臨時檔案
    temp_file_path = temp_folder.create_temp_files(file_name, content, "default")
    
    # 讀取文件內容
    content = await doc_to_text_unstructured(temp_file_path)
    
    # 格式化結果
    content_str = f'Sources:{file_name} relevant content from source: {content}'
    
    return {
        'content_str': content_str,
        'file_name': file_name
    }

async def process_files_parallel(files, temp_folder):
    """並行處理多個檔案"""
    # 建立任務列表
    tasks = [
        process_single_file(file, temp_folder)
        for file in files
    ]
    
    # 並行執行所有任務
    results = await asyncio.gather(*tasks)
    
    # 整理結果
    web_research_results = []
    sources_gathered = []
    
    for result in results:
        web_research_results.append(result['content_str'])
        sources_gathered.append(result['file_name'])
    
    return web_research_results, sources_gathered


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
