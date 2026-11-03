#!/bin/bash
# PythonAnywhere (тегін хостинг) ішінде ботты орнату/жаңарту.
# PythonAnywhere → Consoles → Bash ішінде іске қосылады:
#
#   bash ~/OP-analitic/beauty_bot/pa_setup.sh BOT_TOKEN ADMIN_ID
#
# Алдын ала: Web қойындысында "Add a new web app" → "Manual configuration" арқылы сайт құрылған болуы керек.

TOKEN="$1"
ADMINS="$2"
if [ -z "$TOKEN" ] || [ -z "$ADMINS" ]; then
  echo "Қолданылуы: bash ~/OP-analitic/beauty_bot/pa_setup.sh BOT_TOKEN ADMIN_ID"
  exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
DOMAIN="${PYTHONANYWHERE_DOMAIN:-pythonanywhere.com}"
SITE="$USER.$DOMAIN"
WSGI="/var/www/${SITE//./_}_wsgi.py"
PROXY="http://proxy.server:3128"

if [ ! -f "$WSGI" ]; then
  echo "❌ Сайт әлі құрылмаған ($WSGI табылмады)."
  echo "   Алдымен: Web қойындысы → Add a new web app → Next → Manual configuration → Python (ең жаңасы) → Next."
  exit 1
fi

echo "📦 Кітапханаларды орнату (1-2 минут)..."
PYS=""
for v in 3.13 3.12 3.11 3.10; do
  if command -v "python$v" >/dev/null 2>&1; then
    "python$v" -m pip install -q --user -r "$DIR/requirements.txt" 2>&1 | grep -iv "warning" || true
    PYS="$PYS python$v"
  fi
done
PY="$(echo $PYS | awk '{print $1}')"
[ -z "$PY" ] && { echo "❌ Python табылмады"; exit 1; }

echo "📝 Сайт баптауларын жазу..."
cat > "$WSGI" <<EOF
# Beauty Shop Telegram боты — pa_setup.sh автоматты жазған файл
import os
import sys

os.environ["BOT_TOKEN"] = "$TOKEN"
os.environ["ADMIN_IDS"] = "$ADMINS"
os.environ.setdefault("https_proxy", "$PROXY")

sys.path.insert(0, "$DIR")
from wsgi_app import application  # noqa: E402,F401
EOF
chmod 600 "$WSGI"

echo "🔗 Telegram-ға webhook орнату..."
cd "$DIR" || exit 1
if ! BOT_TOKEN="$TOKEN" ADMIN_IDS="$ADMINS" https_proxy="${https_proxy:-$PROXY}" \
     "$PY" wsgi_app.py "https://$SITE/webhook"; then
  echo "❌ Webhook орнатылмады. Жоғарыдағы қатені скриншот жасап жіберіңіз."
  exit 1
fi

touch "$WSGI"   # сайтты қайта жүктеу
echo ""
echo "✅ Дайын! Енді Web қойындысында жасыл «Reload $SITE» батырмасын басыңыз,"
echo "   содан кейін Telegram-да ботқа /start жазып тексеріңіз."
