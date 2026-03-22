"""
このファイルは、画面表示以外の様々な関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
import streamlit as st
import logging
import sys
import unicodedata
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader, WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import HumanMessage, AIMessage, Document as LCDocument
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from typing import List
from sudachipy import tokenizer, dictionary
from langchain_community.agent_toolkits import SlackToolkit
from langchain.agents import AgentType, initialize_agent
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from docx import Document
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain import LLMChain
from langchain import SerpAPIWrapper
import datetime
import constants as ct
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import requests
#from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time

import time
import requests
import feedparser
from urllib.parse import quote_plus


############################################################
# 設定関連
############################################################
load_dotenv()


############################################################
# 関数定義
############################################################

def build_error_message(message):
    """
    エラーメッセージと管理者問い合わせテンプレートの連結

    Args:
        message: 画面上に表示するエラーメッセージ

    Returns:
        エラーメッセージと管理者問い合わせテンプレートの連結テキスト
    """
    return "\n".join([message, ct.COMMON_ERROR_MESSAGE])


def _build_google_news_rss_url(query: str, hl: str = "ja", gl: str = "JP", ceid: str = "JP:ja") -> str:
    # Google News RSS (search)
    # 例: https://news.google.com/rss/search?q=政治&hl=ja&gl=JP&ceid=JP:ja
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"

def _fetch_feed_entries(rss_url: str, timeout: int = 15):
    response = requests.get(rss_url, timeout=timeout)
    feed = feedparser.parse(response.content)
    entries = []
    for e in feed.entries:
        entries.append({
            "title": e.get("title", ""),
            "link": e.get("link", ""),
            "published": e.get("published", ""),
            "source": (e.get("source") or {}).get("title", ""),
            "summary": e.get("summary", ""),  # RSS側の短い要約
        })
    return entries

def _collect_news_by_topic(topic: str, query: str, max_articles_per_topic: int = 10, sleep_sec: float = 0.8):
    results = {}

    rss_url = _build_google_news_rss_url(query)
    entries = _fetch_feed_entries(rss_url)

    topic_items = []
    for e in entries[:max_articles_per_topic]:

        topic_items.append({
            "topic": topic,
            "title": e["title"],
            "published": e["published"],
            "source": e["source"],
            "url": e["link"],
            "rss_summary": e["summary"],
        })

        time.sleep(sleep_sec)  # アクセス間隔

    results[topic] = topic_items

    return results

def _make_title_corpus(news_items: List[dict]) -> str:
    title_corpus_tmp = []
    for topic, items in news_items.items():
        for i, x in enumerate(items, 1):
            title_corpus_tmp.append(x['title'])

    title_corpus_tmp = "\n".join(title_corpus_tmp)
        
    return title_corpus_tmp

def _make_title_list(news_items: List[dict]) -> list:
    title_list_tmp = []
    for topic, items in news_items.items():
        for i, x in enumerate(items, 1):
            title_list_tmp.append(x['title'])

    return title_list_tmp

def _make_url_list(news_items: List[dict]) -> str:
    url_list_tmp = []
    for topic, items in news_items.items():
        for i, x in enumerate(items, 1):
            url_list_tmp.append(x['url'])

    return url_list_tmp

def _make_source_list(news_items: List[dict]) -> str:
    source_list_tmp = []
    for topic, items in news_items.items():
        for i, x in enumerate(items, 1):
            source_list_tmp.append(x['source'])

    return source_list_tmp

def _summarize_content(content: str) -> str:
    """
    抽出したニュース内容をLLMで要約する
    """
    if not content or len(content.strip()) == 0:
        return "内容がありません"

    if "llm" not in st.session_state or st.session_state.llm is None:
        # LLMが未設定の場合は簡易要約
        sentences = content.split("\n")
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        return "\n".join(summary_sentences).strip()

    summary_prompt = PromptTemplate(
        input_variables=["content"],
        template=ct.SYSTEM_PROMPT_SUMMARIZE_ARTICLE,
    )

    try:
        chain = LLMChain(llm=st.session_state.llm, prompt=summary_prompt)
        summary = chain.run(content=content)
        return summary.strip()
    except Exception as e:
        # 要約失敗時は最初の部分を返す
        return content[:300] + "..."
    
def build_topic_llm_chain(topic_key: str, query: str, max_articles_per_topic: int = 10):
    # 1. RSS取得
    news_items = _collect_news_by_topic(
        topic=topic_key,
        query=query,
        max_articles_per_topic=max_articles_per_topic,
    )

    # 2. タイトル一覧文字列
    title_corpus = _make_title_corpus(news_items)
    title_list = _make_title_list(news_items)
    url_list = _make_url_list(news_items)
    source_list = _make_source_list(news_items)

    # UI表示用に topic_key ごとのURL・ソース一覧を保存
    if "topic_sources" not in st.session_state:
        st.session_state.topic_sources = {}
    st.session_state.topic_sources[topic_key] = {
        "title_list": title_list if isinstance(title_list, list) else [],
        "url_list": url_list if isinstance(url_list, list) else [],
        "source_list": source_list if isinstance(source_list, list) else [],
    }

    # 3. タイトル一覧を要約
    topic_summary = _summarize_content(title_corpus)

    # 4. 要約とタイトル群を文脈に持つLLMChainを作成
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=ct.SYSTEM_PROMPT_RAG_ANSWER.format(
                    topic_key=topic_key,
                    topic_summary=topic_summary,
                    title_corpus=title_corpus,
                    source_list="\n".join(source_list) if isinstance(source_list, list) else str(source_list),
                    url_list="\n".join(url_list) if isinstance(url_list, list) else str(url_list),
                ),
            )

    return LLMChain(llm=st.session_state.llm, prompt=prompt)

def _generate_web_search_query(user_input: str) -> str:
    prompt = PromptTemplate(
        input_variables=["input_text"],
        template=ct.SYSTEM_PROMPT_WEB_QUERY_GEN + "\n\n質問:\n{input_text}\n"
    )
    chain = LLMChain(llm=st.session_state.llm, prompt=prompt)
    q = chain.run(input_text=user_input).strip()
    return q.replace("\n", " ").strip()

def build_dynamic_web_llm_chain(user_prompt: str, max_articles_per_topic: int = 8):
    """
    ユーザープロンプトから検索クエリを生成し、
    取得ニュースを文脈として LLMChain を組み立てて返す。
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # 1) プロンプトから検索クエリを生成
    search_query = _generate_web_search_query(user_prompt)
    if not search_query:
        search_query = user_prompt.strip()

    # 2) 検索クエリでニュース取得（topic名は動的用に固定）
    news_items = _collect_news_by_topic(
        topic="dynamic_web",
        query=search_query,
        max_articles_per_topic=max_articles_per_topic,
    )

    # 3) タイトル・URL・ソースを整形
    title_corpus = _make_title_corpus(news_items)
    url_list = _make_url_list(news_items)
    source_list = _make_source_list(news_items)

    # 4) タイトル群を要約
    summary_input = title_corpus if title_corpus.strip() else search_query
    topic_summary = _summarize_content(summary_input)

    # URL/ソースは文字列化してプロンプトに埋め込む
    url_text = "\n".join(url_list) if isinstance(url_list, list) else str(url_list)
    source_text = "\n".join(source_list) if isinstance(source_list, list) else str(source_list)

    # 5) LLMChain生成
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=ct.SYSTEM_PROMPT_WEB_RAG_ANSWER.format(
                    original_prompt=user_prompt,
                    search_query=search_query,
                    topic_summary=topic_summary,
                    title_corpus=title_corpus,
                    source_text=source_text,
                    url_text=url_text,
                ),
            )

    chain = LLMChain(llm=st.session_state.llm, prompt=prompt)

    # デバッグ・UI表示に使えるメタ情報も返す
    meta = {
        "search_query": search_query,
        "title_count": len(title_corpus.splitlines()) if title_corpus else 0,
        "url_count": len(url_list) if isinstance(url_list, list) else 0,
    }
    logger.info({"build_dynamic_web_llm_chain": meta})

    return chain, meta


