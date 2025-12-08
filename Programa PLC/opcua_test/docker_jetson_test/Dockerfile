FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1

RUN apk update && apk upgrade
RUN apk add --no-cache libc6-compat
RUN apk add --no-cache libffi-dev
RUN apk add --no-cache make
RUN apk add --no-cache cmake
RUN apk add --no-cache musl-dev
RUN apk add --no-cache linux-headers
RUN apk add --no-cache libgcc
RUN apk add --no-cache jansson
RUN apk add --no-cache libstdc++
RUN apk add --no-cache zstd-libs
RUN apk add --no-cache binutils
RUN apk add --no-cache libgomp
RUN apk add --no-cache libatomic
RUN apk add --no-cache gmp
RUN apk add --no-cache isl26
RUN apk add --no-cache mpfr4
RUN apk add --no-cache mpc1
RUN apk add --no-cache gcc
COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt
COPY . .

ENTRYPOINT [ "python3", "test_optix.py" ]
