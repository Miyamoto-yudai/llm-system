import os
import csv
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
import src.embedding as emb
import src.gen.rag as rag

class LegalRAGLoader:
    """
    罪名予測テーブルと量刑予測ヒアリングシートのデータをRAGシステムに読み込むクラス
    """
    
    def __init__(self, data_dir: str = "rag_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def load_crime_prediction_table(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        罪名予測テーブル（TSV/CSV）を読み込んで構造化
        """
        questions = []
        
        # ファイル拡張子によって読み込み方法を変更
        delimiter = '\t' if file_path.suffix == '.tsv' else ','
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            headers = next(reader)  # ヘッダー行を取得
            
            # 最初の列は罪名なので、それ以外を質問項目として取得
            question_columns = headers[1:] if len(headers) > 1 else []
            
            # 各質問項目をRAG用データとして構造化
            for idx, question in enumerate(question_columns):
                if question and len(question.strip()) > 5:  # 有効な質問のみ
                    # カテゴリ名をファイル名から抽出
                    category = file_path.stem.replace('罪名予測テーブル - ', '').replace('罪名予測テーブル_', '')
                    
                    # 質問を端的な形式に変換
                    formatted_question = self._format_question_for_crime(question)
                    
                    questions.append({
                        'category': category,
                        'type': 'crime_prediction',
                        'original_question': question,
                        'formatted_question': formatted_question,
                        'source_file': str(file_path)
                    })
        
        return questions
    
    def load_sentencing_hearing_sheet(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        量刑予測ヒアリングシート（TSV）を読み込んで構造化
        """
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)  # ヘッダー行を取得
            
            # ID列と罪名列を除いた実質的な質問項目を取得
            question_columns = headers[2:] if len(headers) > 2 else []
            
            # 各質問項目をRAG用データとして構造化
            for idx, question in enumerate(question_columns):
                if question and len(question.strip()) > 3:  # 有効な質問のみ
                    # カテゴリ名をファイル名から抽出
                    category = file_path.stem.replace('量刑予測_ヒアリングシート - ', '')
                    
                    # 質問を端的な形式に変換
                    formatted_question = self._format_question_for_sentencing(question)
                    
                    if formatted_question:  # 有効な質問のみ追加
                        questions.append({
                            'category': category,
                            'type': 'sentencing_prediction',
                            'original_question': question,
                            'formatted_question': formatted_question,
                            'source_file': str(file_path)
                        })
        
        return questions
    
    def _format_question_for_crime(self, question: str) -> str:
        """
        罪名予測用の質問を端的な形式にフォーマット
        """
        # 長い説明文を短い質問に変換
        if "旨を告知して脅迫" in question:
            return "脅迫行為の有無と内容を教えてください"
        elif "義務のないことを行わせ" in question:
            return "強要された行為の内容を教えてください"
        elif "身体に対して直接的な拘束" in question:
            return "身体の拘束や監禁の有無と状況を教えてください"
        elif "負傷させた" in question:
            return "被害者の負傷の有無と程度を教えてください"
        elif "死亡させた" in question:
            return "死亡者の有無を教えてください"
        elif "財産上の利益" in question:
            return "金銭や財産上の利益を得る目的はありましたか"
        elif "わいせつ行為" in question:
            return "わいせつ行為の有無と内容を教えてください"
        elif "18歳未満" in question:
            return "被害者の年齢（特に18歳未満かどうか）を教えてください"
        elif "暴行" in question:
            return "暴行の有無と内容を教えてください"
        elif "凶器" in question:
            return "凶器の使用有無と種類を教えてください"
        elif "計画" in question or "準備" in question:
            return "事前の計画や準備の有無を教えてください"
        elif "常習" in question:
            return "同様の行為を繰り返していたか教えてください"
        else:
            # その他の質問は簡潔に
            return question[:50] + "について教えてください" if len(question) > 50 else question + "？"
    
    def _format_question_for_sentencing(self, question: str) -> str:
        """
        量刑予測用の質問を端的な形式にフォーマット
        """
        # ヘッダーの項目名を質問形式に変換
        if "前科" in question:
            return "前科・前歴の有無と内容を教えてください"
        elif "示談" in question:
            return "示談の成立状況と示談金額を教えてください"
        elif "被害金額" in question:
            return "被害金額を具体的に教えてください"
        elif "治療期間" in question:
            return "被害者の治療期間を教えてください"
        elif "準備・計画性" in question:
            return "犯行の計画性や準備状況を教えてください"
        elif "常習性" in question:
            return "同種犯罪の前歴や常習性について教えてください"
        elif "動機" in question or "経緯" in question:
            return "犯行の動機と経緯を詳しく教えてください"
        elif "被害感情" in question:
            return "被害者や遺族の処罰感情を教えてください"
        elif "社会的影響" in question:
            return "事件の社会的影響について教えてください"
        elif "年齢" in question:
            return "被告人の年齢を教えてください"
        elif "犯行後の情状" in question:
            return "犯行後の反省や被害者への対応を教えてください"
        elif "凶器" in question:
            return "使用した凶器の種類を教えてください"
        elif "暴行" in question or "脅迫" in question:
            return "暴行・脅迫の内容と程度を教えてください"
        else:
            # 短い項目名はそのまま返さない
            if len(question) < 10:
                return None
            return question + "について教えてください"
    
    def create_rag_data(self):
        """
        すべてのテーブルとシートを読み込んでRAGデータを生成
        """
        all_questions = []
        
        # 罪名予測テーブルの処理
        crime_table_paths = [
            Path("罪名予測テーブル"),
            Path("dataset/raw")
        ]
        
        for base_path in crime_table_paths:
            if base_path.exists():
                # TSVファイル
                for tsv_file in base_path.glob("罪名予測テーブル*.tsv"):
                    print(f"Loading: {tsv_file}")
                    questions = self.load_crime_prediction_table(tsv_file)
                    all_questions.extend(questions)
                
                # CSVファイル
                for csv_file in base_path.glob("罪名予測テーブル*.csv"):
                    print(f"Loading: {csv_file}")
                    questions = self.load_crime_prediction_table(csv_file)
                    all_questions.extend(questions)
        
        # 量刑予測ヒアリングシートの処理
        hearing_sheet_path = Path("量刑予測ヒアリングシート")
        if hearing_sheet_path.exists():
            for tsv_file in hearing_sheet_path.glob("*.tsv"):
                print(f"Loading: {tsv_file}")
                questions = self.load_sentencing_hearing_sheet(tsv_file)
                all_questions.extend(questions)
        
        # 各質問にembeddingを生成して保存
        print(f"\nGenerating embeddings for {len(all_questions)} questions...")
        for i, question_data in enumerate(all_questions):
            # フォーマット済みの質問と元の質問を組み合わせてembedding生成
            text_for_embedding = f"{question_data['formatted_question']} ({question_data['original_question']})"
            
            # RAGデータとして保存
            ref_data = {
                'text': question_data['formatted_question'],
                'emb': emb.ada(text_for_embedding),
                'tag': f"{question_data['type']}_{question_data['category']}",
                'metadata': question_data
            }
            
            # pickleファイルとして保存
            ref_path = self.data_dir / f"{question_data['type']}_{question_data['category']}_{i}.ref"
            with open(ref_path, 'wb') as f:
                pickle.dump(ref_data, f)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(all_questions)} questions")
        
        print(f"\nRAG data generation complete. {len(all_questions)} questions processed.")
        
        # メタデータを保存
        metadata = {
            'total_questions': len(all_questions),
            'crime_prediction_questions': len([q for q in all_questions if q['type'] == 'crime_prediction']),
            'sentencing_prediction_questions': len([q for q in all_questions if q['type'] == 'sentencing_prediction']),
            'categories': list(set(q['category'] for q in all_questions))
        }
        
        with open(self.data_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata

def main():
    """
    RAGデータを生成するメイン関数
    """
    loader = LegalRAGLoader()
    metadata = loader.create_rag_data()
    print("\nMetadata:")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()