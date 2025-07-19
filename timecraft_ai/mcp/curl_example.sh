#!/usr/bin/env bash


# 1. Testar busca de PRs (seus repositórios já configurados por padrão)
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "list_pull_requests",
         "arguments": {}
       }
     }'

# 2. Testar busca de PRs em repos específicos
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call", 
       "params": {
         "name": "list_pull_requests",
         "arguments": {
           "repos": "rafa-mori/lookatni-file-markers,rafa-mori/formatpilot"
         }
       }
     }'

# 3. Testar pipelines do Azure DevOps
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "get_pipeline_status", 
         "arguments": {
           "project": "kubex"
         }
       }
     }'

# 4. Adicionar nota à memória
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "add_memory_note",
         "arguments": {
           "note": "Testando o StatusRafa via curl"
         }
       }
     }'

# 5. Obter sugestão do próximo passo
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "suggest_next_step",
         "arguments": {}
       }
     }'

# 6. Ver memória recente
curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "summarize_recent_entries",
         "arguments": {
           "limit": 5
         }
       }
     }'


curl -X POST http://127.0.0.1:3001/messages/ \
     -H "Content-Type: application/json" \
     -H "session_id: test_session" \
     -d '{
       "session_id": "test_session",
       "method": "tools/call",
       "params": {
         "name": "list_pull_requests",
         "arguments": {}
       }
     }'