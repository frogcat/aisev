import os
from pypdf import PdfReader
import io
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF files
    
    Args:
        file_path: PDF file path
        
    Returns:
        str: Extracted text
    """
    try:
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        return text
    except Exception as e:
        print(f"PDFテキスト抽出エラー: {e}")
        return f"テキスト抽出に失敗しました: {str(e)}"


async def summarize_text_with_llm(text: str, llm_client, max_chunk_size=8000) -> str:
    """
    Summarize text using LLM
    
    Args:
        text: Text to summarize
        llm_client: LLM client instance
        
    Returns:
        str: Summarized text
    """
    # If the text is too long, it needs to be split and processed
    # max_chunk_size is an estimate of the number of characters, not the number of tokens
    
    if len(text) <= max_chunk_size:
        system_prompt = "あなたは文書要約の専門家です。提供された文書を簡潔に要約してください。"
        user_prompt = f"以下の文書を要約してください。要点を漏らさず簡潔にまとめてください。\n\n{text}"
        return await llm_client.generate(system_prompt, user_prompt)
    else:
        # Split a long document into multiple chunks
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        summaries = []
        
        for i, chunk in enumerate(chunks):
            system_prompt = "あなたは文書要約の専門家です。提供された文書を簡潔に要約してください。"
            user_prompt = f"以下の文書（パート{i+1}/{len(chunks)}）を要約してください。要点を漏らさず簡潔にまとめてください。\n\n{chunk}"
            summary = await llm_client.generate(system_prompt, user_prompt)
            summaries.append(summary)
        
        # Integrate multiple summarized text
        if len(summaries) > 1:
            combined_summaries = "\n\n".join([f"パート{i+1}の要約:\n{s}" for i, s in enumerate(summaries)])
            system_prompt = "あなたは文書要約の専門家です。複数の要約を統合して、全体を代表する1つの要約を作成してください。"
            user_prompt = f"以下の複数の要約を統合して、元の文書全体を代表する1つの包括的な要約を作成してください。文字数は{max_chunk_size}文字以内とし、可能な限り要約前の文の内容を維持する方針としてください。\n\n{combined_summaries}"
            final_summary = await llm_client.generate(system_prompt, user_prompt)
            return final_summary
        else:
            return summaries[0]

