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

    def _format_sentencing_result(self, result_text: str) -> str:
        """量刑予測の結果を整形（新形式は自然な文章なのでそのまま返す）"""
        # 新形式は自然な文章形式なので、特別な整形は不要
        # ただし、旧形式（JSON）の場合は下位互換性のために整形を試みる
        try:
            # JSONを抽出（```json...```で囲まれている場合もある）
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)

                # 旧形式（罪名ごとのJSON）を検出した場合のみ整形
                if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()):
                    formatted_lines = []
                    for crime_name, sentencing_info in data.items():
                        formatted_lines.append(f"\n【{crime_name}の量刑】")

                        if isinstance(sentencing_info, dict) and 'priorities' in sentencing_info:
                            priorities = sentencing_info.get('priorities', [])
                            sentencing_details = sentencing_info.get('sentencing_details', [])
                            reasoning = sentencing_info.get('reasoning', [])
                            advice = sentencing_info.get('advice', [])

                            formatted_lines.append("\n■ 予想される量刑（可能性が高い順）")
                            for idx, detail in enumerate(sentencing_details, 1):
                                sent_type = detail.get('type', '')
                                if sent_type == '執行猶予付き懲役':
                                    formatted_lines.append(
                                        f"{idx}. {sent_type}: 懲役{detail.get('min_value', '?')}〜{detail.get('max_value', '?')}、"
                                        f"執行猶予{detail.get('min_suspended_sentence_value', '?')}〜{detail.get('max_suspended_sentence_value', '?')}"
                                    )
                                else:
                                    formatted_lines.append(
                                        f"{idx}. {sent_type}: {detail.get('min_value', '?')}〜{detail.get('max_value', '?')}"
                                    )

                            if reasoning:
                                formatted_lines.append("\n■ 量刑判断の根拠")
                                for reason in reasoning:
                                    formatted_lines.append(f"  - {reason}")

                            if advice:
                                formatted_lines.append("\n■ 今後のアドバイス")
                                for adv in advice:
                                    formatted_lines.append(f"  - {adv}")

                    return '\n'.join(formatted_lines)

        except (json.JSONDecodeError, Exception) as e:
            # JSON解析に失敗した場合は、新形式の自然な文章として扱う
            logging.debug(f"Not JSON format, treating as natural text: {e}")

        # 新形式（自然な文章）の場合はそのまま返す
        return result_text

    def _create_crime_prediction_assistant(self, rag_only: bool = False):
        """罪名予測用のAssistantを作成"""
        rag_instruction = ""
        if rag_only:
            rag_instruction = "また、このアシスタントはアップロードされた資料に基づいて質問に答え、資料にない事柄に関しては回答しないでください。"

        instructions = f"""
### 指示文
ユーザーが入力する法的案件に対して「最も確率の高い罪」を三つ予測してください。
各罪名について、該当する法律の条文と簡潔な根拠を添えて出力してください。
被害者が複数人いる場合はそれに対応した複数罪名をまとめた呼称で出力してください。
{rag_instruction}

### 出力形式
1. 〇〇罪（刑法第XX条）
   - 該当理由: [簡潔な根拠]

2. XX罪（刑法第YY条）
   - 該当理由: [簡潔な根拠]

3. △△罪（刑法第ZZ条）
   - 該当理由: [簡潔な根拠]

### 注意事項
- 根拠は1〜2行程度で簡潔に記載してください
- 該当する構成要件や重要な事実関係を明記してください
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
複数の罪名が提示されている場合でも、量刑予測・根拠・アドバイスは全体として1つにまとめてください。

罰金刑であればその罰金額を10万円単位で、
執行猶予付き懲役刑であれば執行猶予期間を1年単位で、
実刑であれば刑期を半年単位で予測してください。
また、一定程度幅を持たせて予測してください。

以下の情報を含めてください:
1. 予想される量刑（可能性が高い順）
2. 量刑判断の根拠（考慮すべき情状など）
3. 今後のアドバイス（示談の重要性、弁護士相談など）
{rag_instruction}

### 出力形式
以下の形式で自然な文章として出力してください：

【量刑予測】
予想される量刑を可能性が高い順に記載してください。
例：「最も可能性が高いのは罰金50万円〜150万円です。示談が成立しない場合は執行猶予付き懲役1年〜3年（執行猶予2年〜4年）となる可能性があります。」

【量刑判断の根拠】
量刑判断の主要な根拠となる要素を箇条書きで3〜5項目示してください。

【今後のアドバイス】
今後のアドバイスを箇条書きで2〜3項目示してください。

注意：複数の罪名が提示されている場合でも、量刑予測は1つにまとめてください。罪名ごとに別々の量刑を提示しないでください。
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
                                # 結果を整形（新形式は自然な文章、旧形式はJSON）
                                formatted_result = self._format_sentencing_result(result)
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
