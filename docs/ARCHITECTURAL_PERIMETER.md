# Architectural Perimeter
## *Decisions We Refuse to Make*

---

## 1. Propósito do Perímetro

Este documento define os limites arquiteturais de Quasar.

Seu objetivo não é listar features ausentes. É declarar que certas direções são **fora do escopo por princípio**, independentemente de demanda, facilidade de implementação ou precedente em outras linguagens.

A distinção é importante:

- **"Não implementado"** significa: ainda não existe, poderia existir.
- **"Fora do perímetro"** significa: não será feito, por decisão consciente.

Este documento protege a segunda categoria.

Quando uma proposta entra em conflito com este perímetro, a resposta padrão é **não**. Não é necessário justificar novamente. A justificativa está aqui, uma vez, de forma permanente.

---

## 2. O Core Que Está Sendo Protegido

Quasar v1.9.0 possui:

- **Tipos primitivos explícitos**: int, float, bool, str
- **Structs como dados**: campos tipados, sem métodos, sem herança
- **Enums simples**: variantes nomeadas, sem payload, sem pattern matching
- **Funções globais**: tipagem explícita de parâmetros e retorno
- **Listas e dicionários tipados**: coleções homogêneas
- **Controle de fluxo simples**: if/else, while, for, return
- **Compilação para Python**: código gerado é Python válido e legível

Este core tem uma propriedade central: **previsibilidade total**.

O que você escreve é o que acontece. Não há dispatch implícito, coerção automática, herança oculta ou comportamento dependente de contexto.

Violar o core significa introduzir:
- Comportamento que depende de algo não visível no código
- Mecanismos que exigem conhecimento de sistema de tipos avançado
- Abstrações que escondem complexidade em vez de eliminá-la

---

## 3. Decisões Explicitamente Fora do Perímetro

### 3.1 Métodos em Structs

**Por que parece atraente**: agrupar dados e comportamento é padrão OO. Facilita descoberta de API. Parece organizado.

**Por que é rejeitado**: métodos em structs criam acoplamento implícito. O `self` torna mutação invisível. Encoraja hierarquias. Move Quasar em direção a OO sem os benefícios de uma linguagem OO completa.

**Conexão com identidade**: Quasar separa dados de comportamento. Structs são dados. Funções são comportamento. A separação é o ponto.

---

### 3.2 Herança / Hierarquias OO

**Por que parece atraente**: reutilização de código, polimorfismo, padrões clássicos de design.

**Por que é rejeitado**: herança cria acoplamento vertical. Mudanças em base afetam derivados. "Fragile base class problem" é real. Quasar não oferece mecanismos para mitigar isso, portanto não oferece herança.

**Conexão com identidade**: disciplina significa não oferecer ferramentas cujo uso correto é difícil de garantir.

---

### 3.3 Traits / Interfaces Nominais

**Por que parece atraente**: polimorfismo sem herança. Verificação em compile-time. Abstração de capacidades.

**Por que é rejeitado**: traits exigem sistema de tipos significativamente mais complexo. Interagem com generics, bounds, dispatch. Quasar compila para Python, onde duck typing já existe. Traits adicionariam formalismo em compile-time para algo que o runtime aceita naturalmente.

**Conexão com identidade**: disciplina não significa burocracia. Se o backend aceita, e o benefício é marginal, a complexidade não se justifica.

---

### 3.4 Generics

**Por que parece atraente**: abstração sobre tipos, coleções tipadas genericamente, funções reutilizáveis.

**Por que é rejeitado**: generics mudam fundamentalmente o sistema de tipos. Exigem inferência, bounds, variância. Cada feature futura precisa considerar interação com generics. O custo de manutenção é permanente e cumulativo.

**Conexão com identidade**: Quasar prefere tipos concretos e explícitos. A ausência de generics força clareza.

---

### 3.5 Pattern Matching Geral

**Por que parece atraente**: expressividade, elegância, exhaustiveness checking.

**Por que é rejeitado**: pattern matching geral é quase uma sub-linguagem. Guards, bindings, wildcards, or-patterns. Cada extensão parece natural após a anterior. O escopo cresce indefinidamente. If/else é simples e suficiente.

**Conexão com identidade**: Quasar escolhe um caminho e permanece nele. Pattern matching é caminho alternativo completo, não extensão.

---

### 3.6 Result / Either Como Modelo Central de Erro

