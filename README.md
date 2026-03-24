# TrendSearcher

### 各トピックについて、最新情報をまとめてくれるチャットボット
 - 対応可能なトピック：政治、経済、国際、テクノロジー、ビジネス、天気、健康、ファッション、美容、グルメ、観光、アニメ、漫画、映画・ドラマ、ゲーム、音楽、芸能・エンタメ、スポーツ、アウトドア、教育、働き方・キャリア
 - Googleによる検索結果の要約にRAGを、質問内容から各トピック用のLLMを起動するのにAIエージェントを使用しています。
 - 具体的な質問に関しては、「AIエージェント機能の利用有無」を「利用しない」の状態にすると、質問内容を基に適切なWeb検索で調べてくれます。
 - 「SNSモード」をonにすると、YouTubeの情報をまとめてくれます。

### 実行手順
- 「pip install -r requirements.txt」で必要なライブラリをインストール
- 「.env」に、「OPENAI_API_KEY」、「SERPAPI_API_KEY」、「YOUTUBE_API_KEY（YouTubeDataAPI[https://note.com/quicktoolbox/n/nb2c4c32c5e7f] ）」を定義する
- 「streamlit run main.py」でアプリを起動

### 出力例
- 「AIエージェント機能の利用有無」：利用する、「SNSモード」：OFF  

<img width="1097" height="945" alt="image" src="https://github.com/user-attachments/assets/b583524c-563e-408e-ba6c-849bd4d694b0" />  
<img width="886" height="812" alt="image" src="https://github.com/user-attachments/assets/fe7e6df6-718c-4bf3-b66f-9dc02a4593ef" />  
<img width="1010" height="966" alt="image" src="https://github.com/user-attachments/assets/d6466640-1bfe-4425-b4c8-0c99943f1698" />  


- 「AIエージェント機能の利用有無」：利用しない、「SNSモード」：OFF  

<img width="886" height="734" alt="image" src="https://github.com/user-attachments/assets/4b665318-4be0-4161-9597-66a95daeecff" />  
<img width="1010" height="902" alt="image" src="https://github.com/user-attachments/assets/6662ea3a-8414-4fba-ac58-48d8d4234b2f" />  


- 「AIエージェント機能の利用有無」：利用する、「SNSモード」：ON  

<img width="886" height="692" alt="image" src="https://github.com/user-attachments/assets/f53f5477-96f5-407f-8bd2-8297716c07da" />  
<img width="886" height="835" alt="image" src="https://github.com/user-attachments/assets/7c95be50-8c6e-4dba-8ee7-95d6606d6518" />  


- 
