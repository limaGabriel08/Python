import sqlite3
from functools import wraps

import requests
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

ARQUIVO_BANCO = 'database.db'
SITUACOES = ('pendente', 'em andamento', 'concluida')
ROTULOS = {'pendente': 'Pendente', 'em andamento': 'Em andamento', 'concluida': 'Concluída'}
CORES = {'pendente': 'aberta', 'em andamento': 'andamento', 'concluida': 'pronta'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agenda-chave-de-sessao-2026'


def conectar():
    if 'banco' not in g:
        g.banco = sqlite3.connect(ARQUIVO_BANCO)
        g.banco.row_factory = sqlite3.Row
    return g.banco


@app.teardown_appcontext
def encerrar_conexao(excecao=None):
    banco = g.pop('banco', None)
    if banco is not None:
        banco.close()


def buscar(instrucao, valores=(), unico=False):
    linhas = conectar().execute(instrucao, valores).fetchall()
    if unico:
        return linhas[0] if linhas else None
    return linhas


def gravar(instrucao, valores=()):
    banco = conectar()
    banco.execute(instrucao, valores)
    banco.commit()


def preparar_banco():
    banco = sqlite3.connect(ARQUIVO_BANCO)
    banco.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        );
    """)
    banco.commit()
    banco.close()


def exigir_login(rota):
    @wraps(rota)
    def verificacao(*args, **kwargs):
        if not session.get('conta_id'):
            flash('Entre na sua conta para continuar.', 'warning')
            return redirect(url_for('login'))
        return rota(*args, **kwargs)
    return verificacao


def minha_tarefa(codigo):
    return buscar('SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
                  (codigo, session['conta_id']), unico=True)


def email_aceitavel(texto):
    if texto.count('@') != 1:
        return False
    apelido, dominio = texto.split('@')
    return bool(apelido) and '.' in dominio \
        and not dominio.startswith('.') and not dominio.endswith('.')


def frase_do_dia():
    try:
        resposta = requests.get('https://dummyjson.com/quotes/random', timeout=5)
        dados = resposta.json()
        return f"{dados['quote']} — {dados['author']}"
    except Exception:
        return 'Sem conexão para carregar a frase de hoje.'


@app.context_processor
def injetar_apoio():
    return {'rotulos': ROTULOS, 'cores': CORES}


@app.route('/')
def abertura():
    if session.get('conta_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method != 'POST':
        return render_template('registro.html')

    apelido = request.form['apelido'].strip()
    email = request.form['email'].strip().lower()
    segredo = request.form['segredo']

    if not apelido or not email or not segredo:
        flash('Preencha todos os campos.', 'danger')
    elif not email_aceitavel(email):
        flash('Esse e-mail não parece válido.', 'danger')
    elif len(segredo) < 6:
        flash('Use uma senha de 6 caracteres ou mais.', 'danger')
    elif buscar('SELECT id FROM usuarios WHERE email = ?', (email,), unico=True):
        flash('Já existe uma conta com esse e-mail.', 'danger')
    else:
        gravar('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
               (apelido, email, generate_password_hash(segredo)))
        flash('Conta criada. Faça login para começar.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html', apelido=apelido, email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')

    email = request.form['email'].strip().lower()
    segredo = request.form['segredo']

    if not email or not segredo:
        flash('Informe o e-mail e a senha.', 'danger')
        return render_template('login.html', email=email)

    cadastro = buscar('SELECT * FROM usuarios WHERE email = ?', (email,), unico=True)
    if cadastro and check_password_hash(cadastro['senha'], segredo):
        session.clear()
        session['conta_id'] = cadastro['id']
        session['apelido'] = cadastro['nome']
        return redirect(url_for('dashboard'))

    flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html', email=email)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@exigir_login
def dashboard():
    lista = buscar('SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC',
                   (session['conta_id'],))
    return render_template('dashboard.html', lista=lista, frase=frase_do_dia())


@app.route('/nova_tarefa', methods=['GET', 'POST'])
@exigir_login
def nova_tarefa():
    if request.method != 'POST':
        return render_template('formulario.html', tarefa=None)

    assunto = request.form['assunto'].strip()
    detalhe = request.form['detalhe'].strip()
    situacao = request.form['situacao']

    if not assunto:
        flash('Dê um nome para a tarefa.', 'danger')
        return render_template('formulario.html', tarefa=None)

    if situacao not in SITUACOES:
        situacao = 'pendente'

    gravar('INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)',
           (assunto, detalhe, situacao, session['conta_id']))
    flash('Tarefa adicionada.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/editar/<int:codigo>', methods=['GET', 'POST'])
@exigir_login
def editar(codigo):
    tarefa = minha_tarefa(codigo)
    if tarefa is None:
        flash('Essa tarefa não existe na sua conta.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method != 'POST':
        return render_template('formulario.html', tarefa=tarefa)

    assunto = request.form['assunto'].strip()
    detalhe = request.form['detalhe'].strip()
    situacao = request.form['situacao']

    if not assunto:
        flash('Dê um nome para a tarefa.', 'danger')
        return render_template('formulario.html', tarefa=tarefa)

    if situacao not in SITUACOES:
        situacao = 'pendente'

    gravar('UPDATE tarefas SET titulo = ?, descricao = ?, status = ? '
           'WHERE id = ? AND usuario_id = ?',
           (assunto, detalhe, situacao, codigo, session['conta_id']))
    flash('Alterações salvas.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/concluir/<int:codigo>', methods=['POST'])
@exigir_login
def concluir(codigo):
    if minha_tarefa(codigo) is None:
        flash('Essa tarefa não existe na sua conta.', 'danger')
        return redirect(url_for('dashboard'))

    gravar("UPDATE tarefas SET status = 'concluida' WHERE id = ? AND usuario_id = ?",
           (codigo, session['conta_id']))
    flash('Tarefa concluída!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/excluir/<int:codigo>', methods=['POST'])
@exigir_login
def excluir(codigo):
    if minha_tarefa(codigo) is None:
        flash('Essa tarefa não existe na sua conta.', 'danger')
        return redirect(url_for('dashboard'))

    gravar('DELETE FROM tarefas WHERE id = ? AND usuario_id = ?',
           (codigo, session['conta_id']))
    flash('Tarefa removida.', 'success')
    return redirect(url_for('dashboard'))


preparar_banco()

if __name__ == '__main__':
    app.run(debug=False)