**Por que parece atraente**: erros explícitos, sem exceções implícitas, tipo-checked.

**Por que é rejeitado**: Python usa exceções. Bibliotecas Python levantam exceções. Result criaria dois mundos: código Quasar "seguro" e código Python "inseguro". A fronteira seria dolorosa. A falsa sensação de segurança seria pior que nenhuma.

**Conexão com identidade**: Quasar usa Python como backend. Lutar contra o modelo de erro do backend é batalha perdida.

---

### 3.7 Inferência Automática de Tipos

**Por que parece atraente**: menos anotações, código mais limpo, ergonomia.

**Por que é rejeitado**: inferência muda a relação com anotações. Se inferência existe, anotações parecem opcionais. Mensagens de erro ficam menos localizadas. O que era explícito vira implícito.

**Conexão com identidade**: disciplina significa escrever o que você quer dizer. Tipos explícitos são documentação no código.

---

### 3.8 Operadores de Propagação de Erro (`?`)

**Por que parece atraente**: ergonomia para Result, reduz boilerplate.

**Por que é rejeitado**: `?` só faz sentido com Result. Result está fora do perímetro. Além disso, `?` esconde control flow. O que parece expressão pode sair da função.

**Conexão com identidade**: Quasar não esconde control flow. O que acontece é visível.

---

### 3.9 Sobrecarga de Operadores

**Por que parece atraente**: `a + b` pode significar concatenação, soma de vetores, merge de dicts.

**Por que é rejeitado**: `a + b` deveria significar uma coisa. Sobrecarga cria dependência de tipo para entender semântica. Código fica impossível de ler sem conhecer tipos.

**Conexão com identidade**: previsibilidade. Operadores têm semântica fixa.

---

### 3.10 Macros / Metaprogramação

**Por que parece atraente**: extensibilidade infinita, DSLs, eliminação de boilerplate.

**Por que é rejeitado**: macros criam linguagem dentro da linguagem. Erros são incompreensíveis. Código gerado é invisível. Debugging é pesadelo.

**Conexão com identidade**: o que você escreve é o que acontece. Macros quebram isso fundamentalmente.

---

### 3.11 Null / Nil

**Por que parece atraente**: representar ausência de valor de forma simples.

**Por que é rejeitado**: null é fonte prolífica de bugs. "Billion dollar mistake". Quasar não tem null. Não terá.

**Conexão com identidade**: disciplina significa não oferecer armas carregadas.

---

## 4. Argumentos Que Não São Aceitos

Os seguintes tipos de justificativa **não são válidos** para desafiar este perímetro:

| Argumento | Por que inválido |
|-----------|------------------|
| "Outras linguagens têm" | Quasar não é outras linguagens |
| "É mais elegante" | Elegância não é critério |
| "É fácil de implementar" | Facilidade não justifica existência |
| "Usuários podem querer" | Especulação não é evidência |
| "Completa a linguagem" | Completude é conceito externo |
| "Seria mais produtivo" | Produtividade não é valor central |
| "Python permite" | Quasar não tenta replicar Python |
| "É moderno" | Modernidade não é critério |

---

## 5. Quando Este Documento Pode Ser Desafiado

Este documento não é eterno. Mas desafiá-lo requer:

1. **Código real, existente, que não pode ser escrito** — não hipotético
2. **Múltiplas instâncias independentes do mesmo obstáculo** — padrão, não caso isolado
3. **Demonstração de que a solução proposta impõe disciplina** — não apenas conveniência
4. **Avaliação completa de irreversibilidade** — o que não pode ser desfeito depois
5. **Integração coerente com o core existente** — não exceção, mas extensão natural

Exceções são raras. Exceções são perigosas. Exceções criam precedentes.

A resposta padrão a desafios é: **não**.

---

## 6. Encerramento

Limites não são fraqueza. São escolha.

Quasar não tenta ter todas as features. Tenta ter as features certas, bem integradas, previsíveis.

O perímetro existe para proteger isso. Dizer "não" é mais difícil do que dizer "sim". Este documento torna o "não" explícito, justificado, e permanente.

Quasar prefere ser **pequena e correta** a **grande e incoerente**.

Esse é o perímetro. Ele não se move facilmente.

---

**Versão de referência**: v1.9.0 "Prism"
**Data**: 2026-01-16
**Estado**: FROZEN
