# Sistema Web de Rateio de Conta de Energia - Condomínio Black Falcon

## 1. Visão Geral

Este é um sistema web desenvolvido para o Condomínio Black Falcon com o objetivo de automatizar e simplificar o processo de rateio da conta de energia elétrica para o síndico, Fábio. O sistema permite:

* **Lançamento de Contas Mensais:** O síndico insere o valor total da conta de energia e as leituras atuais dos medidores de cada uma das 10 casas. Para o Salão de Festas, o consumo é inserido diretamente.
* **Cálculo Automático de Consumo e Custos:**
    * Para as casas, o sistema calcula o consumo individual subtraindo a última leitura registrada da leitura atual informada.
    * O custo por kWh é calculado com base no consumo total interno (casas + salão) e o valor total da conta.
    * O custo do Salão de Festas é rateado igualmente entre as 10 casas.
* **Relatórios Detalhados:** Após o cálculo, um relatório claro é gerado, mostrando para cada casa: leitura anterior, leitura atual, consumo calculado, custo base, cota do salão e valor final a pagar.
* **Histórico de Rateios:** Todos os rateios são armazenados, permitindo consulta a relatórios de meses anteriores.
* **Interface Profissional:** O sistema possui uma interface de usuário intuitiva, responsiva e com um design moderno e profissional, utilizando uma paleta de cores sóbria (azul marinho e dourado/bronze como acentos) e tipografia elegante para facilitar o uso.

O foco principal é fornecer uma ferramenta eficiente, transparente e que reduza a chance de erros manuais, economizando tempo para o síndico.

## 2. Tecnologias Utilizadas

* **Backend:** Python com Flask
* **Frontend:** HTML5, CSS3 (Bootstrap 5 + Estilos Personalizados), JavaScript (para funcionalidades do Bootstrap)
* **Banco de Dados:** SQLite
* **Fontes:** Montserrat e Open Sans (via Google Fonts)

## 3. Estrutura de Pastas do Projeto

condominio_black_falcon/
|-- app.py                   # Aplicação Flask principal
|-- database.py              # Funções de interação com o BD
|-- schema.sql               # Schema do banco de dados
|-- data.sql                 # Dados iniciais (unidades e leituras iniciais)
|-- requirements.txt         # Dependências Python
|-- static/
|   |-- css/
|       |-- style.css        # Estilos CSS personalizados
|-- templates/
|   |-- layout.html          # Template base
|   |-- dashboard.html       # Página inicial
|   |-- novo_rateio.html     # Formulário para novo rateio
|   |-- ver_rateio.html      # Detalhes de um rateio
|   |-- historico.html       # Lista de rateios passados
|-- instance/                # Pasta para o arquivo do BD SQLite (criada automaticamente)
|   |-- condominio.db
|-- README.md                # Este arquivo

## 4. Configuração do Ambiente de Desenvolvimento

**Pré-requisitos:**
* Python 3.7 ou superior
* Pip (gerenciador de pacotes Python)

**Passos para Configuração:**

1.  **Clone o repositório ou crie os arquivos:**
    Certifique-se de que todos os arquivos e pastas do projeto estão na estrutura correta conforme descrito acima.

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    No terminal, navegue até a pasta raiz do projeto (`condominio_black_falcon`):
    ```bash
    python -m venv venv
    ```
    Ative o ambiente:
    * No Windows: `venv\Scripts\activate`
    * No macOS/Linux: `source venv/bin/activate`

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicialize o Banco de Dados:**
    Este comando criará o arquivo `condominio.db` na pasta `instance` (que também será criada se não existir), executará o `schema.sql` para criar as tabelas e o `data.sql` para popular as unidades com suas leituras iniciais.
    ```bash
    flask init-db
    ```
    Você deverá ver a mensagem "Banco de dados inicializado." no terminal.

## 5. Como Executar o Sistema

Com o ambiente virtual ativado e o banco de dados inicializado:

1.  Execute a aplicação Flask:
    ```bash
    flask run
    ```
    Ou, como alternativa, se o `if __name__ == '__main__':` estiver configurado em `app.py`:
    ```bash
    python app.py
    ```
2.  Abra seu navegador e acesse o endereço fornecido pelo Flask (geralmente `http://127.0.0.1:5000`).

## 6. Usando o Sistema

* **Dashboard:** A página inicial apresenta uma visão geral e links rápidos para as principais funcionalidades.
* **Lançar Novo Rateio:**
    1.  No menu, clique em "Novo Rateio".
    2.  Preencha o "Mês de Referência", "Ano de Referência" e o "Valor Total da Conta (R$)".
    3.  Para cada **casa**, insira a "Leitura Atual do Medidor (kWh)". A leitura anterior registrada no sistema será exibida como uma dica. O sistema calculará automaticamente o consumo (`Leitura Atual - Leitura Anterior`).
    4.  Para o **Salão de Festas**, insira o "Consumo Total (kWh)" diretamente.
    5.  Clique em "Calcular e Salvar Rateio".
