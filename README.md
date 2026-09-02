# LEIAME - Busca Unificada GIL/GDI

## 1. Apresentacao

O **Busca Unificada**, desenvolvido para a **Gerencia de Informacao Legislativa - GIL/GDI**, permite realizar pesquisas integradas em:

- normas juridicas;
- proposicoes e seus textos/documentos;
- pronunciamentos.

O programa oferece dois modos de pesquisa:

- **Busca textual** - localiza palavras, expressoes exatas, truncamentos e combinacoes de termos;
- **Busca semantica** - recupera conteudos relacionados ao significado da consulta, mesmo quando nao utilizam exatamente os mesmos termos pesquisados.

Os resultados das diferentes fontes sao apresentados de forma unificada e agrupados pelo documento principal.

---

## 2. Como iniciar o programa

Para o uso normal, execute:

```text
Iniciar Busca.vbs
```

Esse e o iniciador recomendado. Ele abre somente a interface grafica do Busca Unificada, **sem manter uma janela do Prompt de Comando (CMD) aberta**.

O iniciador utiliza o `pythonw.exe` existente no Python portatil fornecido com o pacote e, portanto, nao depende de uma instalacao externa do Python para iniciar o aplicativo.

### Atalho opcional

Se desejar, crie um atalho do arquivo `Iniciar Busca.vbs` na Area de Trabalho e utilize esse atalho para abrir o programa.

### Arquivo `Iniciar Busca.bat`

O arquivo:

```text
Iniciar Busca.bat
```

tambem pode ser utilizado. Ele apenas aciona o iniciador grafico `Iniciar Busca.vbs` e encerra em seguida. Dependendo da configuracao do Windows, uma janela do CMD pode aparecer rapidamente durante a abertura, mas nao permanecera aberta.

### Modo de diagnostico

Caso o aplicativo apresente erro ao iniciar e seja necessario visualizar mensagens tecnicas, utilize:

```text
Iniciar Busca - Diagnostico.bat
```

Nesse modo, a janela do CMD permanece disponivel durante a execucao e exibe eventuais mensagens de erro do Python. Esse arquivo deve ser usado apenas para diagnostico e manutencao.

---

## 3. Estrutura esperada do pacote

A estrutura utilizada pelo programa e, em linhas gerais:

```text
busca_completa/
|
|-- Iniciar Busca.vbs
|-- Iniciar Busca.bat
|-- Iniciar Busca - Diagnostico.bat
|-- LEIAME.md
|
`-- sistema/
    |-- app/
    |   `-- app.py
    |
    |-- assets/
    |   `-- logo.png
    |
    |-- dados/
    |   |-- banco_textos_normas_catalogo.db
    |   |-- banco_textos_proposicoes_catalogo.db
    |   |-- pronunciamentos.db
    |   |-- indice_busca_unificada/
    |   `-- indice_semantico_silegis.db
    |
    |-- modelo/
    |   `-- modelo_semantico_multilingual_minilm/
    |
    `-- python/
        `-- python_portatil/
            `-- WPy64-31190b5/
                `-- python-3.11.9.amd64/
                    |-- python.exe
                    `-- pythonw.exe
```

**Importante:** preserve os nomes e a posicao das pastas e arquivos utilizados pelo programa.

---

## 4. Python e dependencias

O pacote utiliza Python 3.11 portatil. O iniciador principal procura o executavel em:

```text
sistema\python\python_portatil\WPy64-31190b5\python-3.11.9.amd64\pythonw.exe
```

As principais dependencias do programa sao:

```text
whoosh
numpy
sentence-transformers
torch
```

Em uma instalacao manual do Python 3.11, elas podem ser instaladas com:

```text
py -3.11 -m pip install whoosh numpy sentence-transformers torch
```

No pacote portatil ja preparado para o aplicativo, essas dependencias devem acompanhar o ambiente Python fornecido.

---

## 5. Modelo da busca semantica

A pasta completa:

```text
modelo_semantico_multilingual_minilm
```

deve estar localizada em:

```text
sistema\modelo\
```

A busca semantica e processada localmente a partir desse modelo.

---

## 6. Modos de pesquisa

Na parte superior da area de pesquisa existem dois controles para alternar entre:

- **Busca textual**;
- **Busca semantica**.