def run_web_search_tool(user_input: str) -> str:
    """
    Web検索Tool用の薄いラッパー。
    ユーザー入力から検索クエリを整形してから検索する。
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    search_query = user_input.strip()
    if "llm" in st.session_state and st.session_state.llm is not None:
        try:
            generated_query = _generate_web_search_query(user_input)
            if generated_query:
                search_query = generated_query
        except Exception as e:
            logger.warning(f"Web検索クエリ生成に失敗したため元の入力を使用します: {e}")

    search_runner = st.session_state.get("search")
    if search_runner is None:
        search_runner = SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"})
        st.session_state.search = search_runner

    result = search_runner.run(search_query)
    return f"検索クエリ: {search_query}\n\n検索結果:\n{result}"


def get_or_create_topic_chain(topic_key: str, query: str):
    if "topic_llm_chains" not in st.session_state:
        st.session_state.topic_llm_chains = {}

    if topic_key not in st.session_state.topic_llm_chains:
        st.session_state.topic_llm_chains[topic_key] = build_topic_llm_chain(topic_key, query)

    return st.session_state.topic_llm_chains[topic_key]

def run_category_doc_chain(topic_key: str, query: str, user_input: str):
    chain = get_or_create_topic_chain(topic_key, query)
    result = chain.invoke({"user_input": user_input})

    # LLMChainの戻りは text キーが一般的
    answer = result.get("text", "") if isinstance(result, dict) else str(result)

    # 直近回答の参照元情報を last_sources に転記（display_llm_response で使用）
    st.session_state.last_sources = (
        st.session_state.get("topic_sources", {}).get(topic_key, {})
    )

    # 既存の会話履歴運用に合わせる
    if "chat_history" in st.session_state:
        st.session_state.chat_history.extend([
            HumanMessage(content=user_input),
            AIMessage(content=answer),
        ])

    return answer

"""
TODO: 後で消す
"""
def run_politics_doc_chain(param):
    """
    政治に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 政治に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.politics_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_economics_doc_chain(param):
    """
    経済に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 経済に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.economy_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_international_doc_chain(param):
    """
    国際に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 国際に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.international_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_technology_doc_chain(param):
    """
    テクノロジーに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # テクノロジーに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.technology_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_business_doc_chain(param):
    """
    ビジネスに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # ビジネスに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.business_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_weather_doc_chain(param):
    """
    天気に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 天気に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.weather_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_weater_doc_chain(param):
    """
    天気に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 天気に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.weather_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_health_doc_chain(param):
    """
    健康に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 健康に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.health_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_fashion_doc_chain(param):
    """
    ファッションに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # ファッションに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.fashion_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_beauty_doc_chain(param):
    """
    美容に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 美容に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.beauty_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_gourmet_doc_chain(param):
    """
    グルメに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # グルメに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.gourmet_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_sightseeing_doc_chain(param):
    """
    観光に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 観光に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.sightseeing_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_anime_doc_chain(param):
    """
    アニメに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # アニメに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.anime_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_manga_doc_chain(param):
    """
    漫画に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 漫画に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.manga_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_movie_doc_chain(param):
    """
    映画に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 映画に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.movie_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_game_doc_chain(param):
    """
    ゲームに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # ゲームに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.game_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_music_doc_chain(param):
    """
    音楽に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 音楽に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.music_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_entertainment_doc_chain(param):
    """
    エンタメに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # エンタメに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.entertainment_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_sports_doc_chain(param):
    """
    スポーツに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # スポーツに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.sports_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_outdoors_doc_chain(param):
    """
    アウトドアに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # アウトドアに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.outdoors_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_education_doc_chain(param):
    """
    教育に関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 教育に関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.education_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_career_doc_chain(param):
    """
    キャリアに関するデータ参照に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # キャリアに関するデータ参照に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.career_doc_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})
    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

def run_competitors_info_tool(param):
    # 比較観点を固定して検索のブレを減らす
    query = f"{ct.SERVICE_DESCRIPTION} 競合 比較 強み 弱み 価格 機能 {param}"
    q = (query or "").strip().replace('"', "").replace("(", "").replace(")", "")
    if not q:
        return "検索クエリが空のため、Web検索を実行できませんでした。"
    try:
        return SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"}).run(q)
    except ValueError as e:
        if "Google hasn't returned any results" in str(e):
            return "Web検索結果が見つかりませんでした。キーワードを変えて再度お試しください。"
        return f"Web検索でエラーが発生しました: {e}"

def run_plan_customer_marketing_strategy_tool_old(param):
    # 修正前の関数

    query = """
        あなたはマーケティングの専門家です。
        マーケティング戦略や顧客獲得に関する実践的なアドバイスを提供します。
        会社のサービスを広めていくための方法を教えてください。
        対象サービス： 
        """ + ct.SERVICE_DESCRIPTION

    q = (query or "").strip().replace('"', "").replace("(", "").replace(")", "")

    if not q:
        return "検索クエリが空のため、Web検索を実行できませんでした。"
    try:
        return SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"}).run(q)
    except ValueError as e:
        if "Google hasn't returned any results" in str(e):
            return "Web検索結果が見つかりませんでした。キーワードを変えて再度お試しください。"
        return f"Web検索でエラーが発生しました: {e}"
    

def _run_serpapi_safe(query: str) -> str:
    """SerpAPI実行を共通化し、エラー時に扱いやすい文字列を返す。"""
    q = (query or "").strip()
    if not q:
        return "Web検索クエリが空です。"

    # セッションに検索クライアントがなければ初期化
    if "search" not in st.session_state:
        st.session_state.search = SerpAPIWrapper(
            params={"engine": "google", "hl": "ja", "gl": "jp"}
        )

    try:
        return st.session_state.search.run(q)
    except ValueError as e:
        if "Google hasn't returned any results" in str(e):
            return "Web検索結果が見つかりませんでした。"
        return f"Web検索でエラーが発生しました: {e}"
    except Exception as e:
        return f"Web検索で予期しないエラーが発生しました: {e}"
    
def run_plan_customer_marketing_strategy_tool(param: str) -> str:
    """
    2段構成:
    1) Web検索で外部情報を収集
    2) LLMで「3戦略 + 根拠 + KPI」に構造化して提案
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # typo互換: SERVICE_DESCRIPTION がなければ既存名を使う
    service_description = getattr(
        ct, "SERVICE_DESCRIPTION", getattr(ct, "SERVICE_DISCRIPTION", "")
    )
    user_request = (param or "").strip()

    # 1) Web検索
    search_query = (
        f"{service_description} マーケティング戦略 顧客獲得 事例 KPI "
        f"ターゲティング 施策 成功要因 {user_request}"
    )
    web_context = _run_serpapi_safe(search_query)

    # 検索結果が得られなくても、最低限の提案は返す
    if "エラー" in web_context or "見つかりませんでした" in web_context:
        logger.info({"tool": "plan_customer_marketing_strategy_tool", "web_context": web_context})

    # 2) LLMで戦略化
    prompt = PromptTemplate(
        input_variables=["service_description", "user_request", "web_context"],
        template=ct.SYSTEM_PROMPT_MARKETING_STRATEGY,
    )
    prompt_text = prompt.format(
        service_description=service_description,
        user_request=user_request,
        web_context=web_context,
    )

    result = st.session_state.llm.invoke(prompt_text)
    answer = result.content if hasattr(result, "content") else str(result)

    logger.info({
        "tool": "plan_customer_marketing_strategy_tool",
        "query": user_request,
        "search_query": search_query
    })

    return answer

