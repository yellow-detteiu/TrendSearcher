"""
このファイルは、固定の文字列や数値などのデータを変数として一括管理するファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader


############################################################
# 共通変数の定義
############################################################

# ==========================================
# 画面表示系
# ==========================================
APP_NAME = "最新情報・トレンドまとめアプリ"
CHAT_INPUT_HELPER_TEXT = "こちらからメッセージを送信してください。"
APP_BOOT_MESSAGE = "アプリが起動されました。"
USER_ICON_FILE_PATH = "./images/user_icon.jpg"
AI_ICON_FILE_PATH = "./images/ai_icon.jpg"
WARNING_ICON = ":material/warning:"
ERROR_ICON = ":material/error:"
SPINNER_TEXT = "回答生成中..."
SPINNER_CONTACT_TEXT = "問い合わせ内容を弊社担当者に送信中です。画面を操作せず、このままお待ちください。"
CONTACT_THANKS_MESSAGE = """
    このたびはお問い合わせいただき、誠にありがとうございます。
    担当者が内容を確認し、3営業日以内にご連絡いたします。
    ただし問い合わせ内容によっては、ご連絡いたしかねる場合がございます。
    もしお急ぎの場合は、お電話にてご連絡をお願いいたします。
"""


# ==========================================
# ユーザーフィードバック関連
# ==========================================
FEEDBACK_YES = "はい"
FEEDBACK_NO = "いいえ"

SATISFIED = "回答に満足した"
DISSATISFIED = "回答に満足しなかった"

FEEDBACK_REQUIRE_MESSAGE = "この回答はお役に立ちましたか？フィードバックをいただくことで、生成AIの回答の質が向上します。"
FEEDBACK_BUTTON_LABEL = "送信"
FEEDBACK_YES_MESSAGE = "ご満足いただけて良かったです！他にもご質問があれば、お気軽にお尋ねください！"
FEEDBACK_NO_MESSAGE = "ご期待に添えず申し訳ございません。今後の改善のために、差し支えない範囲でご満足いただけなかった理由を教えていただけますと幸いです。"
FEEDBACK_THANKS_MESSAGE = "ご回答いただき誠にありがとうございます。"


# ==========================================
# ログ出力系
# ==========================================
LOG_DIR_PATH = "./logs"
LOGGER_NAME = "ApplicationLog"
LOG_FILE = "application.log"


# ==========================================
# LLM設定系
# ==========================================
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5
RETRIEVER_WEIGHTS = [0.5, 0.5]


# ==========================================
# トークン関連
# ==========================================
MAX_ALLOWED_TOKENS = 1000
ENCODING_KIND = "cl100k_base"


# ==========================================
# RAG参照用のデータソース系
# ==========================================
RAG_TOP_FOLDER_PATH = "./data/rag"

SUPPORTED_EXTENSIONS = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": lambda path: TextLoader(path, encoding="utf-8")
}

DB_ALL_PATH = "./.db_all"
DB_COMPANY_PATH = "./.db_company"


# ==========================================
# AIエージェント関連
# ==========================================
AI_AGENT_MAX_ITERATIONS = 5

DB_SERVICE_PATH = "./.db_service"
DB_CUSTOMER_PATH = "./.db_customer"

"""
DB_NAMES = {
    DB_COMPANY_PATH: f"{RAG_TOP_FOLDER_PATH}/company",
    DB_SERVICE_PATH: f"{RAG_TOP_FOLDER_PATH}/service",
    DB_CUSTOMER_PATH: f"{RAG_TOP_FOLDER_PATH}/customer"
}
"""

URL_LIST = {
    POLITICS_URL_LIST: ["https://news.web.nhk/newsweb/genre/politics", "https://www.jiji.com/jc/c?g=pol", "https://www.nikkei.com/news/category/politics/", "https://www.asahi.com/politics/?iref=pc_gnavi", "https://mainichi.jp/seiji/", "https://www.yomiuri.co.jp/politics/", "https://toyokeizai.net/list/genre/economy-and-politics", "https://newspicks.com/theme-news/economic/"],
    ECONOMICS_URL_LIST: ["https://www.bloomberg.com/jp", "https://www.cnbc.com/world/?region=world", "https://www.ft.com/", "https://news.yahoo.co.jp/topics/business", "https://news.web.nhk/newsweb/genre/business", "https://www.jiji.com/jc/c?g=eco", "https://www.nikkei.com/economy/", "https://www.asahi.com/business/?iref=pc_gnavi", "https://mainichi.jp/biz/", "https://www.yomiuri.co.jp/economy/", "https://toyokeizai.net/list/genre/economy-and-politics", "https://newspicks.com/theme-news/market/", ],
    INTERNATIONAL_URL_LIST: ["https://www.reuters.com/", "https://apnews.com/", "https://www.bbc.com/news", "https://news.yahoo.co.jp/categories/world", "https://news.web.nhk/newsweb/genre/international", "https://www.jiji.com/jc/c?g=int", "https://www.nikkei.com/international/", "https://www.asahi.com/international/?iref=pc_gnavi", "https://mainichi.jp/world/", "https://www.yomiuri.co.jp/world/", "https://newspicks.com/theme-news/20191/"],
    TECHNOLOGY_URL_LIST: ["https://ai.watch.impress.co.jp/", "https://edu.watch.impress.co.jp/", "https://cloud.watch.impress.co.jp/", "https://pc.watch.impress.co.jp/", "https://internet.watch.impress.co.jp/", "https://www.verdict.co.uk/", "https://techcrunch.com/", "https://www.nature.com/news", "https://www.science.org/news", "https://arxiv.org/", "https://www.nasa.gov/news", "https://www.itmedia.co.jp/", "https://www.technologyreview.com/", "https://news.yahoo.co.jp/categories/it", "https://news.yahoo.co.jp/categories/science", "https://news.web.nhk/newsweb/genre/science-culture", "https://www.asahi.com/tech_science/?iref=pc_gnavi", "https://mainichi.jp/english/science/", "https://www.yomiuri.co.jp/science/", "https://newspicks.com/theme-news/technology/", "https://www.bbc.com/technology", "https://www.bloomberg.com/jp/technology", ],
    BUSINESS_URL_LIST: ["https://www.nikkei.com/business/", "https://toyokeizai.net/list/genre/business", "https://newspicks.com/theme-news/business/", "https://www.reuters.com/business/", "https://apnews.com/business", "https://www.bbc.com/business", "https://www.cnbc.com/business/"],
    WEATHER_URL_LIST: ["https://weather.yahoo.co.jp/weather/", "https://www.jma.go.jp/jp/yoho/", "https://weathernews.jp/", "https://weathernews.jp/onebox/radar/?fm=header", "https://weathernews.jp/onebox/typhoon/?fm=header", "https://weathernews.jp/quake/?fm=header", "", "https://weathernews.jp/pollen/?fm=header", "https://tenki.jp/", "https://tenki.jp/bousai/warn/", "https://www.msn.com/ja-jp/weather/forecast/"],
    HEALTH_URL_LIST: ["https://www.ozmall.co.jp/healthcare/", "https://www.cdc.gov/", "https://www.who.int/", "https://www.nih.gov/", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/", "https://news.yahoo.co.jp/categories/life", "https://news.web.nhk/newsweb/genre/life", "https://www.jiji.com/jc/list?g=newitem", "https://www.nikkei.com/lifestyle/medical-health/", "https://www.asahi.com/apital/?iref=pc_gnavi", "https://mainichi.jp/medical/", "https://mainichi.jp/welfare/", "https://www.yomiuri.co.jp/medical/", "https://toyokeizai.net/list/genre/life", "https://www.bbc.com/health", "https://www.cnbc.com/health-and-science/", "https://www.ncgm.go.jp/", "https://www.ncc.go.jp/jp/index.html", "https://www.med.or.jp/", "https://www.amed.go.jp/", "https://medical.nikkeibp.co.jp/", "https://medicalnote.jp/", "https://www.qlife.jp/", "https://medicalnote.jp/nj_articles", "https://healthwell.jp/"],
    FASHION_URL_LIST: ["https://kstyle.com/category.ksn?categoryCode=FS", "https://www.vogue.com/", "https://www.vogue.com/business", "https://www.vogue.com/business/fashion", "https://wwd.com/", "https://wwd.com/fashion-news/", "https://wwd.com/beauty-industry-news/", "https://wwd.com/menswear-news/", "https://www.businessoffashion.com/", "https://fashionista.com/", "https://www.fashionsnap.com/", "https://www.wwdjapan.com/", "https://www.fashion-press.net/", "https://www.elle.com/jp/fashion", "https://www.gqjapan.jp/fashion", "https://news.yahoo.co.jp/categories/life", "https://news.web.nhk/newsweb/genre/life", "https://www.jiji.com/jc/list?g=newitem", "https://www.nikkei.com/lifestyle/life/", "https://www.nikkei.com/lifestyle/trend/", "https://www.asahi.com/special/fashion/?iref=pc_gnavi", "https://mainichi.jp/life/", "https://www.yomiuri.co.jp/life/", "https://toyokeizai.net/list/genre/life", "https://apnews.com/hub/fashion", "https://www.cnbc.com/fashion/", ],
    BEAUTY_URL_LIST: ["https://www.oricon.co.jp/category/beauty/", "https://www.ozmall.co.jp/beauty/", "https://www.ozmall.co.jp/cosme/haircare/", "https://www.vogue.com/beauty", "https://www.elle.com/beauty", "https://www.glamour.com/beauty", "https://www.allure.com/", "https://www.cosmeticsdesign.com/", "https://www.cosmeticsbusiness.com/", "https://www.cosmeticsandtoiletries.com/",  "https://www.asahi.com/beauty/?iref=pc_gnavi", "https://wwd.com/beauty-industry-news/", "https://fashionista.com/beauty", "https://www.fashionsnap.com/beauty/", "https://www.wwdjapan.com/category/beauty", "https://www.elle.com/jp/beauty/", "https://www.cosme.net/", "https://maquia.hpplus.jp/", "https://i-voce.jp/", "https://www.biteki.com/", "https://www.fashionsnap.com/beauty", "https://www.elle.com/jp/beauty",],
    GOURMET_URL_LIST: ["https://www.oricon.co.jp/category/gourmet/", "https://www.ozmall.co.jp/gourmet/", "https://gourmet.watch.impress.co.jp/", "https://www.eater.com/", "https://www.foodandwine.com/", "https://www.epicurious.com/", "https://apnews.com/hub/food-and-drink", "https://www.cnbc.com/food-and-beverage/", "https://www.nikkei.com/lifestyle/gourmet-travel/", "https://www.asahi.com/life/food/?iref=pc_gnavi", "https://www.yomiuri.co.jp/life/food-column/", "https://mainichi.jp/food/", "https://www.gnavi.co.jp/?null", "https://tabelog.com/matome", "https://retty.me/", "https://pro.gnavi.co.jp/magazine", "https://hitosara.com/tokyo/", "https://allabout.co.jp/gourmet", "https://macaro-ni.jp/", "https://guide.michelin.com/jp/ja", "https://guide.michelin.com/"],
    SIGHTSEEING_URL_LIST: ["https://www.asahi.com/life/travel/", "https://mainichi.jp/travel/", "https://www.yomiuri.co.jp/hobby/travel/", "https://www.lonelyplanet.com/", "https://www.travelandleisure.com/", "https://www.tripadvisor.com/", "https://www.japan.travel/en/", "https://www.mlit.go.jp/kankocho/", "https://rurubu.jp/", "https://www.jalan.net/", "https://www.jalan.net/travel/?ccnt=global_navi", "https://www.jalan.net/gourmet/?ccnt=global_navi", "https://www.jalan.net/event/?ccnt=global_navi", "https://www.jalan.net/omiyage/?ccnt=global_navi", "https://www.jalan.net/travel-journal/?ccnt=global_navi", "https://travel.watch.impress.co.jp/", "https://www.ozmall.co.jp/travel/", "https://www.ozmall.co.jp/gourmet/", "https://www.travel.co.jp/", "https://www.travel.co.jp/dom/", "https://www.travel.co.jp/int/", "https://www.travel.co.jp/guide/", "https://allabout.co.jp/r_travel", "https://tabizine.jp/", "https://retrip.jp/", "https://www.jtb.co.jp/kaigai/", "https://www.jtb.co.jp/kokunai_tour/", "https://www.jtb.co.jp/kokunai-guide/", "https://www.jtb.co.jp/med/", "https://www.jtb.co.jp/kaigai_guide/", "https://www.his-j.com/kokunai/", "https://www.his-j.com/kaigai/", "https://www.kayak.co.jp/", "https://www.expedia.co.jp/", "https://www.booking.com/", "https://www.agoda.com/"],
    ANIME_URL_LIST: ["https://news.web.nhk/newsweb/pl/news-nwa-topic-nationwide-0000022", "https://www.asahi.com/culture/manga/?iref=pc_gnavi", "https://mainichi.jp/manga-anime-game/", "https://www.yomiuri.co.jp/culture/tv/", "https://www.animenewsnetwork.com/", "https://www.crunchyroll.com/news", "https://myanimelist.net/", "https://animeanime.jp/", "https://natalie.mu/comic", "https://mantan-web.jp/", "https://www.famitsu.com/", "https://nijimen.net/", "https://dengekionline.com/", "https://animecorner.me/", "https://otakuusamagazine.com/", "https://www.animatetimes.com/", "https://www.animatetimes.com/index.php?p=1", "https://www.animatetimes.com/ranking/", "https://www.animatetimes.com/trend/", "https://www.oricon.co.jp/anime/", "https://www.oricon.co.jp/oshikatsu/", "https://www.animenewsnetwork.com/encyclopedia/anime.php", "https://www.animenewsnetwork.com/encyclopedia/manga.php", "https://www.mangaupdates.com/"],
    MANGA_URL_LIST: ["https://natalie.mu/comic", "https://www.asahi.com/culture/literature/?iref=pc_gnavi", "https://www.animenewsnetwork.com/encyclopedia/manga.php", "https://www.mangaupdates.com/", "https://www.asahi.com/culture/manga/?iref=pc_gnavi", "https://mainichi.jp/manga-anime-game/", "https://manga.watch.impress.co.jp/", "https://www.animatetimes.com/book/", "https://natalie.mu/comic", "https://mantan-web.jp/", "https://www.oricon.co.jp/", "https://ddnavi.com/", "https://realsound.jp/book", "https://hon-hikidashi.jp/", "https://www.mangazenkan.com/", "https://www.mangaupdates.com/", "https://booklive.jp/bkmrg/", "https://www.cmoa.jp/", "https://www.ebookjapan.jp/", "https://mechacomic.jp/", "https://piccoma.com/web/", "https://manga.line.me/", "https://mainichi.jp/manga-anime-game/"],
    MOVIE_URL_LIST: ["https://kstyle.com/category.ksn?categoryCode=MV", "https://kstyle.com/category.ksn?categoryCode=ET", "https://www.cinra.net/", "https://news.yahoo.co.jp/categories/entertainment", "https://mantan-web.jp/cinema/", "https://news.yahoo.co.jp/categories/entertainment", "https://news.web.nhk/newsweb/pl/news-nwa-topic-nationwide-0000022", "https://www.jiji.com/jc/c?g=ent", "https://www.nikkei.com/business/entertainment/", "https://www.asahi.com/culture/movies/?iref=pc_gnavi", "https://www.asahi.com/culture/stage/?iref=pc_gnavi", "https://mainichi.jp/movie/", "https://mainichi.jp/geinou/", "https://www.yomiuri.co.jp/culture/cinema/", "https://www.animatetimes.com/eiga/", "https://www.hollywoodreporter.com/", "https://variety.com/", "https://www.imdb.com/news/movie/", "https://www.rottentomatoes.com/", "https://www.cinematoday.jp/", "https://eiga.com/news/", "https://www.slashfilm.com/category/news/", "https://www.firstshowing.net/", "https://www.screengeek.net/", "https://www.filmstories.co.uk/category/news/", "https://www.hollywoodreporter.com/", "https://deadline.com/", "https://www.polygon.com/", "https://eiga.com/", "https://www.cinematoday.jp/", "https://www.crank-in.net/", "https://moviewalker.jp/", "https://natalie.mu/eiga"],
    GAME_URL_LIST: ["https://www.famitsu.com/", "https://www.asahi.com/culture/manga/?iref=pc_gnavi", "https://mainichi.jp/manga-anime-game/", "https://www.oricon.co.jp/animegame/", "https://www.nme.com/gaming", "https://www.animatetimes.com/game/", "https://www.polygon.com/", "https://www.4gamer.net/", "https://www.gamespot.com/news/", "https://www.ign.com/articles", "https://www.gameinformer.com/", "https://www.eurogamer.net/", "https://www.gematsu.com/", "https://dengekionline.com/category/game/page/1", "https://game.watch.impress.co.jp/", "https://hobby.watch.impress.co.jp/", "https://automaton-media.com/", "https://www.gamespark.jp/", "https://jp.ign.com", "https://cgworld.jp/"],
    MUSIC_URL_LIST: ["https://www.hollywoodreporter.com/c/music/", "https://www.oricon.co.jp/music/", "https://www.billboard.com/charts/", "https://www.billboard.com/c/music/", "https://www.nme.com/news/music", "https://www.rollingstone.com/music/music-news/", "https://natalie.mu/music", "https://barks.jp/", "https://realsound.jp/music", "https://spice.eplus.jp/", "https://rockinon.com/", "https://www.thefirsttimes.jp/", "https://utaten.com/", "https://ebravo.jp/", "https://www.jazz.co.jp/", "https://iflyer.tv/", "https://www.lisani.jp/", "https://www.jiji.com/jc/list?g=cnp", "https://www.asahi.com/culture/idol/?iref=pc_gnavi", "https://www.asahi.com/culture/music/?iref=pc_gnavi", "https://www.asahi.com/culture/classic-dance/?iref=pc_gnavi", "https://mainichi.jp/music/", "https://www.yomiuri.co.jp/culture/music/", "https://www.yomiuri.co.jp/feature/titlelist/%E3%82%AF%E3%83%A9%E3%82%B7%E3%83%83%E3%82%AF%E3%82%AC%E3%82%A4%E3%83%89/", "https://kstyle.com/category.ksn?categoryCode=KP"],
    ENTERTAINMENT_URL_LIST: ["https://kstyle.com/category.ksn?categoryCode=ET", "https://www.crank-in.net/", "https://news.web.nhk/newsweb/pl/news-nwa-topic-nationwide-0000022", "https://www.jiji.com/jc/c?g=ent", "https://www.nikkei.com/business/entertainment/", "https://www.asahi.com/culture/showbiz/?iref=pc_gnavi", "https://www.asahi.com/culture/idol/?iref=pc_gnavi", "https://www.yomiuri.co.jp/culture/tv/", "https://apnews.com/entertainment", "https://www.bbc.com/culture", "https://mdpr.jp/", "https://mantan-web.jp/", "https://www.sponichi.co.jp/entertainment/", "https://www.sanspo.com/", "https://www.sanspo.com/tag/feature/divorce/", "https://www.sanspo.com/tag/feature/romance/", "https://www.daily.co.jp/gossip/", "https://encount.press/"],
    SPORTS_URL_LIST: ["https://www.daily.co.jp/general/", "https://www.daily.co.jp/soccer/", "https://www.daily.co.jp/baseball/", "https://www.sanspo.com/sports/others/", "https://www.nikkei.com/sports/", "https://news.yahoo.co.jp/categories/sports", "https://news.web.nhk/newsweb/genre/sports", "https://www.jiji.com/jc/c?g=spo", "https://www.asahi.com/sports/?iref=pc_gnavi", "https://mainichi.jp/sports/", "https://www.yomiuri.co.jp/sports/", "https://apnews.com/sports", "https://www.bbc.com/sport", "https://www.oricon.co.jp/category/sports/"],
    OUTDOOR_URL_LIST: ["https://www.jiji.com/jc/car", "https://www.yomiuri.co.jp/hobby/atcars/", "https://car.watch.impress.co.jp/", "https://www.oricon.co.jp/category/spot/", "https://encount.press/archives/category/vehicle/", "https://press.outdoorday.jp/", "https://www.sanspo.com/fishing/", "https://www.motormagazine.co.jp/", "https://www.webcg.net/", "https://outdoorgearzine.com/", "https://www.bepal.net/", "https://www.hokkaido-np.co.jp/outdoor", "https://forestoutdoor.net/", "https://yamania.net/", "https://www.nachu-magazine.com/", "https://www.nachu-magazine.com/tag/travel/"],
    EDUCATION_URL_LIST: ["https://www.nikkei.com/lifestyle/childcare/", "https://www.asahi.com/edu/?iref=pc_gnavi", "https://mainichi.jp/edu/", "https://www.yomiuri.co.jp/life/kosodate/", "https://toyokeizai.net/list/genre/career-and-education", "https://newspicks.com/theme-news/education/", "https://www.gov-online.go.jp/parenting_education/", "https://dot.asahi.com/aerakids", "https://www.kknews.co.jp/", "https://resemom.jp/", "https://hugkum.sho.jp/", "https://benesse.jp/", "https://kodomo-manabi-labo.net/"],
    CAREER_URL_LIST: ["https://www.nikkei.com/lifestyle/workstyle/", "https://toyokeizai.net/list/genre/career-and-education", "https://newspicks.com/theme-news/education/", "https://newspicks.com/theme-news/9984/", "https://www.reuters.com/business/", "https://apnews.com/business", "https://www.bbc.com/business", "https://www.bloomberg.com/jp/companies", "https://www.ft.com/companies", "https://www.ft.com/markets", "https://www.ft.com/work-careers", "https://www.cnbc.com/business/", "https://www.businessinsider.jp/?utm_source=chatgpt.com", "https://jbpress.ismedia.jp/", "https://business.nikkei.com/", "https://diamond.jp/", "https://president.jp/", "https://www.itmedia.co.jp/business", "https://newspicks.com/", "https://logmi.jp/", "https://news.mynavi.jp/", "https://news.mynavi.jp/top/kurashi/jobhunting/"]
}

AI_AGENT_MODE_ON = "利用する"
AI_AGENT_MODE_OFF = "利用しない"

CONTACT_MODE_ON = "ON"
CONTACT_MODE_OFF = "OFF"

SEARCH_POLITICS_INFO_TOOL_NAME = "search_politics_info_tool"
SEARCH_POLITICS_INFO_TOOL_DESCRIPTION = "政治に関する情報を参照したい時に使う"
SEARCH_ECONOMICS_INFO_TOOL_NAME = "search_economics_info_tool"
SEARCH_ECONOMICS_INFO_TOOL_DESCRIPTION = "経済に関する情報を参照したい時に使う"
SEARCH_INTERNATIONAL_INFO_TOOL_NAME = "search_international_info_tool"
SEARCH_INTERNATIONAL_INFO_TOOL_DESCRIPTION = "国際に関する情報を参照したい時に使う"
SEARCH_TECHNOLOGY_INFO_TOOL_NAME = "search_technology_info_tool"
SEARCH_TECHNOLOGY_INFO_TOOL_DESCRIPTION = "技術に関する情報を参照したい時に使う"
SEARCH_BUSINESS_INFO_TOOL_NAME = "search_business_info_tool"
SEARCH_BUSINESS_INFO_TOOL_DESCRIPTION = "ビジネスに関する情報を参照したい時に使う"
SEARCH_WEATHER_INFO_TOOL_NAME = "search_weather_info_tool"
SEARCH_WEATHER_INFO_TOOL_DESCRIPTION = "天気に関する情報を参照したい時に使う"
SEARCH_HEALTH_INFO_TOOL_NAME = "search_health_info_tool"
SEARCH_HEALTH_INFO_TOOL_DESCRIPTION = "健康に関する情報を参照したい時に使う"
SEARCH_FASHION_INFO_TOOL_NAME = "search_fashion_info_tool"
SEARCH_FASHION_INFO_TOOL_DESCRIPTION = "ファッションに関する情報を参照したい時に使う"
SEARCH_BEAUTY_INFO_TOOL_NAME = "search_beauty_info_tool"
SEARCH_BEAUTY_INFO_TOOL_DESCRIPTION = "美容に関する情報を参照したい時に使う"
SEARCH_GOURMET_INFO_TOOL_NAME = "search_gourmet_info_tool"
SEARCH_GOURMET_INFO_TOOL_DESCRIPTION = "グルメに関する情報を参照したい時に使う"
SEARCH_SIGHTSEEING_INFO_TOOL_NAME = "search_sightseeing_info_tool"
SEARCH_SIGHTSEEING_INFO_TOOL_DESCRIPTION = "観光に関する情報を参照したい時に使う"
SEARCH_ANIME_INFO_TOOL_NAME = "search_anime_info_tool"
SEARCH_ANIME_INFO_TOOL_DESCRIPTION = "アニメに関する情報を参照したい時に使う"
SEARCH_MANGA_INFO_TOOL_NAME = "search_manga_info_tool"
SEARCH_MANGA_INFO_TOOL_DESCRIPTION = "マンガに関する情報を参照したい時に使う"
SEARCH_MOVIE_INFO_TOOL_NAME = "search_movie_info_tool"
SEARCH_MOVIE_INFO_TOOL_DESCRIPTION = "映画・ドラマに関する情報を参照したい時に使う"
SEARCH_GAME_INFO_TOOL_NAME = "search_game_info_tool"
SEARCH_GAME_INFO_TOOL_DESCRIPTION = "ゲームに関する情報を参照したい時に使う"
SEARCH_MUSIC_INFO_TOOL_NAME = "search_music_info_tool"
SEARCH_MUSIC_INFO_TOOL_DESCRIPTION = "音楽に関する情報を参照したい時に使う"
SEARCH_ENTERTAINMENT_INFO_TOOL_NAME = "search_entertainment_info_tool"
SEARCH_ENTERTAINMENT_INFO_TOOL_DESCRIPTION = "芸能・エンターテインメントに関する情報を参照したい時に使う"
SEARCH_SPORTS_INFO_TOOL_NAME = "search_sports_info_tool"
SEARCH_SPORTS_INFO_TOOL_DESCRIPTION = "スポーツに関する情報を参照したい時に使う"
SEARCH_OUTDOOR_INFO_TOOL_NAME = "search_outdoor_info_tool"
SEARCH_OUTDOOR_INFO_TOOL_DESCRIPTION = "アウトドアに関する情報を参照したい時に使う"
SEARCH_EDUCATION_INFO_TOOL_NAME = "search_education_info_tool"
SEARCH_EDUCATION_INFO_TOOL_DESCRIPTION = "教育に関する情報を参照したい時に使う"
SEARCH_CAREER_INFO_TOOL_NAME = "search_career_info_tool"
SEARCH_CAREER_INFO_TOOL_DESCRIPTION = "働き方・キャリアに関する情報を参照したい時に使う"

SEARCH_WEB_INFO_TOOL_NAME = "search_web_tool"
SEARCH_WEB_INFO_TOOL_DESCRIPTION = "Web検索が必要と判断した場合に使う"

SERVICE_DESCRIPTION = "個人や法人が簡単にオリジナルデザインのTシャツを作成し、環境に配慮した素材で製品化できるWebサービス"

# ==========================================
# マーケティング戦略Tool関連
# ==========================================
SYSTEM_PROMPT_MARKETING_STRATEGY = """
あなたはBtoC/BtoB双方に対応できるマーケティング戦略コンサルタントです。
以下の入力を基に、実行可能な戦略を必ず3つ提案してください。

