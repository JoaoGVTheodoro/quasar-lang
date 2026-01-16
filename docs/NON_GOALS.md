# Quasar — Limites Explícitos de Design

Este documento define **o que Quasar não tenta ser**.
Ausência de feature **não é dívida técnica por padrão**.

Este arquivo existe para **reduzir pressão por crescimento incoerente** e servir como **critério de veto** para propostas futuras.

---

## 1. O Que Quasar Não É

Quasar **não** tenta ser:

* Um "Python melhorado"
* Um substituto para Python
* Rust rodando em Python
* Uma linguagem de tipagem máxima
* Uma linguagem de ergonomia máxima
* Uma linguagem de expressividade total
* Uma linguagem orientada a objetos completa
* Um experimento acadêmico de tipos
* Uma linguagem "com tudo que as outras têm"

Comparações com outras linguagens **não são justificativa suficiente** para adição de features.

---

## 2. O Que Quasar Não Prioriza

Quasar **não prioriza**, por si só:

* Conveniência sobre disciplina
* Sintaxe mais curta se reduzir clareza
* Features "esperadas" por tradição cultural
* Completeness por simetria ("se tem X, deveria ter Y")
* Acomodar todos os estilos de programação
* Crescimento por pressão externa
* Antecipação de necessidades futuras
* Preparação especulativa de código

---

## 3. Ausências Não São Falhas Automáticas

A ausência de uma feature **não implica**:

* Que a linguagem está incompleta
* Que a feature "virá depois"
* Que há um roadmap oculto
* Que o design é provisório
* Que o problema não foi considerado

Toda ausência é considerada **intencional até prova em contrário**.

---

## 4. Features Explicitamente Fora de Escopo (Até Nova Evidência)

Sem evidência concreta de necessidade, Quasar **não assume**:

* Métodos em structs
* Herança ou subtipagem nominal
* Traits / interfaces
* Pattern matching geral
* Result como modelo obrigatório de erro
* Operadores mágicos de propagação (`?`)
* Inferência de tipos global
* Null / nil implícito
* Metaprogramação (macros)
* Sobrecarga de operadores
* Dispatch implícito por tipo

Esta lista **não é promessa de nunca**, mas é **veto por padrão**.

---

## 5. Critério Para Revisar Um Non-Goal

Um item deste documento **só pode ser questionado** se houver:

* Código real existente que não pode ser escrito hoje
* Evidência repetida de obstáculo prático, não estético
* Demonstração clara de que a feature impõe disciplina real
* Integração coerente com o sistema atual
* Avaliação explícita de irreversibilidade

"Seria mais bonito", "outras linguagens têm" e "pode ser útil"
**não são critérios válidos**.

---

## 6. Função Deste Documento

Este documento existe para:

* Proteger coerência arquitetural
* Reduzir decisões reativas
* Preservar opções futuras
* Tornar o "não" explícito e justificável
* Evitar crescimento acidental

Quasar cresce **quando a realidade força**, não quando a comparação sugere.

---

## 7. Estado

Documento ativo.
Revisão apenas mediante evidência concreta.
Silêncio é escolha válida.

Versão de referência: v1.9.0 "Prism"
Data: 2026-01-16
