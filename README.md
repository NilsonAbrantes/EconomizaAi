# Organização Financeira - Django

Aplicação web em Django para organização financeira mensal.

## Funções

- Cadastro de salário mensal.
- Cadastro de contas fixas.
- Cadastro de faturas previstas.
- Cadastro de bicos/renda extra com nome e valor.
- Cálculo de renda total, gastos, saldo final e recomendação para guardar dinheiro.
- Classificação financeira:
  - Crítico
  - Moderado
  - Suave
- Histórico em formato de planilha.
- Detalhes por mês.
- Edição de mês salvo.
- Exclusão de mês.
- Exportação CSV.

## Como executar

Dentro da pasta do projeto:

```bash
python -m venv venv
```

No Windows:

```bash
venv\Scripts\activate
```

No Linux/Mac:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o banco de dados:

```bash
python manage.py makemigrations
python manage.py migrate
```

Execute o servidor:

```bash
python manage.py runserver
```

Acesse no navegador:

```text
http://127.0.0.1:8000/
```

O banco será criado no arquivo:

```text
db.sqlite3
```
