import io
import os
from typing import List, Dict, Any

import chromadb
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
router = APIRouter()

def ingest_pdfFile_to_VectorDB(
    pdf_bytes: bytes,
    pdf_name: str,
    document_type: str,
    DTYPE:str,
    collection_name: str = "rag_docs",

):
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMADB_KEY"),
        tenant=os.getenv("CHROMADB_TENANT"),
        database=os.getenv("CHROMADB_DATABASE"),
    )
    collection = client.get_or_create_collection(name=collection_name)


    elements = partition_pdf(
        file=io.BytesIO(pdf_bytes),#type:ignore
        strategy="fast",
    )

    chunks = chunk_by_title(elements)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        text = chunk.text.strip()
        if not text:
            continue

        chunk_id = f"{pdf_name}_{i}"
        ids.append(chunk_id)
        documents.append(text)
        metadatas.append({
            "source_file": pdf_name,
            "document_type": document_type,
            "chunk_index": i,
            "DTYPE":DTYPE
        })
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

def RRS_Retrive_offline(query:str):
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMADB_KEY"),
        tenant=os.getenv("CHROMADB_TENANT"),
        database=os.getenv("CHROMADB_DATABASE"),
    )
    collection = client.get_or_create_collection(name="RAG")
    result = collection.query(query_texts=query,n_results=3)
    return result["documents"]

@router.post("/RRS/retrieve")
async def RSS_Retrive(request:Request):
    _data = await request.json()
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMADB_KEY"),
        tenant=os.getenv("CHROMADB_TENANT"),
        database=os.getenv("CHROMADB_DATABASE"),
    )
    collection = client.get_or_create_collection(name="RAG")
    result = collection.query(query_texts=_data["query"],n_results=3)
    _send = {"retrieved_context":result["documents"]}
    return JSONResponse(_send,200)