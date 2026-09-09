# Entrega 2 — Estimativa AWS

[Comparação completa com gráfico, quatro prints e justificativa no README principal](../README.md#entrega-2--computação-em-nuvem-aws) · [Vídeo](https://www.youtube.com/watch?v=N1n0pr-CVUY)

Mesma máquina Linux compartilhada t3.micro, 2 vCPU, 1 GiB, até 5 Gbps, 730 horas On-Demand por mês e EBS magnético de 50 GB, sem snapshots.

| Região | EC2 mensal USD | EBS mensal USD | Total USD |
|---|---:|---:|---:|
| Virgínia | 7,59 | 2,50 | 10,09 |
| São Paulo | 12,26 | 6,00 | 18,26 |

Virgínia é US$8,17 mais barata. São Paulo atende à restrição de residência de dados no Brasil do cenário proposto; a vantagem de latência é uma expectativa a medir.

As tarifas fixas no script reproduzem as capturas fornecidas da AWS Pricing Calculator. Para gerar novamente CSV e gráfico, execute a partir da pasta principal:

```powershell
.\.venv\Scripts\python.exe entrega2_aws/scripts/gerar_comparativo_aws.py
```

Não é uma consulta de preços ao vivo. Exclusões e limites da estimativa estão no README principal.