* **Visualizar Detalhes do Rateio:**
    * Após salvar um novo rateio, você será redirecionado para a tela de visualização detalhada.
    * No histórico, clique em "Ver" ao lado de um rateio para acessar seus detalhes.
    * O relatório exibe:
        * Dados gerais da conta (mês/ano, valor total, consumo total interno, custo por kWh).
        * Detalhes do Salão de Festas (consumo informado, custo total, cota por casa).
        * Para cada casa: Leitura Anterior, Leitura Atual, Consumo Calculado, Custo Base, Cota do Salão e Valor Final a Pagar.
        * Soma de verificação para garantir que os valores batem com a conta total.
* **Histórico de Rateios:**
    * Acesse "Histórico" no menu para ver uma lista de todos os rateios lançados.
    * A lista é ordenada do mais recente para o mais antigo.
    * Permite visualizar os detalhes de cada rateio ou excluí-lo.
* **Excluir Rateio:**
    * Disponível na página de detalhes de um rateio ou na lista do histórico.
    * Uma confirmação é solicitada antes da exclusão. **Atenção:** Esta ação remove os registros do rateio das tabelas `Contas` e `DetalhesRateioUnidade`, mas **não reverte** a `ultima_leitura_kwh` na tabela `Unidades` para o valor que era antes deste rateio.

## 7. Estrutura do Banco de Dados (Principais Colunas)

* **Tabela `Unidades`**: Armazena as informações das 10 casas e do Salão de Festas.
    * `id` (PK)
    * `nome` (TEXTO): Nome da unidade (ex: "Casa 1", "Salão de Festas").
    * `tipo` (TEXTO): "casa" ou "salao_festas".
    * `ultima_leitura_kwh` (REAL): Armazena a última leitura do medidor para unidades do tipo "casa". É atualizada após cada rateio.

* **Tabela `Contas`**: Armazena os dados gerais de cada conta/rateio mensal.
    * `id` (PK)
    * `mes_referencia`, `ano_referencia` (INTEIRO)
    * `valor_total_reais` (REAL)
    * `consumo_total_interno_kwh` (REAL): Soma dos consumos das casas e do salão.
    * `custo_medio_kwh` (REAL): `valor_total_reais / consumo_total_interno_kwh`.
    * `custo_total_salao_reais` (REAL): Custo de energia específico do salão.
    * `cota_salao_por_casa_reais` (REAL): `custo_total_salao_reais / 10`.
    * `data_lancamento` (TIMESTAMP)

* **Tabela `DetalhesRateioUnidade`**: Armazena o consumo e os custos calculados para cada unidade em um determinado rateio.
    * `id` (PK)
    * `conta_id` (FK para `Contas.id`)
    * `unidade_id` (FK para `Unidades.id`)
    * `leitura_anterior_kwh` (REAL): Para casas, a leitura do medidor no início do período.
    * `leitura_atual_kwh` (REAL): Para casas, a leitura do medidor no fim do período (informada pelo síndico). Para o salão, armazena o consumo direto informado.
    * `consumo_kwh` (REAL): Consumo calculado (`leitura_atual - leitura_anterior` para casas) ou informado (para salão).
    * `custo_direto_reais` (REAL): `consumo_kwh * custo_medio_kwh`.
    * `valor_final_reais` (REAL): Para casas, `custo_direto_reais + cota_salao_por_casa_reais`. Para o salão, igual ao `custo_direto_reais`.

## 8. Sugestões e Melhorias Futuras

* **Edição de Rateios:** Permitir que o síndico edite um rateio lançado, caso algum dado tenha sido inserido incorretamente. Isso precisaria de uma lógica cuidadosa para recalcular e, possivelmente, ajustar a `ultima_leitura_kwh` das unidades.
* **Geração de Relatórios em PDF:** Facilitar a impressão e distribuição dos rateios.
* **Gráficos Simples:** Visualização do histórico de consumo/custo por casa ou do condomínio.
* **Autenticação de Usuário:** Proteger o acesso ao sistema com login e senha para o síndico.
* **Validações de Entrada de Dados Mais Robustas:** Tanto no frontend (JavaScript) quanto no backend.
* **Notificações:** Por exemplo, e-mail para o síndico após salvar um rateio.
* **Tratamento para Troca/Reset de Medidores:** Interface para registrar a troca de um medidor de uma casa e sua nova leitura inicial, ou para lidar com situações onde a leitura atual é menor que a anterior devido a um reset.
* **Backup e Restauração do Banco de Dados:** Uma funcionalidade simples para o síndico fazer cópias de segurança.

---
