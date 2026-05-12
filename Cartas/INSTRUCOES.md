# Manual do Gerador de Cartas - CertGame

Este guia detalha o funcionamento e a configuração do script Python para geração dos baralhos de cartas em PDF.

## 🚀 Início Rápido

1. **Ambiente Virtual**: Crie e ative um ambiente isolado (recomendado).
   ```powershell
   # Criar venv
   python -m venv venv
   
   # Ativar (Windows)
   .\venv\Scripts\activate
   ```

2. **Dependências**: Instale as bibliotecas necessárias.
   ```bash
   pip install -r requirements.txt
   ```

3. **Execução**: Rode o script principal.
   ```bash
   python gerador_cartas.py
   ```

## 📁 Estrutura do Projeto

* `gerador_cartas.py`: Lógica principal de renderização.
* `config.json`: Controle central de design e caminhos de arquivos.
* `JSON/`: Perguntas em formato estruturado.
* `Fundos/`: Artes das cartas (Frente padrão e Versos específicos).
* `PDFs/`: Resultados finais (um arquivo por nível).
* `.gitignore`: Configurado para ignorar a pasta `venv/` e arquivos temporários do Python.

## ⚙️ Configuração (`config.json`)

O script é totalmente controlado pelo `config.json`. Veja os principais campos:

### `size` (Tamanho da Carta)
* Define as dimensões físicas em **décimos de milímetro**.
* Padrão: `width: 635` (63.5mm) e `height: 889` (88.9mm).

### `font` (Tipografia e Margens)
* `name`: Nome da fonte. O script busca por **Consolas** no Windows por padrão.
* `size`: Tamanho fixo da fonte (ex: `8`, `10`, `12`). **Nota**: O script não redimensiona o texto automaticamente para caber.
* `alignment`: Alinhamento (`left`, `center`, `right`, `justify`).
* `margen_top/down/left/right`: Margens em **pixels** baseadas na resolução da imagem de fundo.

### `background` e `questions`
* Mapeiam quais imagens e arquivos JSON serão usados para cada nível (Junior, Pleno, Sênior).

## 🎨 Detalhes Visuais
* **Fundo Branco**: O texto é desenhado sobre um retângulo branco sólido para garantir contraste.
* **Respostas**: A alternativa correta de cada pergunta é automaticamente formatada em **negrito**.
* **UTF-8**: Suporte total a acentos e caracteres especiais do Português (PT-BR).
* **Layout Lado a Lado**: Cada página do PDF contém a frente (esquerda) e o verso (direita), facilitando a impressão frente e verso ou corte manual.

## ⚠️ Observações Importantes
* Se o texto de uma pergunta "sumir", provavelmente o tamanho da fonte no `config.json` está muito grande para o espaço disponível. Diminua o valor de `size` e regere o arquivo.
