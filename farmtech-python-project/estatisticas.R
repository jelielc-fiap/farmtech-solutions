# Caso não tenha a biblioteca Jsonlite instalada descomente o coméntário abaixo
#install.packages("jsonlite")

library(jsonlite)

# Limpar ambiente 
rm(list = ls())

# 1. Carregamento dos dados
arquivo <- "dados_farmtech.json" 

if (!file.exists(arquivo)) {
  stop("Arquivo não encontrado! Verifique o nome gerado pelo Python.")
}

dados <- fromJSON(arquivo, simplifyVector = FALSE)

# 2. Extração de Vetores
culturas       <- sapply(dados, function(x) x$cultura)
areas_gerais   <- sapply(dados, function(x) as.numeric(x$area_plantio$area_m2))
insumos_gerais <- sapply(dados, function(x) as.numeric(x$manejo_insumos[[1]]$total_necessario_litros))
insumos_nomes  <- sapply(dados, function(x) x$manejo_insumos[[1]]$produto)

# Função para formatar o desvio padrão (evita erro de texto com apenas 1 registro)
formatar_sd <- function(vetor, casas = 2) {
  if (length(vetor) < 2) return("0.00 (Registro único)")
  return(round(sd(vetor), casas))
}


# RELATÓRIO DE ESTATÍSTICAS


cat("ESTATISTICAS GERAIS\n")
cat("======================================================================\n\n")

cat("Vetor de areas (m2):", paste(areas_gerais, collapse = " "), "\n")
cat("Media das areas:      ", round(mean(areas_gerais), 2), "m2\n")
cat("Desvio padrao areas:  ", formatar_sd(areas_gerais), "m2\n")
cat("Minimo:               ", min(areas_gerais), "m2\n")
cat("Maximo:               ", max(areas_gerais), "m2\n\n")

cat("Vetor de insumos (L):", paste(insumos_gerais, collapse = " "), "\n")
cat("Media dos insumos:    ", round(mean(insumos_gerais), 4), "L\n")
cat("Desvio padrao insumos:", formatar_sd(insumos_gerais, 4), "L\n")
cat("Minimo:               ", min(insumos_gerais), "L\n")
cat("Maximo:               ", max(insumos_gerais), "L\n\n")

# --- ESTATÍSTICAS POR CULTURA ---
tipos_presentes <- unique(culturas)

for (cult in tipos_presentes) {
  cat("======================================================================\n")
  cat("ESTATISTICAS -", toupper(cult), "\n")
  cat("======================================================================\n\n")
  
  idx <- which(culturas == cult)
  areas_v <- areas_gerais[idx]
  insumos_v <- insumos_gerais[idx]
  
  cat("Registros:", length(idx), "\n\n")
  cat("Areas (m2):", paste(areas_v, collapse = " "), "\n")
  cat("Media das areas:     ", round(mean(areas_v), 2), "m2\n")
  cat("Desvio padrao areas: ", formatar_sd(areas_v), "m2\n\n")
  
  cat("Insumo principal:", insumos_nomes[idx][1], "\n")
  cat("Quantidades (L):", paste(insumos_v, collapse = " "), "\n")
  cat("Media dos insumos:   ", round(mean(insumos_v), 4), "L\n")
  cat("Desvio padrao insumos:", formatar_sd(insumos_v, 4), "L\n\n")
}

# --- RESUMO FINAL ---
cat("======================================================================\n")
cat("RESUMO FINAL DA FAZENDA\n")
cat("======================================================================\n")
cat("Total de registros: ", length(dados), "\n")
cat("Culturas:           ", paste(tipos_presentes, collapse = " e "), "\n")
cat("Area Total:         ", sum(areas_gerais), "m2\n")
cat("Insumos Totais:     ", sum(insumos_gerais), "L\n")
cat("======================================================================\n")

cat(">> Analise estatistica concluida com sucesso!\n\n")

