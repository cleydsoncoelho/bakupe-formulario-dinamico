from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from banco import Session, Setor, Formulario, Pergunta

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Altere para uma chave secreta segura

# Criar sessão do banco de dados
session_db = Session()

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'setor_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    setores = session_db.query(Setor).all()
    return render_template('index.html', setores=setores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        setor_nome = request.form['setor']
        senha = request.form['senha']
        
        setor = session_db.query(Setor).filter_by(setor=setor_nome).first()
        
        if setor and setor.senha == senha:
            session['setor_id'] = setor.id
            session['setor_nome'] = setor.setor
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('administrador'))
        else:
            flash('Setor ou senha inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/administrador')
@app.route('/administrador/<int:formulario_id>')
@login_required
def administrador(formulario_id=None):
    setor_id = session.get('setor_id')
    setor = session_db.query(Setor).get(setor_id)
    formularios = session_db.query(Formulario).filter_by(setor_id=setor_id).all()
    
    if formulario_id:
        formulario_selecionado = session_db.query(Formulario).get(formulario_id)
        if formulario_selecionado and formulario_selecionado.setor_id == setor_id:
            perguntas = session_db.query(Pergunta).all()
            # Adiciona atributo 'ativa' para cada pergunta
            for pergunta in perguntas:
                pergunta.ativa = pergunta in formulario_selecionado.perguntas
            return render_template('administrador.html', 
                                 setor=setor,
                                 formularios=formularios,
                                 formulario_selecionado=formulario_selecionado,
                                 perguntas=perguntas)
    
    return render_template('administrador.html', 
                         setor=setor,
                         formularios=formularios)

@app.route('/novo_formulario', methods=['POST'])
@login_required
def novo_formulario():
    nome = request.form['nome']
    tipo_profissional = request.form['tipo_profissional']
    setor_id = session.get('setor_id')
    
    setor = session_db.query(Setor).get(setor_id)
    if setor:
        novo_form = Formulario(nome=nome, tipo_profissional=tipo_profissional, setor=setor)
        session_db.add(novo_form)
        session_db.commit()
        flash('Formulário criado com sucesso!', 'success')
    else:
        flash('Erro ao criar formulário!', 'danger')
    
    return redirect(url_for('administrador'))

@app.route('/toggle_pergunta/<int:pergunta_id>/<int:formulario_id>')
@login_required
def toggle_pergunta(pergunta_id, formulario_id):
    try:
        pergunta = session_db.query(Pergunta).get(pergunta_id)
        formulario = session_db.query(Formulario).get(formulario_id)
        
        if pergunta and formulario:
            if pergunta in formulario.perguntas:
                formulario.perguntas.remove(pergunta)
            else:
                formulario.perguntas.append(pergunta)
            session_db.commit()
            flash('Pergunta atualizada com sucesso!', 'success')
        else:
            flash('Pergunta ou formulário não encontrado!', 'danger')
    except Exception as e:
        session_db.rollback()
        flash('Erro ao atualizar pergunta!', 'danger')
    
    return redirect(url_for('administrador', formulario_id=formulario_id))

@app.route('/visualizar_formulario/<int:formulario_id>')
def visualizar_formulario(formulario_id):
    formulario = session_db.query(Formulario).filter_by(id=formulario_id).first()
    if not formulario:
        flash('Formulário não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    perguntas_ativas = [p for p in formulario.perguntas]
    
    # Direciona para template específico baseado no tipo de profissional
    if formulario.tipo_profissional == 'enfermeiro':
        return render_template('formularioenfermeiro.html', 
                             formulario=formulario, 
                             perguntas=perguntas_ativas,
                             setor=formulario.setor)
    else:
        return render_template('formulario.html', 
                             formulario=formulario, 
                             perguntas=perguntas_ativas,
                             setor=formulario.setor)

if __name__ == '__main__':
    app.run(debug=True)