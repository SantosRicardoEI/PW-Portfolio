# Making Of — Ficha 6

## Estado e limite do trabalho

Esta versão cobre a modelação e a configuração do Django Admin até ao final da
secção 3. Não inclui páginas públicas, dados fictícios persistentes, importação
do JSON de TFCs, APIs ou scraping. A modelação será revista quando forem
observados os dados reais das secções seguintes.

## Evolução do modelo

### Versão 1 — identificação das entidades

Foram identificadas as entidades pedidas: Licenciatura, Unidade Curricular,
Projeto, Tecnologia, TFC, Competência, Formação e Making Of.

### Versão 2 — normalização das relações

Foi criada `Docente` como entidade adicional. Um docente pode participar em
várias UCs e orientar vários TFCs, evitando repetir nome, contacto e página
pessoal. As fotografias do processo foram separadas em `EvidenciaMakingOf`,
permitindo várias imagens ordenadas por entrada do diário.

### Versão 3 — implementação incremental

Os modelos foram implementados em três migrações: núcleo académico; projetos e
percurso pessoal; diário Making Of. A separação permite reconhecer a evolução
da base de dados e localizar mais facilmente uma futura alteração.

## Diagrama entidade-relação digital

Este diagrama é um apoio à passagem do modelo para papel. Não substitui a
fotografia obrigatória do DER desenhado pelo aluno.

```mermaid
erDiagram
    LICENCIATURA ||--o{ UNIDADE_CURRICULAR : inclui
    DOCENTE }o--o{ UNIDADE_CURRICULAR : leciona
    UNIDADE_CURRICULAR }o--o{ PROJETO : enquadra
    TECNOLOGIA }o--o{ PROJETO : utiliza
    DOCENTE }o--o{ TFC : orienta
    COMPETENCIA }o--o{ PROJETO : demonstra
    COMPETENCIA }o--o{ TECNOLOGIA : aplica
    FORMACAO }o--o{ COMPETENCIA : desenvolve
    MAKING_OF ||--o{ EVIDENCIA_MAKING_OF : contém
    ENTIDADE_PORTFOLIO o|--o{ MAKING_OF : documentada_por
```

`ENTIDADE_PORTFOLIO` representa conceptualmente qualquer um dos modelos da
aplicação. Em Django, esta ligação é implementada com `ContentType` e um ID, o
que permite documentar entidades diferentes sem criar uma coluna opcional para
cada uma.

## Decisões e justificações por entidade

### Licenciatura

1. O código institucional é único, porque será a referência estável usada pela
   futura API; para LEI está preparado o código `260`.
2. Duração e ECTS são valores separados da descrição para poderem ser filtrados
   e validados, em vez de ficarem escondidos em texto livre.

### Docente — entidade adicional

1. Foi criada uma entidade própria porque o mesmo docente pode lecionar várias
   UCs e orientar vários TFCs.
2. A página pessoal é obrigatória, pois a ficha pede explicitamente a ligação
   ao perfil da Universidade Lusófona; email e fotografia são opcionais.

### Unidade Curricular

1. Cada UC pertence a uma licenciatura, mas pode ter vários docentes, pelo que
   foram usadas relações `ForeignKey` e `ManyToManyField`, respetivamente.
2. Código, ano, semestre e ECTS são estruturados para permitirem pesquisa e
   filtros no Admin; a imagem é obrigatória por requisito do enunciado.

### Projeto

1. A relação com UCs é muitos-para-muitos porque um projeto pode combinar
   conhecimentos de mais de uma disciplina.
2. GitHub é obrigatório por ser importante para entrevistas; demo e vídeo são
   opcionais porque nem todos os projetos possuem esses recursos.

### Tecnologia

1. Categoria e nível usam escolhas fechadas para evitar variações como
   “framework”, “Framework” e “framework web” nos filtros.
2. O interesse usa uma escala validada de 1 a 5; logo e website oficial são
   obrigatórios para caracterizar visualmente e referenciar a tecnologia.

### TFC

1. O título, resumo, ano, estudante e área foram escolhidos como núcleo inicial,
   sem tentar antecipar todas as propriedades do JSON ainda não analisado.
2. Orientadores são relacionados com `Docente`; interesse e destaque registam
   a avaliação pessoal pedida sem alterar os dados objetivos do TFC.

### Competência

1. Categoria e nível refletem a forma habitual de organizar competências num
   CV e permitem filtros consistentes.
2. As relações com projetos e tecnologias funcionam como evidência concreta de
   onde cada competência foi aplicada.

### Formação

1. Datas de início e fim permitem ordenação cronológica; `em_curso` representa
   formações ainda sem data final.
2. Certificado e URL são opcionais porque nem todas as formações fornecem ambos;
   competências relacionam a formação com resultados adquiridos.

### Making Of

1. Decisões, erros, correções e uso de IA possuem campos separados para que o
   processo não fique reduzido a uma descrição genérica.