出力ルール:
- 日本語で回答する
- 各戦略は「戦略名」「対象顧客」「施策」「根拠」「KPI」の順で記述
- KPIは数値目標の形で具体化する（例: CVR 1.2%→1.8%）
- 推測だけで断定せず、Web検索結果に基づく根拠を明示
- 最後に「優先実行順（1〜3位）」を記載

入力:
- サービス概要: {service_description}
- ユーザー要望: {user_request}
- Web検索結果: {web_context}
"""

# ==========================================
# Slack連携関連
# ==========================================
EMPLOYEE_FILE_PATH = "./data/slack/従業員情報.csv"
INQUIRY_HISTORY_FILE_PATH = "./data/slack/問い合わせ対応履歴.csv"
CSV_ENCODING = "utf-8-sig"


# ==========================================
# プロンプトテンプレート
# ==========================================
SYSTEM_PROMPT_CREATE_INDEPENDENT_TEXT = "会話履歴と最新の入力をもとに、会話履歴なしでも理解できる独立した入力テキストを生成してください。"

NO_DOC_MATCH_MESSAGE = "回答に必要な情報が見つかりませんでした。弊社に関する質問・要望を、入力内容を変えて送信してください。"

SYSTEM_PROMPT_INQUIRY = """
    あなたは社内文書を基に、顧客からの問い合わせに対応するアシスタントです。
    以下の条件に基づき、ユーザー入力に対して回答してください。

    【条件】
    1. ユーザー入力内容と以下の文脈との間に関連性がある場合のみ、以下の文脈に基づいて回答してください。
    2. ユーザー入力内容と以下の文脈との関連性が明らかに低い場合、「回答に必要な情報が見つかりませんでした。弊社に関する質問・要望を、入力内容を変えて送信してください。」と回答してください。
    3. 憶測で回答せず、あくまで以下の文脈を元に回答してください。
    4. できる限り詳細に、マークダウン記法を使って回答してください。
    5. マークダウン記法で回答する際にhタグの見出しを使う場合、最も大きい見出しをh3としてください。
    6. 複雑な質問の場合、各項目についてそれぞれ詳細に回答してください。
    7. 必要と判断した場合は、以下の文脈に基づかずとも、一般的な情報を回答してください。

    {context}