A busca textual e indicada para localizar palavras e expressoes efetivamente presentes nos documentos. A busca semantica e indicada para localizar documentos conceitualmente relacionados ao assunto pesquisado.

---

## 7. Busca textual

### Pesquisa simples

Digite normalmente o termo desejado.

Exemplo:

```text
meio ambiente
```

### Expressao exata

Utilize aspas:

```text
"pagamento por servicos ambientais"
```

### Truncamento

O caractere `*` permite pesquisar diferentes terminacoes:

```text
ambient*
```

Tambem e possivel pesquisar uma sequencia em qualquer posicao da palavra:

```text
*ambient*
```

Esse tipo de consulta pode ser mais lento.

O caractere `$` funciona como atalho para truncamento ao final:

```text
ambient$
```

equivale a:

```text
ambient*
```

### Curinga de um caractere

O caractere `?` representa um unico caractere:

```text
constitui?ao
```

### Truncamento dentro de expressao

```text
"servic* ambient*"
```

### Operadores booleanos

A busca textual aceita:

```text
AND
OR
NOT
```

Exemplos:

```text
educacao AND saude
```

```text
"meio ambiente" OR sustentabilidade
```

```text
tributacao NOT ICMS
```

---

## 8. Busca semantica

A busca semantica procura conteudos relacionados conceitualmente a consulta.

Para utiliza-la:

1. selecione o modo **Busca semantica**;
2. informe a consulta;
3. ajuste, se necessario, as fontes, os tipos documentais e os campos;
4. execute a pesquisa.

O programa transforma a consulta em um vetor semantico e o compara com os trechos previamente indexados.

A busca semantica depende da existencia do modelo semantico local e do indice semantico consolidado.

---

## 9. Fontes de pesquisa

Podem ser selecionadas uma ou mais fontes:

- **Normas**;
- **Proposicoes**;
- **Pronunciamentos**.

Caso nenhuma fonte seja selecionada, o programa solicitara a selecao de pelo menos uma.

---

## 10. Tipos documentais

Para normas e proposicoes, e possivel restringir a pesquisa aos tipos documentais desejados.

Os seletores permitem:

- marcar todos;
- desmarcar todos;
- selecionar tipos individualmente.

Nos tipos de proposicao, a identificacao e apresentada pela respectiva sigla.

---

## 11. Campos pesquisaveis

A pesquisa pode ser limitada aos seguintes campos:

- **Ementa**;
- **Resumo**;
- **Indexacao**;
- **Assunto**;
- **Autoria**;
- **Texto**.

E possivel pesquisar em todos os campos ou selecionar apenas os de interesse.

---

## 12. Resultados

Os resultados sao agrupados pelo documento principal.

A tabela apresenta informacoes para identificacao dos documentos e, quando disponivel, acesso ao Portal da ALMG.

Os resultados podem ser ordenados clicando nos cabecalhos da tabela.

---

## 13. Painel de detalhes

Ao selecionar um resultado, o programa apresenta informacoes do documento, que podem incluir:

- identificacao;
- fonte;
- tipo;
- numero;
- ano;
- data;
- metadados catalograficos;
- locais ou campos em que a pesquisa foi encontrada.

---

## 14. Abertura dos textos

Os textos integrais extensos nao sao reproduzidos integralmente no painel lateral.

Quando necessario, o programa recupera o texto diretamente do respectivo banco SQLite e pode gerar uma pagina HTML local com:

- ocorrencias destacadas;
- posicionamento na primeira ocorrencia;
- navegacao para a ocorrencia anterior;
- navegacao para a proxima ocorrencia;
- contador de ocorrencias.

---

## 15. Portal da ALMG

Para normas e proposicoes, o aplicativo procura utilizar URLs publicas do **Portal da Assembleia Legislativa do Estado de Minas Gerais - ALMG**.

Quando houver endereco disponivel, o usuario podera acessar diretamente a pagina correspondente no Portal.

---

## 16. Atualizacao dos indices

O botao:

```text
ATUALIZAR INDICES
```

executa a manutencao incremental dos indices de pesquisa.

A atualizacao procura:

- documentos novos;
- documentos modificados desde a ultima sincronizacao.

Documentos inalterados sao preservados e nao precisam ser integralmente reprocessados.