def run_all_doc_chain(param):
    """
    全データ横断検索に特化したTool設定用の関数

    Args:
        param: ユーザー入力値

    Returns:
        LLMからの回答
    """
    # 全データ横断検索に特化したChainを実行してLLMからの回答取得
    ai_msg = st.session_state.rag_chain.invoke({"input": param, "chat_history": st.session_state.chat_history})

    # 会話履歴への追加
    st.session_state.chat_history.extend([HumanMessage(content=param), AIMessage(content=ai_msg["answer"])])

    return ai_msg["answer"]

"""
TODO: 後で消す　終わり
"""

def delete_old_conversation_log(result):
    """
    古い会話履歴の削除

    Args:
        result: LLMからの回答
    """
    # LLMからの回答テキストのトークン数を取得
    response_tokens = len(st.session_state.enc.encode(result))
    # 過去の会話履歴の合計トークン数に加算
    st.session_state.total_tokens += response_tokens

    # トークン数が上限値を下回るまで、順に古い会話履歴を削除
    while st.session_state.total_tokens > ct.MAX_ALLOWED_TOKENS:
        # 最も古い会話履歴を削除
        removed_message = st.session_state.chat_history.pop(1)
        # 最も古い会話履歴のトークン数を取得
        removed_tokens = len(st.session_state.enc.encode(removed_message.content))
        # 過去の会話履歴の合計トークン数から、最も古い会話履歴のトークン数を引く
        st.session_state.total_tokens -= removed_tokens