"""

SYSTEM_PROMPT_EMPLOYEE_SELECTION = """
    # 命令
    以下の「顧客からの問い合わせ」に対して、社内のどの従業員が対応するかを
    判定する生成AIシステムを作ろうとしています。

    以下の「従業員情報」は、問い合わせに対しての一人以上の対応者候補のデータです。
    しかし、問い合わせ内容との関連性が薄い従業員情報が含まれている可能性があります。
    以下の「条件」に従い、従業員情報の中から、問い合わせ内容との関連性が特に高いと思われる
    従業員の「ID」をカンマ区切りで返してください。

    # 顧客からの問い合わせ
    {query}

    # 条件
    - 全ての従業員が、問い合わせ内容との関連性が高い（対応者候補である）と判断した場合は、
    全ての従業員の従業員IDをカンマ区切りで返してください。ただし、関連性が低い（対応者候補に含めるべきでない）
    と判断した場合は省いてください。
    - 特に、「過去の問い合わせ対応履歴」と、「対応可能な問い合わせカテゴリ」、また「現在の主要業務」を元に判定を
    行ってください。
    - 一人も対応者候補がいない場合、空文字を返してください。
    - 判定は厳しく行ってください。

    # 従業員情報
    {context}

    # 出力フォーマット
    {format_instruction}