Para documentos modificados, as unidades antigas correspondentes sao substituidas pelas versoes atuais. Na busca semantica, somente os conteudos novos ou alterados precisam ter seus embeddings recalculados.

### Importante

A funcao **Atualizar indices nao cria os indices consolidados do zero**.

Ela pressupoe a existencia previa do indice textual e do indice semantico consolidados.

Se um desses indices estiver ausente ou incompatível, a atualizacao e interrompida para evitar a reconstrucao ou substituicao indevida do acervo existente.

---

## 17. Bancos de dados

O programa utiliza:

```text
banco_textos_normas_catalogo.db
banco_textos_proposicoes_catalogo.db
pronunciamentos.db
```

Os bancos de origem sao acessados em modo somente leitura nas operacoes de consulta.

Eles devem permanecer em:

```text
sistema\dados\
```

---

## 18. Indices

### Indice textual

```text
sistema\dados\indice_busca_unificada\
```

### Indice semantico

```text
sistema\dados\indice_semantico_silegis.db
```

Nao exclua esses indices para tentar solucionar problemas de atualizacao. Esta versao foi desenvolvida para preservar e atualizar incrementalmente indices consolidados ja existentes.

---

## 19. Problemas comuns

### O programa nao abre pelo `Iniciar Busca.vbs`

Execute:

```text
Iniciar Busca - Diagnostico.bat
```

para visualizar eventuais mensagens de erro.

### Python portatil nao encontrado

Confirme a existencia de:

```text
sistema\python\python_portatil\WPy64-31190b5\python-3.11.9.amd64\pythonw.exe
```

No modo de diagnostico, confirme tambem:

```text
sistema\python\python_portatil\WPy64-31190b5\python-3.11.9.amd64\python.exe
```

### `app.py` nao encontrado

Confirme:

```text
sistema\app\app.py
```

### Indice textual consolidado nao encontrado

Verifique:

```text
sistema\dados\indice_busca_unificada\
```

### Indice semantico consolidado nao encontrado

Verifique:

```text
sistema\dados\indice_semantico_silegis.db
```

### Modelo semantico local nao encontrado

Verifique:

```text
sistema\modelo\modelo_semantico_multilingual_minilm\
```

### Nenhum resultado

Confira:

- a expressao pesquisada;
- o modo de busca selecionado;
- as fontes marcadas;
- os tipos de norma ou proposicao;
- os campos selecionados.

---

## 20. Recomendacoes de uso

- Para o uso cotidiano, abra sempre pelo **`Iniciar Busca.vbs`**.
- Utilize **`Iniciar Busca - Diagnostico.bat`** somente quando precisar investigar erros.
- Para localizar palavra ou expressao conhecida, prefira a busca textual.
- Para procurar documentos relacionados a uma ideia ou assunto, utilize a busca semantica.
- Use os filtros de fonte, tipo e campo para reduzir o universo pesquisado.
- Evite `*termo*` desnecessariamente, pois esse tipo de truncamento pode tornar a consulta mais lenta.
- Preserve a estrutura original das pastas.
- Antes de substituir bancos ou indices, mantenha uma copia de seguranca do pacote funcional.
- Utilize **Atualizar indices** apos a atualizacao das bases de dados para incorporar documentos novos ou modificados.

---

## 21. Resumo rapido

### Para pesquisar

1. Execute **`Iniciar Busca.vbs`**.
2. Escolha busca textual ou busca semantica.
3. Digite a consulta.
4. Se necessario, ajuste fontes, tipos e campos.
5. Execute a pesquisa.
6. Selecione um resultado para visualizar os detalhes.
7. Utilize os controles disponiveis para abrir o texto ou acessar o Portal da ALMG.

### Se o programa nao abrir

1. Execute **`Iniciar Busca - Diagnostico.bat`**.
2. Leia a mensagem exibida no CMD.
3. Verifique principalmente os caminhos do Python portatil, do `app.py`, dos bancos, dos indices e do modelo semantico.

### Para atualizar o conteudo pesquisavel

1. Certifique-se de que os bancos atualizados estao em `sistema\dados\`.
2. Abra o programa pelo `Iniciar Busca.vbs`.
3. Clique em **ATUALIZAR INDICES**.
4. Confirme a operacao.
5. Aguarde a conclusao da atualizacao incremental.

A atualizacao preservara os documentos inalterados e processara apenas itens novos ou modificados.
