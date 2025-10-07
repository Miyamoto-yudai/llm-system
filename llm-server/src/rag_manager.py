"""
RAGマネージャー
OpenAI Assistants APIのFile Search機能を使用して判例検索を実装
"""

import json
import logging
import re
from typing import List, Dict, Optional, Generator
from functools import lru_cache

import src.config as config


class RAGAssistantManager:
    """OpenAI Assistants APIを使用したRAG管理クラス"""

    def __init__(self):
        self.client = config.get_openai_client()
        self.vector_store_id = config.get_vector_store_id()
        self.rag_only_mode = config.get_rag_only_mode()

    def _format_sentencing_json(self, json_str: str) -> str:
        """量刑予測のJSON結果を読みやすく整形"""
        try:
            # JSONを抽出（```json...```で囲まれている場合もある）
            json_match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)

            # JSONをパース
            data = json.loads(json_str)

            formatted_lines = []
            for crime_name, sentencing_info in data.items():
                formatted_lines.append(f"\n【{crime_name}の量刑】")

                # 優先順位
                if sentencing_info and len(sentencing_info) > 0:
                    priorities = sentencing_info[0]
                    priority_list = []
                    for key in sorted(priorities.keys()):
                        priority_list.append(priorities[key])
                    formatted_lines.append(f"量刑の種類（優先順位順）: {' → '.join(priority_list)}")

                # 各量刑の詳細
                if len(sentencing_info) > 1:
                    for item in sentencing_info[1:]:
                        if 'type' in item:
                            sent_type = item['type']
                            if sent_type == '執行猶予付き懲役':
                                formatted_lines.append(
                                    f"  • {sent_type}: 懲役{item.get('min_value', '?')}〜{item.get('max_value', '?')}、"
                                    f"執行猶予{item.get('min_suspended_sentence_value', '?')}〜{item.get('max_suspended_sentence_value', '?')}"
                                )
                            else:
                                formatted_lines.append(
                                    f"  • {sent_type}: {item.get('min_value', '?')}〜{item.get('max_value', '?')}"
                                )

            return '\n'.join(formatted_lines)

        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse sentencing JSON: {e}")
            # パースに失敗した場合は元の文字列を返す
            return json_str
        except Exception as e:
            logging.warning(f"Failed to format sentencing: {e}")
            return json_str

    def _create_crime_prediction_assistant(self, rag_only: bool = False):
        """罪名予測用のAssistantを作成"""
        rag_instruction = ""
        if rag_only:
            rag_instruction = "また、このアシスタントはアップロードされた資料に基づいて質問に答え、資料にない事柄に関しては回答しないでください。"

        instructions = f"""
### 指示文
ユーザーが入力する法的案件に対して「最も確率の高い罪」を三つ予測してください。
また、罪名のみを番号付きリスト形式で出力し、その補足等は出力を禁止します。
被害者が複数人いる場合はそれに対応した複数罪名をまとめた呼称で出力してください。
{rag_instruction}

### 出力形式
1. 〇〇
2. xxx
3. ……
"""

        # Create assistant with file_search tool and vector store (v2 API)
        assistant = self.client.beta.assistants.create(
            name="罪名予測アシスタント",
            instructions=instructions.strip(),
            model=config.get_model("main"),
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store_id]
                }
            } if self.vector_store_id else None
        )
        return assistant

    def _create_sentencing_prediction_assistant(self, rag_only: bool = False):
        """量刑予測用のAssistantを作成"""
        rag_instruction = ""
        if rag_only:
            rag_instruction = "また、このアシスタントはアップロードされた資料に基づいて質問に答え、資料にない事柄に関しては回答しないでください。"

        instructions = f"""
### 指示文
与えられた罪名を参考に、ユーザーが入力する法的案件の具体的な量刑を予測してください。
なお、解説等は出力しないでください。
罰金刑であればその罰金額を10万円単位で、
執行猶予付き懲役刑であれば執行猶予期間を1年単位で、
実刑であれば刑期を半年単位で予測してください。
また、一定程度幅を持たせて予測してください。
{rag_instruction}

### 出力形式
出力形式は出力例を参考にJSON形式にしてください。
まず最初にあり得るであろう量刑の種類(罰金、執行猶予付き懲役、懲役)を優先順位順に並べてください。
また、その際にありえないであろう量刑は入れなくて良いです。
その後、それらの量刑の最小値、最大値を量刑の種類と合わせて記述してください。

### 出力例
{{"〇〇罪":[{{"1": "罰金", "2": "執行猶予付き懲役", "3": "懲役"}}, {{'type':'罰金', 'min_value':'50万円', 'max_value':'150万円'}}, {{'type':'執行猶予付き懲役' ,'min_value':'1年', 'max_value': '3年' ,'min_suspended_sentence_value':'2年', 'max_suspended_sentence_value': '4年'}}, {{'type':'懲役', 'min_value': '2年', 'max_value': '3年'}}],
"xx罪":[{{"1": "罰金", "2": "執行猶予付き懲役", "3": "懲役"}}, {{'type':'罰金', 'min_value':'50万円', 'max_value':'150万円'}}, {{'type':'執行猶予付き懲役' ,'min_value':'1年', 'max_value': '3年' ,'min_suspended_sentence_value':'2年', 'max_suspended_sentence_value': '4年'}}, {{'type':'懲役', 'min_value': '2年', 'max_value': '3年'}}],
"□□罪":[{{"1": "罰金", "2": "執行猶予付き懲役", "3": "懲役"}}, {{'type':'罰金', 'min_value':'50万円', 'max_value':'150万円'}}, {{'type':'執行猶予付き懲役' ,'min_value':'1年', 'max_value': '3年' ,'min_suspended_sentence_value':'2年', 'max_suspended_sentence_value': '4年'}}, {{'type':'懲役', 'min_value': '2年', 'max_value': '3年'}}]}}
"""

        # Create assistant with file_search tool and vector store (v2 API)
        assistant = self.client.beta.assistants.create(
            name="量刑予測アシスタント",
            instructions=instructions.strip(),
            model=config.get_model("main"),
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store_id]
                }
            } if self.vector_store_id else None
        )
        return assistant

    def predict_crime_with_rag(self, incident_text: str, rag_only: Optional[bool] = None) -> str:
        """RAGを使用した罪名予測"""
        if rag_only is None:
            rag_only = self.rag_only_mode

        try:
            # Assistantを作成
            assistant = self._create_crime_prediction_assistant(rag_only=rag_only)

            # Threadを作成
            thread = self.client.beta.threads.create()

            # メッセージを作成
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=incident_text
            )

            # Runを実行
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            # 結果を取得
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                # 最新のアシスタントメッセージを取得
                for message in messages.data:
                    if message.role == "assistant":
                        # テキストコンテンツを抽出
                        for content in message.content:
                            if hasattr(content, 'text'):
                                result = content.text.value
                                # クリーンアップ
                                self._cleanup_assistant(assistant.id)
                                self._cleanup_thread(thread.id)
                                return result

            # エラー時のフォールバック
            self._cleanup_assistant(assistant.id)
            self._cleanup_thread(thread.id)
            return "罪名予測に失敗しました。"

        except Exception as e:
            logging.error(f"RAG crime prediction error: {e}")
            return f"エラーが発生しました: {str(e)}"

    def predict_sentencing_with_rag(
        self,
        incident_text: str,
        crime_names: str,
        rag_only: Optional[bool] = None
    ) -> str:
        """RAGを使用した量刑予測"""
        if rag_only is None:
            rag_only = self.rag_only_mode

        try:
            # Assistantを作成
            assistant = self._create_sentencing_prediction_assistant(rag_only=rag_only)

            # Threadを作成
            thread = self.client.beta.threads.create()

            # 事件内容と罪名を組み合わせて送信
            combined_content = f"""
{incident_text}

### 罪名
{crime_names}
"""

            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=combined_content
            )

            # Runを実行
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            # 結果を取得
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                # 最新のアシスタントメッセージを取得
                for message in messages.data:
                    if message.role == "assistant":
                        # テキストコンテンツを抽出
                        for content in message.content:
                            if hasattr(content, 'text'):
                                result = content.text.value
                                # JSON形式の結果を整形
                                formatted_result = self._format_sentencing_json(result)
                                # クリーンアップ
                                self._cleanup_assistant(assistant.id)
                                self._cleanup_thread(thread.id)
                                return formatted_result

            # エラー時のフォールバック
            self._cleanup_assistant(assistant.id)
            self._cleanup_thread(thread.id)
            return "量刑予測に失敗しました。"

        except Exception as e:
            logging.error(f"RAG sentencing prediction error: {e}")
            return f"エラーが発生しました: {str(e)}"

    def predict_crime_and_sentencing_with_rag(
        self,
        incident_text: str,
        rag_only: Optional[bool] = None
    ) -> Dict[str, str]:
        """RAGを使用した罪名と量刑の統合予測"""
        # 罪名予測を実行
        crime_names = self.predict_crime_with_rag(incident_text, rag_only=rag_only)

        # 量刑予測を実行
        sentencing = self.predict_sentencing_with_rag(incident_text, crime_names, rag_only=rag_only)

        return {
            "crime_names": crime_names,
            "sentencing": sentencing
        }

    def _cleanup_assistant(self, assistant_id: str):
        """Assistantを削除してリソースを解放"""
        try:
            self.client.beta.assistants.delete(assistant_id)
        except Exception as e:
            logging.warning(f"Failed to delete assistant {assistant_id}: {e}")

    def _cleanup_thread(self, thread_id: str):
        """Threadを削除してリソースを解放"""
        try:
            self.client.beta.threads.delete(thread_id)
        except Exception as e:
            logging.warning(f"Failed to delete thread {thread_id}: {e}")


# シングルトンインスタンス
@lru_cache(maxsize=1)
def get_rag_manager() -> RAGAssistantManager:
    """RAGマネージャーのシングルトンインスタンスを取得"""
    return RAGAssistantManager()