"""

SYSTEM_PROMPT_SELECTION_REASON = """
あなたは問い合わせ担当者のアサイン理由を説明するアシスタントです。
以下の問い合わせ内容と担当候補情報をもとに、選ばれた従業員ごとの選定理由を作成してください。

# 問い合わせ内容
{query}

# 選定された従業員情報
{selected_context}

# 出力ルール
- 日本語
- 各従業員ごとに2〜3文
- 「過去の対応履歴」「対応可能カテゴリ」「現在の主要業務」の観点を必ず含める
- 形式:
  - 従業員ID: <ID>
    選定理由: <理由>
"""

SLACK_CHANNEL_NAME = "23-3問い合わせ対応自動化aiエージェント用"
NO_ASSIGNEE_MESSAGE = "申し訳ございませんが、今回の問い合わせ内容に最も適した担当者を特定できませんでした。引き続き内容を確認し、適切な担当者が対応できるよう努めます。ご不便をおかけして申し訳ございませんが、何卒ご理解いただけますと幸いです。"
SYSTEM_PROMPT_NOTICE_SLACK = """
    # 役割
    具体的で分量の多いメッセージの作成と、指定のメンバーにメンションを当ててSlackへの送信を行うアシスタント


    # 命令
    Slackの「23-3問い合わせ対応自動化aiエージェント用」チャンネルで、メンバーIDが{slack_id_text}のメンバーに一度だけメンションを当て、生成したメッセージを送信してください。


    # 送信先のチャンネル名
    23-3問い合わせ対応自動化aiエージェント用


    # メッセージの通知先
    メンバーIDが{slack_id_text}のメンバー


    # メッセージ通知（メンション付け）のルール
    - メッセージ通知（メンション付け）は、メッセージの先頭で「一度だけ」行ってください。
    - メンション付けの行は、メンションのみとしてください。


    # メッセージの生成条件
    - 各項目について、できる限り長い文章量で、具体的に生成してください。

    - 「メッセージフォーマット」を使い、以下の各項目の文章を生成してください。
        - 【問い合わせ情報】の「カテゴリ」
        - 【問い合わせ情報】の「日時」
        - 【回答・対応案とその根拠】

    - 「顧客から弊社への問い合わせ内容」と「従業員情報と過去の問い合わせ対応履歴」を基に文章を生成してください。

    - 【問い合わせ情報】の「カテゴリ」は、【問い合わせ情報】の「問い合わせ内容」を基に適切なものを生成してください。

    - 【回答・対応案】について、以下の条件に従って生成してください。
        - 回答・対応案の内容と、それが良いと判断した根拠を、それぞれ3つずつ生成してください。


    # 顧客から弊社への問い合わせ内容
    {query}


    # 従業員情報と過去の問い合わせ対応履歴
    {context}


    # メッセージフォーマット
    こちらは顧客問い合わせに対しての「担当者割り振り」と「回答・対応案の提示」を自動で行うAIアシスタントです。
    担当者は問い合わせ内容を確認し、対応してください。

    ================================================

    【問い合わせ情報】
    ・問い合わせ内容: {query}
    ・カテゴリ: 
    ・問い合わせ者: 山田太郎
    ・日時: {now_datetime}

    --------------------

    【メンション先の選定理由】
    {selection_reasons}

    --------------------

    【回答・対応案】
    ＜1つ目＞
    ●内容: 
    ●根拠: 

    ＜2つ目＞
    ●内容: 
    ●根拠: 

    ＜3つ目＞
    ●内容: 
    ●根拠: 

    --------------------

    【参照資料】
    ・従業員情報.csv
    ・問い合わせ履歴.csv
