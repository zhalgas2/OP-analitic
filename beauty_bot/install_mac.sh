#!/bin/bash
# Mac-та ботты фонда (Terminal-сыз) автоматты түрде жұмыс істететін скрипт.
#
#   bash install_mac.sh BOT_TOKEN ADMIN_ID   — орнату / жаңарту / қайта іске қосу
#   bash install_mac.sh status               — бот жұмыс істеп тұр ма
#   bash install_mac.sh stop                 — ботты толық тоқтату
#
# Бот Mac қосылғанда өзі іске қосылады, құласа 10 секундтан кейін қайта қосылады,
# жұмыс кезінде Mac-тың ұйқыға кетуіне жол бермейді (қақпағы ашық тұрғанда).

LABEL="kz.beautyshop.bot"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/bot.log"
UID_NUM="$(id -u)"

unload() { launchctl bootout "gui/$UID_NUM/$LABEL" >/dev/null 2>&1 || true; }

case "$1" in
  stop)
    unload
    rm -f "$PLIST"
    echo "⏹  Бот тоқтатылды және автоматты іске қосу өшірілді."
    exit 0
    ;;
  status)
    if launchctl print "gui/$UID_NUM/$LABEL" 2>/dev/null | grep -q "state = running"; then
      echo "✅ Бот жұмыс істеп тұр."
    else
      echo "❌ Бот жұмыс істеп тұрған жоқ."
    fi
    echo "--- соңғы жазулар ($LOG) ---"
    tail -n 15 "$LOG" 2>/dev/null || echo "(лог әлі жоқ)"
    exit 0
    ;;
esac

TOKEN="$1"
ADMINS="$2"
if [ -z "$TOKEN" ] || [ -z "$ADMINS" ]; then
  echo "Қолданылуы: bash install_mac.sh BOT_TOKEN ADMIN_ID"
  exit 1
fi

PY="$(python3 -c 'import sys; print(sys.executable)')" || { echo "❌ python3 табылмады"; exit 1; }
echo "📦 Кітапханаларды тексеру..."
python3 -m pip install -q --user -r "$DIR/requirements.txt" 2>&1 | grep -v -i "warning" || true

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string>
    <string>-i</string>
    <string>$PY</string>
    <string>$DIR/bot.py</string>
  </array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>BOT_TOKEN</key><string>$TOKEN</string>
    <key>ADMIN_IDS</key><string>$ADMINS</string>
    <key>PYTHONUNBUFFERED</key><string>1</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF
chmod 600 "$PLIST"

unload
: > "$LOG"
launchctl bootstrap "gui/$UID_NUM" "$PLIST" || { echo "❌ Іске қосу сәтсіз болды"; exit 1; }

echo "⏳ Бот іске қосылуда..."
sleep 6
if grep -q "Run polling" "$LOG"; then
  echo "✅ Бот фонда жұмыс істеп тұр! Terminal-ды жаба беруге болады."
else
  echo "⚠️  Бот әлі қосылмады. Соңғы жазулар:"
  tail -n 15 "$LOG"
fi
