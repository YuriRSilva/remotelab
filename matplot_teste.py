import matplotlib.pyplot as plt
import seaborn as sns

# Dados fictícios (substitua pelos seus dados reais)
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
instalacoes = [120, 150, 130, 140, 160, 155]
cancelamentos = [10, 12, 15, 8, 11, 9]
abandonos = [5, 6, 7, 4, 5, 6]
inadimplencia = [3, 4, 3, 2, 3, 4]
ticket_medio = [80, 85, 82, 88, 90, 87]
clientes_pagantes = [1000, 1020, 1015, 1032, 1040, 1038]

# Configurações de estilo do Seaborn
sns.set(style="whitegrid")

# Criando subplots
fig, axs = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle('Dashboard de KPIs para Provedores de Internet')

# Gráfico de Instalações
axs[0, 0].bar(meses, instalacoes, color='skyblue')
axs[0, 0].set_title('Número de Instalações')

# Gráfico de Cancelamentos
axs[0, 1].plot(meses, cancelamentos, marker='o', color='orange')
axs[0,  1].set_title('Número de Cancelamentos')

# Gráfico de Abandonos
axs[0, 2].pie(abandonos, labels=meses, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
axs[0, 2].set_title('Distribuição de Abandonos')

# Gráfico de Inadimplência
axs[1, 0].plot(meses, inadimplencia, marker='s', color='purple')
axs[1, 0].set_title('% de Inadimplência')

# Gráfico de Ticket Médio
axs[1, 1].bar(meses, ticket_medio, color='gold')
axs[1,  1].set_title('Ticket Médio')

# Gráfico de Clientes Pagantes
axs[1, 2].plot(meses, clientes_pagantes, marker='D', color='tomato')
axs[1,  2].set_title('Número de Clientes Pagantes')

# Ajustando layout
plt.tight_layout()
plt.show()
