#!/usr/bin/env bash

# Hata olursa scripti durdur
set -e

echo "🚀 Cemil Bot hızlı başlatma scripti çalışıyor..."

# Script'in bulunduğu dizine git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Proje dizini: $SCRIPT_DIR"

# Python kontrolü
if command -v python3 &>/dev/null; then
  PYTHON_BIN=python3
elif command -v python &>/dev/null; then
  PYTHON_BIN=python
else
  echo "❌ Python bulunamadı. Lütfen Python 3.10+ kurun."
  exit 1
fi

echo "🐍 Python: $($PYTHON_BIN --version)"

# Virtualenv oluştur (yoksa)
if [ ! -d ".venv" ]; then
  echo "🧱 Sanal ortam (.venv) oluşturuluyor..."
  $PYTHON_BIN -m venv .venv
fi

# Virtualenv aktif et
echo "✅ Sanal ortam aktive ediliyor..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  # Windows (Git Bash/Powershell) için
  source ".venv/Scripts/activate"
else
  # macOS / Linux
  source ".venv/bin/activate"
fi

echo "📦 Bağımlılıklar yükleniyor (requirements.txt)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 .env dosyası kontrol ediliyor..."
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    echo "📝 .env bulunamadı, .env.example'dan kopyalanıyor..."
    cp .env.example .env
    echo "⚠️ Lütfen .env dosyasını düzenleyip Slack ve Groq anahtarlarını girin."
  else
    echo "⚠️ .env veya .env.example bulunamadı. Ortam değişkenlerini elle ayarlamanız gerekiyor."
  fi
fi

echo "🤖 Cemil Bot başlatılıyor..."
$PYTHON_BIN -m src

