REGION="ap-northeast-1"
PROFILE="share"
AWS_USER="199750128665.dkr.ecr.ap-northeast-1.amazonaws.com"
SOURCE="chat-server"
V="$1"
TAG="${SOURCE}:${V}"
TARGET="${AWS_USER}/${TAG}"

if [ -z "$1" ]; then
    echo "you must specify version like '1'"
else
    $(aws ecr get-login --no-include-email --region ${REGION} --profile ${PROFILE})
    docker build  -t ${TAG} . --build-arg CACHEBUST=$(date +%s)
    docker tag ${TAG} ${TARGET}
    docker push ${TARGET}
    echo ${V} > "version.txt"
    echo "Successfully pushed ${TAG} to ${TARGET}"
fi

## if you want to get pushed container
#  $(aws ecr get-login --no-include-email --region ap-northeast-1 --profile share) && docker image pull 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat-server:1
# docker run -p 80:80  -it 199750128665.dkr.ecr.ap-northeast-1.amazonaws.com/chat-server:1
