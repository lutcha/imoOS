---
name: security-scan-owasp
description: Configuração de scan ativo OWASP ZAP para a API ImoOS, job GitHub Actions no build noturno, análise de resultados e falha em descobertas CRITICAL/HIGH, alerta Slack.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Detetar automaticamente vulnerabilidades de segurança na API ImoOS através de scans OWASP ZAP. O scan noturno garante que novas vulnerabilidades são detetadas rapidamente e o alerta Slack notifica a equipa imediatamente.

## Code Pattern

```yaml
# .github/workflows/security-scan.yml
name: OWASP ZAP Security Scan

on:
  schedule:
    - cron: "0 2 * * *"  # Diariamente às 02:00 UTC
  workflow_dispatch:      # Execução manual

jobs:
  zap-scan:
    name: OWASP ZAP Active Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging for scan
        run: echo "Staging já está disponível em ${{ secrets.STAGING_URL }}"

      - name: Create ZAP auth script
        run: |
          cat > zap_auth.py << 'EOF'
          import urllib.request, urllib.parse, json

          def authenticate(helper, paramsValues, credentials):
              url = paramsValues.get("loginUrl")
              data = json.dumps({
                  "email": credentials.getParam("username"),
                  "password": credentials.getParam("password")
              }).encode()
              req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
              response = urllib.request.urlopen(req).read()
              token = json.loads(response)["access"]
              helper.prepareMessage()
          EOF

      - name: Run OWASP ZAP Scan
        uses: zaproxy/action-api-scan@v0.7.0
        with:
          target: "${{ secrets.STAGING_URL }}/api/schema/"
          format: openapi
          rules_file_name: ".github/zap/rules.tsv"
          cmd_options: >
            -z "-config replacer.full_list(0).description=auth
                -config replacer.full_list(0).enabled=true
                -config replacer.full_list(0).matchtype=REQ_HEADER
                -config replacer.full_list(0).matchstr=Authorization
                -config replacer.full_list(0).replacement=Bearer ${{ secrets.ZAP_API_TOKEN }}"

      - name: Upload ZAP Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-report
          path: report_html.html

      - name: Parse ZAP Results and Fail on HIGH/CRITICAL
        run: |
          python3 << 'EOF'
          import json, sys

          with open("report_json.json") as f:
              report = json.load(f)

          critical_high = [
              alert for site in report.get("site", [])
              for alert in site.get("alerts", [])
              if alert.get("riskcode") in ["3", "2"]  # 3=HIGH, 2=MEDIUM, mas só falhar em 3
              if alert.get("riskcode") == "3"
          ]

          if critical_high:
              print(f"FALHA: {len(critical_high)} vulnerabilidades CRITICAL/HIGH encontradas:")
              for a in critical_high:
                  print(f"  - [{a['riskdesc']}] {a['name']}: {a['url']}")
              sys.exit(1)
          print("Sem vulnerabilidades CRITICAL/HIGH.")
          EOF

      - name: Notify Slack on Failure
        if: failure()
        uses: rtCamp/action-slack-notify@v2
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_SECURITY_WEBHOOK }}
          SLACK_MESSAGE: "ALERTA SEGURANÇA: ZAP encontrou vulnerabilidades CRITICAL/HIGH na API ImoOS. Ver: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          SLACK_COLOR: "danger"
```

```tsv
# .github/zap/rules.tsv — regras personalizadas ZAP
# IGNORE falsos positivos conhecidos
10010	IGNORE	Cookie sem secure flag — gerido pelo proxy Nginx
```

## Key Rules

- Executar o scan apenas em staging — nunca em produção (scan ativo faz pedidos que podem modificar dados).
- Falhar o build apenas em `riskcode=3` (HIGH) e `riskcode=4` (CRITICAL) — MEDIUM em modo de aviso.
- O token de autenticação para o ZAP deve ser um utilizador de teste dedicado com permissões limitadas.
- Rever o relatório HTML semanalmente mesmo sem falhas — pode conter informação útil sobre MEDIUM.

## Anti-Pattern

```yaml
# ERRADO: ignorar todos os alertas sem critério
continue-on-error: true  # anula completamente o propósito do scan de segurança
```
