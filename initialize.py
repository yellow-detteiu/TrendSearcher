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
from langchain.schema import SystemMessage
import utils
import constants as ct
from functools import partial

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

        st.session_state.youtube_cache = {}
        st.session_state.youtube_disabled_reason = ""

    if "youtube_disabled_reason" not in st.session_state:
        st.session_state.youtube_disabled_reason = ""  # 空文字列は有効状態


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


    # Web検索用のToolを設定するためのオブジェクトを用意
    #search = SerpAPIWrapper()
    search = SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"}) # エラー予防のため、日本語でGoogle検索を行うためのパラメータを追加

    if "news_chain_cache" not in st.session_state:
        st.session_state.news_chain_cache = {}

    if "youtube_cache" not in st.session_state:
        st.session_state.youtube_cache = {}

    if "youtube_disabled_reason" not in st.session_state:
        st.session_state.youtube_disabled_reason = ""

    # エラー防止用
    if "search" not in st.session_state:
        st.session_state.search = SerpAPIWrapper(params={"engine": "google", "hl": "ja", "gl": "jp"})

    # Agent Executorに渡すTool一覧を用意
    tools = []

    # [constants.py](http://_vscodecontentref_/9) の TOPIC_TOOL_CONFIGS を使って自動生成
    for cfg in ct.TOPIC_TOOL_CONFIGS:
        tools.append(
            Tool(
                name=cfg["tool_name"],
                func=partial(
                    utils.run_category_doc_chain,
                    cfg["key"],
                    cfg["query"],
                ),
                description=(
                    f"{cfg['tool_description']}。"
                    "このToolを最優先で使うのは、そのカテゴリの最新動向や最近の話題を聞かれたとき。"
                    "入力にはユーザーの元の質問をそのまま渡す。"
                    f"内部では次の観点で関連ニュースを収集する: {cfg['query']}。"
                    "質問が広くてもカテゴリが合っていれば search_web_tool より先にこのToolを使う。"
                ),
            )
        )

    # Web検索Toolは従来どおり追加
    tools.append(
        Tool(
            name=ct.SEARCH_WEB_INFO_TOOL_NAME,
            func=utils.run_web_search_tool,
            description=(
                f"{ct.SEARCH_WEB_INFO_TOOL_DESCRIPTION}。"
                "どのカテゴリToolにも当てはまらない質問、またはカテゴリToolの結果を補足したい場合のみ使う。"
                "入力にはユーザーの元の質問をそのまま渡す。"
            ),
        )
    )

    # Agent Executorの作成
    # OPENAI_FUNCTIONS: OpenAI APIのネイティブなfunction calling機能を使用するため、
    # ZERO_SHOT_REACT_DESCRIPTIONで発生するテキストパースエラー（ツール名に引数が混入するなど）を防げる
    st.session_state.agent_executor = initialize_agent(
        llm=st.session_state.llm,
        tools=tools,
        agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs={
            "system_message": SystemMessage(content=ct.AGENT_TOOL_SELECTION_PROMPT),
        },
        max_iterations=ct.AI_AGENT_MAX_ITERATIONS,
        early_stopping_method="generate",
        handle_parsing_errors=True,
        verbose=True,
    )