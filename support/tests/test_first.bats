# test_kubex_publish_guard.bats

setup() {
  # Roda antes de cada teste
  mkdir -p ./docs/vsctl
  rm -f ./docs/vsctl/.kubex_publish_marker_*
}

teardown() {
  # Limpa tudo depois de cada teste
  rm -rf ./docs
}

@test "Sanitize version padrão" {
  run bash scripts/kubex_publish_guard.sh sanitize_version "refs/tags/v1.2.3"
  [ "$status" -eq 0 ]
  [ "$output" = "1.2.3" ]
}

@test "Falha se contributor não autorizado" {
  export GITHUB_REF="refs/tags/v1.0.0"
  export GITHUB_ACTOR="pirata"
  export GITHUB_REPOSITORY="repo/teste"
  export GITHUB_EVENT_NAME="push"
  # Simula um contributor fake (gh precisa estar autenticado ou você pode mockar a função)
  run bash scripts/kubex_publish_guard.sh "1.0.0" "repo/teste" "pirata" "push" "false" "refs/tags/v1.0.0"
  [[ "$output" == *"not an authorized contributor"* ]]
  [ "$status" -ne 0 ]
}

@test "Falha em tag inválida" {
  run bash scripts/kubex_publish_guard.sh "1.2.3" "repo/teste" "fulano" "push" "false" "refs/heads/main"
  [[ "$output" == *"Tag does not match semver format"* ]]
  [ "$status" -ne 0 ]
}

@test "Avança em primeira execução válida" {
  export GITHUB_REF="refs/tags/v2.0.0"
  run bash scripts/kubex_publish_guard.sh "2.0.0" "repo/teste" "fulano" "push" "false" "refs/tags/v2.0.0"
  [[ "$output" == *"Proceeding with deployment"* ]]
  [ "$status" -eq 0 ]
}

@test "Aborta após limite de tentativas" {
  export GITHUB_REF="refs/tags/v3.0.0"
  # Cria marker já estourado
  mkdir -p ./docs/vsctl
  echo "COUNT=2" > ./docs/vsctl/.kubex_publish_marker_3.0.0_deadbeef
  run bash scripts/kubex_publish_guard.sh "3.0.0" "repo/teste" "fulano" "push" "false" "refs/tags/v3.0.0"
  [[ "$output" == *"has reached 2 executions"* ]]
  [ "$status" -ne 0 ]
}

@test "Reseta marker se passado de 24h" {
  export GITHUB_REF="refs/tags/v4.0.0"
  mkdir -p ./docs/vsctl
  TS=$(date -d "2 days ago" +%s)
  echo "COUNT=2" > ./docs/vsctl/.kubex_publish_marker_4.0.0_deadbeef
  echo "TIMESTAMP=$(date -d "@$TS" +"%Y-%m-%d %H:%M:%S")" >> ./docs/vsctl/.kubex_publish_marker_4.0.0_deadbeef
  run bash scripts/kubex_publish_guard.sh "4.0.0" "repo/teste" "fulano" "push" "false" "refs/tags/v4.0.0"
  [[ "$output" == *"Removing marker file, allowing runners again over this tag"* ]]
  [ "$status" -eq 0 ]
}
