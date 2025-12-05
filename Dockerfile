FROM python:3.9-slim

RUN apt-get update && apt-get install -y openssl

WORKDIR /app

# On installe PyJWT mais on va coder la verif "a la main" pour introduire la faille
RUN pip install flask pyjwt

COPY app.py .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 443

CMD ["./entrypoint.sh"]