"""


# ==========================================
# エラー・警告メッセージ
# ==========================================
COMMON_ERROR_MESSAGE = "このエラーが繰り返し発生する場合は、管理者にお問い合わせください。"
INITIALIZE_ERROR_MESSAGE = "初期化処理に失敗しました。"
CONVERSATION_LOG_ERROR_MESSAGE = "過去の会話履歴の表示に失敗しました。"
MAIN_PROCESS_ERROR_MESSAGE = "ユーザー入力に対しての処理に失敗しました。"
DISP_ANSWER_ERROR_MESSAGE = "回答表示に失敗しました。"
INPUT_TEXT_LIMIT_ERROR_MESSAGE = f"入力されたテキストの文字数が受付上限値（{MAX_ALLOWED_TOKENS}）を超えています。受付上限値を超えないよう、再度入力してください。"


# ==========================================
# スタイリング
# ==========================================
STYLE = """
<style>
    .stHorizontalBlock {
        margin-top: -14px;
    }
    .stChatMessage + .stHorizontalBlock {
        margin-left: 56px;
    }
    .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
        margin-left: -24px;
    }
    @media screen and (max-width: 480px) {
        .stChatMessage + .stHorizontalBlock {
            flex-wrap: nowrap;
            margin-left: 56px;
        }
        .stChatMessage + .stHorizontalBlock .stColumn:nth-of-type(2) {
            margin-left: -206px;
        }
    }
</style>
"""