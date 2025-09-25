# LLM Client

- チャットボットのクライアント（UI）部分

- [original](https://github.com/KtechB/llm-interface-react/tree/v0.0.0)を改変したもの


## First Step


npm install


以下のようにvite.config.jsを変更

- [参考](https://choice-site.com/2021/06/24/docker%E3%81%ABvite%E3%82%92%E5%85%A5%E3%82%8C%E3%81%A6vue%E3%81%A7%E9%96%8B%E7%99%BA%E3%81%97%E3%82%88%E3%81%86%E3%81%A8%E3%81%97%E3%81%9F%E3%81%A8%E3%81%8Dlocalhost%E3%81%AB%E7%B9%8B%E3%81%8C/)


## 開発

```
export default defineConfig({
plugins: [vue()],
server: {
host: true
}
})
```

- `websocketのエンドポイントをllm-serverのものに変更する`

## 起動

```
yarn dev
```

### 開発サーバでの挙動テスト

``` 
# vite buildしてngnixでホスティング
docker build -t llm-client . && docker run -p 80:80 llm-client:latest


# デプロイ
./save_to_ecr.sh 1
```



## 本番


### 運用サーバ

```
$(aws ecr get-login --no-include-email --region ap-northeast-1 --profile share) && docker image pull 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat:1
docker run -p 80:80  -it 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat:1
```