2. Foi usada uma relação genérica validada, permitindo associar uma entrada a
   qualquer entidade do portfólio sem dezenas de relações opcionais.

### Evidência Making Of

1. A evidência é um modelo separado para permitir várias fotografias em cada
   entrada do diário.
2. Legenda e ordem são obrigatórias; a combinação entrada/ordem é única para
   manter uma sequência inequívoca.

## Problemas identificados e correções

- O projeto Django gera um ficheiro `views.py`, mas esta fase é exclusivamente
  administrativa. O ficheiro foi removido e só existe a rota `/admin/`.
- A configuração inicial gera uma chave secreta dentro de `settings.py`. Foi
  substituída por leitura de variável de ambiente, com valor local não secreto.
- Uma data final de formação poderia ser anterior à data inicial. Foi adicionada
  validação no modelo para impedir esse estado.
- Uma ligação genérica do Making Of poderia guardar apenas o tipo, apenas o ID
  ou um ID inexistente. A validação exige o par completo e confirma a existência
  do objeto.

## Utilização de inteligência artificial

Foi utilizado o Codex como apoio para interpretar o enunciado, propor a primeira
modelação, implementar os modelos e o Admin e preparar a documentação.
As decisões continuam a ter de ser revistas e explicadas pelo aluno durante a
defesa. A IA não consultou nem inventou dados pessoais, TFCs ou conteúdos das
APIs, e não produziu fotografias falsas de trabalho em papel.

## Evidências em papel ainda necessárias

Antes da submissão, desenhar e fotografar:

1. Lista inicial de entidades e atributos.
2. Primeira versão do DER.
3. Versão revista com `Docente`, relações muitos-para-muitos e Making Of.
4. Apontamentos sobre pelo menos uma alteração ou correção feita pelo aluno.

Guardar os ficheiros reais em `media/makingof/` seguindo o guia dessa pasta e
substituir esta secção por referências às fotografias adicionadas.

## Evolução após análise do JSON de TFCs

Ao analisar `data/tfcs.json`, a modelação inicial revelou-se insuficiente: um
TFC pode possuir vários alunos, orientadores, cursos, áreas, palavras-chave e
tecnologias. Os campos singulares de estudante e área foram por isso
substituídos por relações muitos-para-muitos.

Foram criadas as entidades `Aluno`, `AreaTFC` e `PalavraChaveTFC`. As entidades
`Licenciatura`, `Docente` e `Tecnologia` foram reutilizadas, evitando guardar o
mesmo nome repetidamente em cada TFC. Os atributos que não existem no JSON,
como o website de uma tecnologia ou a página pessoal de um docente, passaram a
poder ficar por completar no Admin em vez de receberem valores inventados.

O email, o estado, a parceria e as ligações externas permanecem no próprio TFC
porque caracterizam aquela ocorrência concreta. A parceria ficou em texto, uma
vez que alguns valores do ficheiro agregam várias organizações e não existe uma
separação suficientemente segura entre elas.

O carregamento foi implementado com o ORM Django e dentro de uma transação. A
combinação de título, ano e email identifica cada TFC, permitindo repetir o
script sem criar duplicados. Uma nova execução atualiza os dados objetivos e as
relações, mas preserva as classificações pessoais de interesse e destaque.

## Evolução após análise das APIs de curso e UCs

As APIs académicas forneceram uma descrição geral de LEI, o plano com 31 UCs e
o detalhe pedagógico de cada disciplina. A informação portuguesa foi integrada
na aplicação e as respostas PT e ENG foram guardadas no repositório para manter
os dados originais e permitir uma eventual utilização bilingue no futuro.

O modelo `Licenciatura` passou a guardar objetivos, competências, saídas
profissionais, condições de acesso, grau, área científica, modalidade e estado
de acreditação. Foi também criada uma relação com os docentes apresentados pela
API como pertencentes ao corpo docente do curso.

O modelo `UnidadeCurricular` foi enriquecido com apresentação, objetivos,
competências, programa, metodologia, avaliação, bibliografia, natureza, idioma,
horas de contacto e ano letivo. O semestre passou de um número para as opções
`S1`, `S2` e `A`, pois o Trabalho Final de Curso é anual. A imagem tornou-se
opcional porque a API não fornece imagens; estas terão de ser adicionadas
manualmente no Admin.

A lista de 51 docentes do curso não indica quais lecionam cada UC. Por esse
motivo, os docentes foram associados a LEI, mas não foram criadas relações
UC–Docente sem evidência. As páginas pessoais também permanecem por completar,
uma vez que não são fornecidas por estas APIs.

### Erro encontrado e correção

No primeiro carregamento, as horas de contacto chegaram da API como números de
ponto flutuante. A representação binária introduziu casas decimais adicionais e
foi rejeitada pelo `DecimalField`. Como o carregamento decorria numa transação,
nada ficou parcialmente guardado. A correção consistiu em converter o valor
para `Decimal` e quantizá-lo explicitamente para uma casa decimal antes de o
entregar ao ORM.
