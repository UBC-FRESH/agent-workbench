#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

secrets_file="${VLLM_SECRETS_ENV:-/srv/shared-data/vllm/secrets.env}"
mkdir -p "$(dirname "$secrets_file")"

printf "Paste Hugging Face token: " >&2
stty -echo
IFS= read -r token
stty echo
printf "\n" >&2

if [[ -z "$token" ]]; then
  echo "No token entered; leaving ${secrets_file} unchanged." >&2
  exit 1
fi

umask 077
tmp_file="$(mktemp "${secrets_file}.tmp.XXXXXX")"
{
  printf "HF_TOKEN=%q\n" "$token"
  printf "HUGGING_FACE_HUB_TOKEN=%q\n" "$token"
} > "$tmp_file"
mv "$tmp_file" "$secrets_file"
chmod 600 "$secrets_file"

echo "Stored Hugging Face token in ${secrets_file}"
echo "Restart vLLM for the token to affect downloads."
