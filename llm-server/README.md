# LLM-Server

- チャットボットのエンジン（OpenAIとの橋渡し）部分

- [original](https://github.com/KtechB/llm-server) を改変したもの

## Dev

```
# poetry lock --no-update (ライブラリをアップデートする場合)

poetry install
sudo poetry shell # port=80の場合はsudo必須
export OPENAI_API_KEY="sk-***c"
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

### インタプリタでのテスト
```
import src.chat as c
import src.gen.util as u

u.print_reply(c.reply(c.sample_hist2))
```


## Production

### ローカル

```
./save_to_ecr.sh
```

### 運用サーバ

```
$(aws ecr get-login --no-include-email --region ap-northeast-1 --profile share) && docker image pull 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat-server:4
docker run -p 80:80 --env-file .env -it 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat-server:4
```
