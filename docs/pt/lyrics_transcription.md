# Transcrição e Alinhamento de Letras

Wavoscope oferece uma trilha de letras dedicada para transcrição interativa, alinhamento palavra por palavra e exportação MusicXML. Esta funcionalidade foi projetada para entrada rápida e ajuste preciso de tempo.

## Conceitos Fundamentais

### A Trilha de Letras
A trilha de letras é uma trilha especializada baseada em canvas, localizada acima da forma de onda principal. Exibe os elementos da letra como caixas editáveis.
- **Visibilidade:** Alterne a trilha usando o botão "Letras" no cabeçalho da forma de onda.
- **Escala:** A altura da trilha é fixa (32px), mas seu conteúdo acompanha o zoom e a rolagem globais.
- **Seleção:** Apenas uma letra pode ser selecionada por vez. Selecionar uma letra a destaca e ativa atalhos de teclado específicos.

### Fluxo de Trabalho: "Digitar-Dividir-Avançar"
A forma mais eficiente de transcrever uma música é seguindo este fluxo:
1.  **Início:** Pressione `L` ou clique em um espaço vazio para criar a primeira letra na posição atual do cursor.
2.  **Digitar:** Digite a primeira palavra.
3.  **Dividir:** Pressione `Espaço` (para novas palavras) ou `-` (para sílabas dentro de uma palavra). Isso confirma o texto atual e cria imediatamente uma nova caixa de letra.
4.  **Repetir:** O foco é transferido automaticamente para a nova caixa, permitindo que você continue transcrevendo enquanto a música toca.
5.  **Confirmar:** Pressione `Enter` ou clique em outro lugar para encerrar a edição.

## Interação e Atalhos

### Controle do Mouse
- **Clique Único (espaço vazio):** Adiciona uma nova letra naquela posição de tempo e entra no modo de edição.
- **Clique Esquerdo (caixa existente):** Seleciona a letra.
- **Clique Único (caixa selecionada):** Desmarca a letra.
- **Arrastar (centro 80%):** Move o elemento da letra ao longo da linha do tempo.
- **Arrastar (bordas 10%):** Redimensiona a letra. Arrastar a borda esquerda ajusta o início; arrastar a borda direita ajusta a duração.
- **Clique Duplo:** Entra no modo de edição para a letra clicada.
- **Clique no Fundo:** Desmarca a letra atual.

### Atalhos de Teclado

| Tecla | Ação | Contexto |
|-------|--------|----------|
| `L` | Adicionar / Confirmar e Avançar | Global |
| `Shift + L` | Desmarcar tudo | Global |
| `Tab` | Ciclar modos de loop | Global |
| `Enter` | Iniciar/Encerrar edição | Selecionado |
| `Esc` | Cancelar edição / Desmarcar | Selecionado |
| `Setas (Esquerda/Direita)` | Ajustar posição (0.1s) | Selecionado (Sem editar) |
| `Setas (Cima/Baixo)` | Ajustar duração (0.1s) | Selecionado (Sem editar) |
| `Shift + Setas` | Pular entre letras | Global / Selecionado |
| `Espaço / -` | Confirmar e gerar próxima | Editando |

## Implementação Técnica

### Frontend
- **`LyricsTimeline.tsx`**: Utiliza um sistema de gerenciamento de estado baseado em referências para lidar com interações de alta frequência (arrastar) localmente antes de confirmar no backend. Usa um `ResizeObserver` para renderização reativa do canvas.
- **Gerenciamento de Estado**: Integrado no `projectSlice.ts`. Operações CRUD são otimizadas para atualizar o estado local diretamente a partir das respostas do backend, minimizando o tráfego de rede.
- **Visualização**: Possui um motor de renderização dinâmico que gerencia o truncamento e desvanecimento do texto para elementos pequenos.

### Backend
- **Estrutura de Dados**: Letras são armazenadas como uma lista ordenada de objetos `{text, timestamp, duration}` no arquivo `.oscope`.
- **Motor de Loop**: O `LoopingEngine` suporta um modo `lyric`, que define automaticamente o intervalo do loop para a letra selecionada no momento.
- **Exportação MusicXML**: `session/export.py` divide os compassos em segmentos em cada limite de letra e harmonia. Isso garante que as tags `<lyric>` estejam perfeitamente alinhadas com a estrutura rítmica na partitura exportada.

## Dicas de Alinhamento
- **Zoom Alto:** Para alinhamento palavra por palavra, aumente o zoom até ver claramente os transientes na forma de onda.
- **Loops:** Use o modo de loop `lyric` (alterne com `Tab`) para repetir a palavra atual enquanto ajusta seus pontos de início e fim.
- **Metrônomo:** Mantenha os cliques de subdivisão ativados para garantir que suas letras se alinhem com os marcadores de batida (Marcadores de Ritmo).
