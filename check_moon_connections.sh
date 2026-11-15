#!/usr/bin/env bash

set -u

echo "======================================"
echo "       M.O.O.N. CONNECTION CHECK"
echo "======================================"

check_url() {
    local name="$1"
    local url="$2"

    echo
    echo "[$name]"
    echo "URL : $url"

    if curl -sS --max-time 3 -o /tmp/moon_response.txt \
        -w "HTTP %{http_code}\n" "$url"; then
        echo "Réponse :"
        head -c 500 /tmp/moon_response.txt
        echo
    else
        echo "ERREUR : service inaccessible."
    fi
}

check_url "BACKEND PRINCIPAL" \
    "http://127.0.0.1:8000/api/health"

check_url "BACKEND SIMULATION" \
    "http://127.0.0.1:8001/health"

echo
echo "======================================"
echo "       FRONTEND"
echo "======================================"

if [ -d "frontend" ]; then
    echo "Dossier frontend : OK"

    for file in \
        frontend/vite.config.ts \
        frontend/src/services/api.ts \
        frontend/src/Welcome.tsx \
        frontend/src/App.tsx \
        frontend/package.json
    do
        if [ -f "$file" ]; then
            echo "[OK] $file"
        else
            echo "[ABSENT] $file"
        fi
    done
else
    echo "ERREUR : dossier frontend introuvable."
fi

echo
echo "======================================"
echo "       FIN DU DIAGNOSTIC"
echo "======================================"
