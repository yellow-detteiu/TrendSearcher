"""
このファイルは、最初の画面読み込み時にのみ実行される初期化処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st
import tiktoken
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain import SerpAPIWrapper
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
import utils
import constants as ct



############################################################
# 設定関連
############################################################
load_dotenv()


############################################################
# 関数定義
############################################################

def initialize():
    """
    画面読み込み時に実行する初期化処理
    """
    # 初期化データの用意
    initialize_session_state()
    # ログ出力用にセッションIDを生成
    initialize_session_id()
    # ログ出力の設定
    initialize_logger()
    # Agent Executorを作成
    initialize_agent_executor()


def initialize_session_state():
    """
    初期化データの用意
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
        # 会話履歴の合計トークン数を加算する用の変数
        st.session_state.total_tokens = 0

        # フィードバックボタンで「はい」を押下した後にThanksメッセージを表示するためのフラグ
        st.session_state.feedback_yes_flg = False
        # フィードバックボタンで「いいえ」を押下した後に入力エリアを表示するためのフラグ
        st.session_state.feedback_no_flg = False
        # LLMによる回答生成後、フィードバックボタンを表示するためのフラグ
        st.session_state.answer_flg = False
        # フィードバックボタンで「いいえ」を押下後、フィードバックを送信するための入力エリアからの入力を受け付ける変数
        st.session_state.dissatisfied_reason = ""
        # フィードバック送信後にThanksメッセージを表示するためのフラグ
        st.session_state.feedback_no_reason_send_flg = False