def execute_agent_or_chain(chat_message):
    """
    AIエージェントもしくはAIエージェントなしのRAGのChainを実行

    Args:
        chat_message: ユーザーメッセージ
    
    Returns:
        LLMからの回答
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # AIエージェント機能を利用する場合
    if st.session_state.agent_mode == ct.AI_AGENT_MODE_ON:
        # LLMによる回答をストリーミング出力するためのオブジェクトを用意
        st_callback = StreamlitCallbackHandler(st.container())
        # Agent Executorの実行（AIエージェント機能を使う場合は、Toolとして設定した関数内で会話履歴への追加処理を実施）
        result = st.session_state.agent_executor.invoke({"input": chat_message}, {"callbacks": [st_callback]})
        response = result["output"]
    # AIエージェントを利用しない場合
    else:
        # RAGのChainを実行
        result = st.session_state.rag_chain.invoke({"input": chat_message, "chat_history": st.session_state.chat_history})
        # 会話履歴への追加
        st.session_state.chat_history.extend([HumanMessage(content=chat_message), AIMessage(content=result["answer"])])
        response = result["answer"]

    # LLMから参照先のデータを基にした回答が行われた場合のみ、フィードバックボタンを表示
    if response != ct.NO_DOC_MATCH_MESSAGE:
        st.session_state.answer_flg = True
    
    return response


def notice_slack(chat_message):
    """
    問い合わせ内容のSlackへの通知

    Args:
        chat_message: ユーザーメッセージ

    Returns:
        問い合わせサンクスメッセージ
    """

    logger = logging.getLogger(ct.LOGGER_NAME)  # 追加

    # Slack通知用のAgent Executorを作成
    toolkit = SlackToolkit()
    tools = toolkit.get_tools()
    agent_executor = initialize_agent(
        llm=st.session_state.llm,
        tools=tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
    )

    # 担当者割り振りに使う用の「従業員情報」と「問い合わせ対応履歴」の読み込み
    loader = CSVLoader(ct.EMPLOYEE_FILE_PATH, encoding=ct.CSV_ENCODING)
    docs = loader.load()
    loader = CSVLoader(ct.INQUIRY_HISTORY_FILE_PATH, encoding=ct.CSV_ENCODING)
    docs_history = loader.load()

    # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
    for doc in docs:
        doc.page_content = adjust_string(doc.page_content)
        for key in doc.metadata:
            doc.metadata[key] = adjust_string(doc.metadata[key])
    for doc in docs_history:
        doc.page_content = adjust_string(doc.page_content)
        for key in doc.metadata:
            doc.metadata[key] = adjust_string(doc.metadata[key])

    # 問い合わせ内容と関連性が高い従業員情報を取得するために、参照先データを整形
    docs_all = adjust_reference_data(docs, docs_history)
    
    # 形態素解析による日本語の単語分割を行うため、参照先データからテキストのみを抽出
    docs_all_page_contents = []
    for doc in docs_all:
        docs_all_page_contents.append(doc.page_content)

    # Retrieverの作成
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(docs_all, embedding=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": ct.TOP_K})
    bm25_retriever = BM25Retriever.from_texts(
        docs_all_page_contents,
        preprocess_func=preprocess_func,
        k=ct.TOP_K
    )
    retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, retriever],
        weights=ct.RETRIEVER_WEIGHTS
    )

    # 問い合わせ内容と関連性の高い従業員情報を取得
    employees = retriever.invoke(chat_message)
    
    # プロンプトに埋め込むための従業員情報テキストを取得
    context = get_context(employees)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", ct.SYSTEM_PROMPT_EMPLOYEE_SELECTION)
    ])
    # フォーマット文字列を生成
    output_parser = CommaSeparatedListOutputParser()
    format_instruction = output_parser.get_format_instructions()

    # 問い合わせ内容と関連性が高い従業員のID一覧を取得
    messages = prompt_template.format_prompt(context=context, query=chat_message, format_instruction=format_instruction).to_messages()
    employee_id_response = st.session_state.llm(messages)
    try:
        employee_ids = output_parser.parse(employee_id_response.content)
    except ValueError as e:
        logger.warning(
            {
                "notice_slack.parse_error": str(e),
                "raw_employee_id_response": employee_id_response.content
            },
            exc_info=True
        )
        # フォールバック: 担当者なし扱い（または後段で管理者通知）
        employee_ids = []
    except Exception as e:
        logger.error(
            {
                "notice_slack.unexpected_parse_error": str(e),
                "raw_employee_id_response": employee_id_response.content
            },
            exc_info=True
        )
        employee_ids = []

    # 問い合わせ内容と関連性が高い従業員情報を、IDで照合して取得
    target_employees = get_target_employees(employees, employee_ids)
    
    # 問い合わせ内容と関連性が高い従業員情報の中から、SlackIDのみを抽出
    slack_ids = get_slack_ids(target_employees)

    # 追加: 従業員一覧、従業員数、スラックid一覧、チャットメッセージ ログ
    logger.info({"notice_slack.employee_ids": employee_ids})
    logger.info({"notice_slack.target_employees_len": len(target_employees)})
    logger.info({"notice_slack.slack_ids": slack_ids})
    logger.info({"notice_slack.chat_message": chat_message})

    # 追加: 担当者が1人もいない場合のガード
    if not slack_ids:
        admin_prompt = f"""
        Slackの「{ct.SLACK_CHANNEL_NAME}」チャンネルに、次の内容を送信してください。

        【自動通知】担当者未割り当て
        問い合わせ内容: {chat_message}
        理由: 関連度の高い担当者を特定できませんでした。
        対応依頼: 担当者の手動アサインをお願いします。
        """
        # 管理者チャンネルへ固定通知
        admin_invoke_result = agent_executor.invoke({"input": admin_prompt})
        logger.info({"notice_slack.admin_invoke_result": admin_invoke_result})

        # UIには「該当担当者なし」を返す
        return ct.NO_ASSIGNEE_MESSAGE
    
    # 抽出したSlackIDの連結テキストを生成
    slack_id_text = create_slack_id_text(slack_ids)

    # 追加: 選定理由を作成
    selection_reasons = create_selection_reasons(chat_message, target_employees)
    logger.info({"notice_slack.selection_reasons": selection_reasons})
    
    # プロンプトに埋め込むための（問い合わせ内容と関連性が高い）従業員情報テキストを取得
    context = get_context(target_employees)

    # 現在日時を取得
    now_datetime = get_datetime()

    # Slack通知用のプロンプト生成
    prompt = PromptTemplate(
        input_variables=["slack_id_text", "query", "context", "now_datetime", "selection_reasons"],
        template=ct.SYSTEM_PROMPT_NOTICE_SLACK,
    )
    prompt_message = prompt.format(slack_id_text=slack_id_text, query=chat_message, context=context, now_datetime=now_datetime, selection_reasons=selection_reasons)

    # Slack通知の実行
    invoke_result = agent_executor.invoke({"input": prompt_message})

    # 追加: invoke戻り値ログ（大きすぎる場合は必要項目だけに絞る）
    logger.info({"notice_slack.invoke_result": invoke_result})

    return ct.CONTACT_THANKS_MESSAGE


def adjust_reference_data(docs, docs_history):
    """
    Slack通知用の参照先データの整形

    Args:
        docs: 従業員情報ファイルの読み込みデータ
        docs_history: 問い合わせ対応履歴ファイルの読み込みデータ

    Returns:
        従業員情報と問い合わせ対応履歴の結合テキスト
    """

    docs_all = []
    for row in docs:
        # 従業員IDの取得
        row_lines = row.page_content.split("\n")
        row_dict = {item.split(": ")[0]: item.split(": ")[1] for item in row_lines}
        employee_id = row_dict["従業員ID"]

        doc = ""

        # 取得した従業員IDに紐づく問い合わせ対応履歴を取得
        same_employee_inquiries = []
        for row_history in docs_history:
            row_history_lines = row_history.page_content.split("\n")
            row_history_dict = {item.split(": ")[0]: item.split(": ")[1] for item in row_history_lines}
            if row_history_dict["従業員ID"] == employee_id:
                same_employee_inquiries.append(row_history_dict)

        new_doc = Document()

        if same_employee_inquiries:
            # 従業員情報と問い合わせ対応履歴の結合テキストを生成
            doc += "【従業員情報】\n"
            row_data = "\n".join(row_lines)
            doc += row_data + "\n=================================\n"
            doc += "【この従業員の問い合わせ対応履歴】\n"
            for inquiry_dict in same_employee_inquiries:
                for key, value in inquiry_dict.items():
                    doc += f"{key}: {value}\n"
                doc += "---------------\n"
            new_doc.page_content = doc
        else:
            new_doc.page_content = row.page_content
        new_doc.metadata = {}

        docs_all.append(new_doc)
    
    return docs_all



def get_target_employees(employees, employee_ids):
    """
    問い合わせ内容と関連性が高い従業員情報一覧の取得

    Args:
        employees: 問い合わせ内容と関連性が高い従業員情報一覧
        employee_ids: 問い合わせ内容と関連性が「特に」高い従業員のID一覧

    Returns:
        問い合わせ内容と関連性が「特に」高い従業員情報一覧
    """

    target_employees = []
    duplicate_check = []
    target_text = "従業員ID"
    for employee in employees:
        # 従業員IDの取得
        num = employee.page_content.find(target_text)
        employee_id = employee.page_content[num+len(target_text)+2:].split("\n")[0]
        # 問い合わせ内容と関連性が高い従業員情報を、IDで照合して取得（重複除去）
        if employee_id in employee_ids:
            if employee_id in duplicate_check:
                continue
            duplicate_check.append(employee_id)
            target_employees.append(employee)
    
    return target_employees


def get_slack_ids(target_employees):
    """
    SlackIDの一覧を取得

    Args:
        target_employees: 問い合わせ内容と関連性が高い従業員情報一覧

    Returns:
        SlackIDの一覧
    """

    target_text = "SlackID"
    slack_ids = []
    for employee in target_employees:
        num = employee.page_content.find(target_text)
        slack_id = employee.page_content[num+len(target_text)+2:].split("\n")[0]
        slack_ids.append(slack_id)
    
    return slack_ids


def create_slack_id_text(slack_ids):
    """
    SlackIDの一覧を取得

    Args:
        slack_ids: SlackIDの一覧

    Returns:
        SlackIDを「と」で繋いだテキスト
    """
    slack_id_text = ""
    for i, id in enumerate(slack_ids):
        slack_id_text += f"「{id}」"
        # 最後のSlackID以外、連結後に「と」を追加
        if not i == len(slack_ids)-1:
            slack_id_text += "と"
    
    return slack_id_text


def get_context(docs):
    """
    プロンプトに埋め込むための従業員情報テキストの生成
    Args:
        docs: 従業員情報の一覧

    Returns:
        生成した従業員情報テキスト
    """

    context = ""
    for i, doc in enumerate(docs, start=1):
        context += "===========================================================\n"
        context += f"{i}人目の従業員情報\n"
        context += "===========================================================\n"
        context += doc.page_content + "\n\n"

    return context

def create_selection_reasons(chat_message, target_employees):
    """
    選定された従業員ごとの理由テキストをLLMで生成
    """
    if not target_employees:
        return "該当担当者が見つからなかったため、管理者確認が必要です。"

    selected_context = get_context(target_employees)

    prompt = PromptTemplate(
        input_variables=["query", "selected_context"],
        template=ct.SYSTEM_PROMPT_SELECTION_REASON,
    )
    prompt_text = prompt.format(
        query=chat_message,
        selected_context=selected_context,
    )

    result = st.session_state.llm.invoke(prompt_text)
    return result.content if hasattr(result, "content") else str(result)


def get_datetime():
    """
    現在日時を取得

    Returns:
        現在日時
    """

    dt_now = datetime.datetime.now()
    now_datetime = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')

    return now_datetime


def preprocess_func(text):
    """
    形態素解析による日本語の単語分割
    Args:
        text: 単語分割対象のテキスト

    Returns:
        単語分割を実施後のテキスト
    """

    tokenizer_obj = dictionary.Dictionary(dict="full").create()
    mode = tokenizer.Tokenizer.SplitMode.A
    tokens = tokenizer_obj.tokenize(text ,mode)
    words = [token.surface() for token in tokens]
    words = list(set(words))

    return words


def adjust_string(s):
    """
    Windows環境でRAGが正常動作するよう調整
    
    Args:
        s: 調整を行う文字列
    
    Returns:
        調整を行った文字列
    """
    # 調整対象は文字列のみ
    if type(s) is not str:
        return s

    # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
    if sys.platform.startswith("win"):
        s = unicodedata.normalize('NFC', s)
        s = s.encode("cp932", "ignore").decode("cp932")
        return s
    
    # OSがWindows以外の場合はそのまま返す
    return s