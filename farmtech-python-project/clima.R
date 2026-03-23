# ============================================================
# FarmTech Solutions - Consulta de Dados Climaticos em R
# Conecta-se a API meteorologica publica Open-Meteo
# (Ir alem: usar R para coletar dados climaticos)
# ============================================================

# Limpar ambiente
rm(list = ls())

# Verificar e instalar pacotes necessarios
if (!requireNamespace("httr", quietly = TRUE)) {
  install.packages("httr", repos = "https://cloud.r-project.org")
}
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  install.packages("jsonlite", repos = "https://cloud.r-project.org")
}

library(httr)
library(jsonlite)

# ------------------------------------------------------------
# CONFIGURACAO - Coordenadas de cidades brasileiras
# ------------------------------------------------------------
cidades <- data.frame(
  nome = c("Sao Paulo", "Campinas", "Ribeirao Preto"),
  latitude = c(-23.55, -22.91, -21.18),
  longitude = c(-46.63, -47.06, -47.81),
  stringsAsFactors = FALSE
)

cat("\n")
cat("==================================================\n")
cat("  FARMTECH SOLUTIONS - Dados Climaticos\n")
cat("  Fonte: API Open-Meteo (gratuita, sem chave)\n")
cat("==================================================\n\n")

# ------------------------------------------------------------
# MENU DE SELECAO DE CIDADE
# ------------------------------------------------------------
cat("  Cidades disponiveis:\n")
for (i in seq_len(nrow(cidades))) {
  cat("  ", i, "-", cidades$nome[i], "\n")
}

cat("\n")
escolha <- as.integer(readline(prompt = "  Escolha a cidade (1-3): "))

if (is.na(escolha) || escolha < 1 || escolha > nrow(cidades)) {
  cat("  [!] Opcao invalida. Usando Sao Paulo como padrao.\n")
  escolha <- 1
}

cidade <- cidades$nome[escolha]
lat <- cidades$latitude[escolha]
lon <- cidades$longitude[escolha]

cat("\n  >> Consultando dados para:", cidade, "\n")
cat("  >> Coordenadas: lat =", lat, ", lon =", lon, "\n\n")

# ------------------------------------------------------------
# CONSULTA A API OPEN-METEO (clima atual + previsao 7 dias)
# ------------------------------------------------------------
url_atual <- paste0(
  "https://api.open-meteo.com/v1/forecast?",
  "latitude=", lat,
  "&longitude=", lon,
  "&current_weather=true",
  "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum",
  "&timezone=America/Sao_Paulo"
)

tryCatch({
  resposta <- GET(url_atual)

  if (status_code(resposta) == 200) {
    dados <- fromJSON(content(resposta, "text", encoding = "UTF-8"))

    # Clima atual
    atual <- dados$current_weather
    cat("==================================================\n")
    cat("  CLIMA ATUAL -", cidade, "\n")
    cat("==================================================\n")
    cat("  Temperatura:     ", atual$temperature, "C\n")
    cat("  Vento:           ", atual$windspeed, "km/h\n")
    cat("  Direcao do vento:", atual$winddirection, "graus\n")
    cat("  Horario:         ", atual$time, "\n\n")

    # Previsao 7 dias
    diario <- dados$daily
    datas <- diario$time
    temp_max <- diario$temperature_2m_max
    temp_min <- diario$temperature_2m_min
    chuva <- diario$precipitation_sum

    cat("==================================================\n")
    cat("  PREVISAO 7 DIAS -", cidade, "\n")
    cat("==================================================\n")
    cat(sprintf("  %-12s %-10s %-10s %-10s\n", "Data", "Max(C)", "Min(C)", "Chuva(mm)"))
    cat("  ", strrep("-", 42), "\n", sep = "")

    for (i in seq_along(datas)) {
      cat(sprintf("  %-12s %-10.1f %-10.1f %-10.1f\n",
                  datas[i], temp_max[i], temp_min[i], chuva[i]))
    }

    # Estatisticas da previsao
    cat("\n==================================================\n")
    cat("  ESTATISTICAS DA PREVISAO\n")
    cat("==================================================\n")
    cat("  Media temp. maxima: ", round(mean(temp_max), 1), "C\n")
    cat("  Media temp. minima: ", round(mean(temp_min), 1), "C\n")
    cat("  Desvio padrao (max):", round(sd(temp_max), 1), "C\n")
    cat("  Desvio padrao (min):", round(sd(temp_min), 1), "C\n")
    cat("  Total de chuva:     ", round(sum(chuva), 1), "mm\n")
    cat("  Media de chuva/dia: ", round(mean(chuva), 1), "mm\n\n")

  } else {
    cat("  [!] Erro na requisicao. Codigo:", status_code(resposta), "\n")
  }

}, error = function(e) {
  cat("  [!] Erro ao conectar com a API:\n")
  cat("  ", conditionMessage(e), "\n")
  cat("  Verifique sua conexao com a internet.\n")
})

cat(">> Consulta climatica concluida!\n\n")