def initialize_session_id():
    """
    セッションIDの作成
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid4().hex


def initialize_logger():
    """
    ログ出力の設定
    """
    os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)

    logger = logging.getLogger(ct.LOGGER_NAME)

    if logger.hasHandlers():
        return

    log_handler = TimedRotatingFileHandler(
        os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
        when="D",
        encoding="utf8"
    )
    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s line %(lineno)s, in %(funcName)s, session_id={st.session_state.session_id}: %(message)s"
    )
    log_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)


def initialize_agent_executor():
    """
    画面読み込み時にAgent Executor（AIエージェント機能の実行を担当するオブジェクト）を作成
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # すでにAgent Executorが作成済みの場合、後続の処理を中断
    if "agent_executor" in st.session_state:
        return
    
    # 消費トークン数カウント用のオブジェクトを用意
    st.session_state.enc = tiktoken.get_encoding(ct.ENCODING_KIND)
    
    st.session_state.llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE, streaming=True)

    # 各Tool用のChainを作成
    st.session_state.politics_doc_chain = utils.create_rag_chain_from_news_urls(ct.POLITICS_URL_LIST)
    st.session_state.economics_doc_chain = utils.create_rag_chain_from_news_urls(ct.ECONOMICS_URL_LIST)
    st.session_state.international_doc_chain = utils.create_rag_chain_from_news_urls(ct.INTERNATIONAL_URL_LIST)
    st.session_state.technology_doc_chain = utils.create_rag_chain_from_news_urls(ct.TECHNOLOGY_URL_LIST)
    st.session_state.business_doc_chain = utils.create_rag_chain_from_news_urls(ct.BUSINESS_URL_LIST)
    st.session_state.weather_doc_chain = utils.create_rag_chain_from_news_urls(ct.WEATHER_URL_LIST)
    st.session_state.health_doc_chain = utils.create_rag_chain_from_news_urls(ct.HEALTH_URL_LIST)
    st.session_state.fashion_doc_chain = utils.create_rag_chain_from_news_urls(ct.FASHION_URL_LIST)
    st.session_state.beauty_doc_chain = utils.create_rag_chain_from_news_urls(ct.BEAUTY_URL_LIST)
    st.session_state.grourmet_doc_chain = utils.create_rag_chain_from_news_urls(ct.GOURMET_URL_LIST)
    st.session_state.sightseeing_doc_chain = utils.create_rag_chain_from_news_urls(ct.SIGHTSEEING_URL_LIST)
    st.session_state.anime_doc_chain = utils.create_rag_chain_from_news_urls(ct.ANIME_URL_LIST)
    st.session_state.manga_doc_chain = utils.create_rag_chain_from_news_urls(ct.MANGA_URL_LIST)
    st.session_state.movie_doc_chain = utils.create_rag_chain_from_news_urls(ct.MOVIE_URL_LIST)
    st.session_state.game_doc_chain = utils.create_rag_chain_from_news_urls(ct.GAME_URL_LIST)
    st.session_state.music_doc_chain = utils.create_rag_chain_from_news_urls(ct.MUSIC_URL_LIST)
    st.session_state.entertainment_doc_chain = utils.create_rag_chain_from_news_urls(ct.ENTERTAINMENT_URL_LIST)
    st.session_state.sports_doc_chain = utils.create_rag_chain_from_news_urls(ct.SPORTS_URL_LIST)
    st.session_state.outdoor_doc_chain = utils.create_rag_chain_from_news_urls(ct.OUTDOOR_URL_LIST)
    st.session_state.education_doc_chain = utils.create_rag_chain_from_news_urls(ct.EDUCATION_URL_LIST)
    st.session_state.career_doc_chain = utils.create_rag_chain_from_news_urls(ct.CAREER_URL_LIST)


    # Web検索用のToolを設定するためのオブジェクトを用意
    #search = SerpAPIWrapper()
    search = SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"}) # エラー予防のため、日本語でGoogle検索を行うためのパラメータを追加

    # エラー防止用
    if "search" not in st.session_state:
        st.session_state.search = SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"})

    # Agent Executorに渡すTool一覧を用意
    tools = [
        # 政治に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_POLITICS_INFO_TOOL_NAME,
            func=utils.run_politics_doc_chain,
            description=ct.SEARCH_POLITICS_INFO_TOOL_DESCRIPTION
        ),
        # 経済に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_ECONOMY_INFO_TOOL_NAME,
            func=utils.run_economy_doc_chain,
            description=ct.SEARCH_ECONOMY_INFO_TOOL_DESCRIPTION
        ),
        # 国際に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_INTERNATIONAL_INFO_TOOL_NAME,
            func=utils.run_international_doc_chain,
            description=ct.SEARCH_INTERNATIONAL_INFO_TOOL_DESCRIPTION
        ),
        # テクノロジーに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_TECHNOLOGY_INFO_TOOL_NAME,
            func=utils.run_technology_doc_chain,
            description=ct.SEARCH_TECHNOLOGY_INFO_TOOL_DESCRIPTION
        ),
        # ビジネスに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_BUSINESS_INFO_TOOL_NAME,
            func=utils.run_business_doc_chain,
            description=ct.SEARCH_BUSINESS_INFO_TOOL_DESCRIPTION
        ),
        # 天気に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_WEATHER_INFO_TOOL_NAME,
            func=utils.run_weather_doc_chain,
            description=ct.SEARCH_WEATHER_INFO_TOOL_DESCRIPTION
        ),
        # 健康に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_HEALTH_INFO_TOOL_NAME,
            func=utils.run_health_doc_chain,
            description=ct.SEARCH_HEALTH_INFO_TOOL_DESCRIPTION
        ),
        # ファッションに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_FASHION_INFO_TOOL_NAME,
            func=utils.run_fashion_doc_chain,
            description=ct.SEARCH_FASHION_INFO_TOOL_DESCRIPTION
        ),
        # 美容に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_BEAUTY_INFO_TOOL_NAME,
            func=utils.run_beauty_doc_chain,
            description=ct.SEARCH_BEAUTY_INFO_TOOL_DESCRIPTION
        ),
        # グルメに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_GOURMET_INFO_TOOL_NAME,
            func=utils.run_gourmet_doc_chain,
            description=ct.SEARCH_GOURMET_INFO_TOOL_DESCRIPTION
        ),
        # 観光に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_SIGHTSEEING_INFO_TOOL_NAME,
            func=utils.run_sightseeing_doc_chain,
            description=ct.SEARCH_SIGHTSEEING_INFO_TOOL_DESCRIPTION
        ),
        # アニメに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_ANIME_INFO_TOOL_NAME,
            func=utils.run_anime_doc_chain,
            description=ct.SEARCH_ANIME_INFO_TOOL_DESCRIPTION
        ),
        # 漫画に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_MANGA_INFO_TOOL_NAME,
            func=utils.run_manga_doc_chain,
            description=ct.SEARCH_MANGA_INFO_TOOL_DESCRIPTION
        ),
        # 映画に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_MOVIE_INFO_TOOL_NAME,
            func=utils.run_movie_doc_chain,
            description=ct.SEARCH_MOVIE_INFO_TOOL_DESCRIPTION
        ),
        # ゲームに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_GAME_INFO_TOOL_NAME,
            func=utils.run_game_doc_chain,
            description=ct.SEARCH_GAME_INFO_TOOL_DESCRIPTION
        ),
        # 音楽に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_MUSIC_INFO_TOOL_NAME,
            func=utils.run_music_doc_chain,
            description=ct.SEARCH_MUSIC_INFO_TOOL_DESCRIPTION
        ),
        # 芸能・エンタメに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_ENTERTAINMENT_INFO_TOOL_NAME,
            func=utils.run_entertainment_doc_chain,
            description=ct.SEARCH_ENTERTAINMENT_INFO_TOOL_DESCRIPTION
        ),
        # スポーツに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_SPORTS_INFO_TOOL_NAME,
            func=utils.run_sports_doc_chain,
            description=ct.SEARCH_SPORTS_INFO_TOOL_DESCRIPTION
        ),
        # アウトドアに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_OUTDOOR_INFO_TOOL_NAME,
            func=utils.run_outdoor_doc_chain,
            description=ct.SEARCH_OUTDOOR_INFO_TOOL_DESCRIPTION
        ),
        # 教育に関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_EDUCATION_INFO_TOOL_NAME,
            func=utils.run_education_doc_chain,
            description=ct.SEARCH_EDUCATION_INFO_TOOL_DESCRIPTION
        ),
        # キャリアに関するデータ検索用のTool
        Tool(
            name=ct.SEARCH_CAREER_INFO_TOOL_NAME,
            func=utils.run_career_doc_chain,
            description=ct.SEARCH_CAREER_INFO_TOOL_DESCRIPTION
        ),
        # Web検索用のTool
        Tool(
            name = ct.SEARCH_WEB_INFO_TOOL_NAME,
            func=search.run,
            description=ct.SEARCH_WEB_INFO_TOOL_DESCRIPTION
        ),
    ]

    # Agent Executorの作成
    st.session_state.agent_executor = initialize_agent(
        llm=st.session_state.llm,
        tools=tools,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        max_iterations=ct.AI_AGENT_MAX_ITERATIONS,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )