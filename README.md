# Projeto-tematico1
# Sistema de Manutenção Hospitalar

## Descrição
O **Sistema de Manutenção Hospitalar** é uma aplicação desktop em **Python** com interface gráfica **Tkinter** e tema **TTKBootstrap**, desenvolvido para monitorar e gerenciar equipamentos, ordens de serviço (OS) e planejamentos hospitalares.  

O sistema permite acompanhar KPIs, visualizar gráficos de desempenho, pesquisar e gerenciar OS, cadastrar usuários com diferentes perfis e gerar relatórios em PDF.

---

## Funcionalidades

### Painel de Controle
O **Painel** oferece uma visão geral do sistema, permitindo acompanhar indicadores-chave e visualizar gráficos:

#### KPIs
- **Equipamentos**: total e disponíveis.
- **Ordens Abertas**: quantidade de OS em andamento.
- **Ordens Atrasadas**: OS que não foram concluídas no prazo.
- **Planejamentos**: quantidade de planejamentos ativos.

#### Gráficos
- **Distribuição de Equipamentos**: gráfico de pizza mostrando disponíveis x em manutenção.
- **Ordens por Status**: gráfico de barras mostrando quantidade de OS por status (Pendente, Em análise, Concluída, etc.).
- **Ordens por Prioridade**: gráfico de barras mostrando quantidade de OS por criticidade.

#### Tabela de OS do Mês
- Lista todas as ordens de serviço com:
  - ID da OS
  - Tipo (Preventiva, Corretiva, Planejada)
  - Equipamento
  - Responsável
  - Data Prevista
  - Prioridade
  - Status
- Destaque visual:
  - Linhas alternadas para melhor leitura
  - OS atrasadas em vermelho
- Barra de rolagem integrada para monitoramento em qualquer tamanho de tela
- Atualização automática ao salvar ou gerar novas OS

#### Relatórios
- Geração de **relatórios PDF por setor** usando `reportlab` ou utilitário `RelatorioPDFUtil`.
- Inclui gráficos resumidos e tabelas de OS.

---

### Aba Usuários
- Cadastro e edição de usuários:
  - Nome, Login (E-mail), Senha, Contato, Perfil e Status
- Perfis:
  - Administrador: acesso total
  - Gestor: acesso a cadastros e relatórios
  - Técnico / Usuário: acesso limitado
- Pesquisa dinâmica de usuários
- Edição e exclusão com confirmação
- Tabela com cores alternadas para melhor visualização

---

## Estrutura do Projeto

├── src/
│ ├── dao/ # DAO e acesso ao banco de dados
│ │ ├── manutencao_dao.py
│ │ ├── equipamento_dao.py
│ │ ├── planejamento_dao.py
│ │ └── usuario_dao.py
│ ├── model/ # Modelos de dados
│ │ ├── manutencao.py
│ │ ├── equipamento.py
│ │ ├── planejamento.py
│ │ ├── usuario.py
│ │ └── relatorio.py # Utilitário de PDF
│ └── ui/ # Interface gráfica
│ ├── painel.py # Aba Painel
│ └── usuarios.py # Aba Usuários
├── image/ # Ícones e imagens
│ └── favicon.png
├── main.py # Script principal para iniciar o sistema
└── README.md


---

## Estrutura das Tabelas (Banco de Dados)

| Tabela           | Campos Principais                                    | Descrição |
|-----------------|-----------------------------------------------------|-----------|
| equipamentos     | id, nome, status, setor                              | Lista de equipamentos do hospital |
| manutencao       | id, planejamento_id, data_prevista, status, prioridade | Ordens de serviço vinculadas a um planejamento |
| planejamento     | id, tipo, equipamento_id, responsavel_id, data_inicial, dias_previstos, last_gerada, criticidade | Planejamentos de manutenção preventiva/corretiva |
| usuarios         | id, nome, login, senha, contato, perfil, status     | Usuários do sistema com diferentes perfis |

---

## Requisitos

- Python 3.9+
- Pacotes:
  - `ttkbootstrap`
  - `matplotlib`
  - `Pillow`
  - `reportlab` (opcional para PDF)
- Banco de dados SQLite ou outro compatível com SQLAlchemy

Instalação de dependências:
```bash
pip install ttkbootstrap matplotlib pillow reportlab


Fluxo do Sistema

Login (caso implementado): validação de usuário.

Painel: exibe KPIs e gráficos.

Tabela de OS:

Atualizada automaticamente

Barra de rolagem integrada

Destaque de OS atrasadas

Usuários:

Cadastro, edição e exclusão

Perfis controlam permissões

Relatórios:

PDF por setor

Inclui dados de equipamentos, OS e gráficos

Funcionalidades Avançadas

Barra de rolagem única para painel de OS e gráficos

Tabelas com cores alternadas e tags de destaque

Cálculo automático de próximas datas de OS preventivas

Atualização dinâmica de KPIs e gráficos

Compatível com múltiplos setups e diferentes resoluções de tela


