from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

# Certifique-se de que a pasta instance existe
if not os.path.exists('instance'):
    os.makedirs('instance')

# Criação do engine e da base declarativa
engine = create_engine('sqlite:///instance/database.db')
Base = declarative_base()

# Tabela de associação entre Formulário e Perguntas
formulario_perguntas = Table(
    'formulario_perguntas',
    Base.metadata,
    Column('formulario_id', Integer, ForeignKey('Formularios.id'), primary_key=True),
    Column('pergunta_id', Integer, ForeignKey('Perguntas.id'), primary_key=True)
)

# Definição da tabela Perguntas
class Pergunta(Base):
    __tablename__ = 'Perguntas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    codigo_html = Column(Text, nullable=False)
    modo = Column(String, nullable=False)
    area = Column(String, nullable=False)
    formularios = relationship('Formulario', secondary=formulario_perguntas, back_populates='perguntas')

# Definição da tabela Setores
class Setor(Base):
    __tablename__ = 'Setores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    setor = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    formularios = relationship('Formulario', back_populates='setor')

# Definição da tabela Formularios
class Formulario(Base):
    __tablename__ = 'Formularios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    tipo_profissional = Column(String, nullable=False)  # 'enfermeiro' ou 'tecnico'
    setor_id = Column(Integer, ForeignKey('Setores.id'), nullable=False)
    setor = relationship('Setor', back_populates='formularios')
    perguntas = relationship('Pergunta', secondary=formulario_perguntas, back_populates='formularios')

# Criação das tabelas no banco de dados
Base.metadata.create_all(engine)

# Criação de uma sessão
Session = sessionmaker(bind=engine)
session = Session()

# Dados de exemplo para perguntas
perguntas_exemplo = [
    {
        "titulo": "Avaliação de Dor",
        "codigo_html": '<div class="form-group"><label>Intensidade da Dor (0-10):</label><input type="number" min="0" max="10" class="form-control"></div>',
        "modo": "Modo Fisiológico",
        "area": "Dor"
    },
    {
        "titulo": "Estado Emocional",
        "codigo_html": '<div class="form-group"><label>Como está seu estado emocional hoje?</label><select class="form-control"><option>Calmo</option><option>Ansioso</option><option>Deprimido</option></select></div>',
        "modo": "Modo Autoconceito",
        "area": "Psicológico"
    },
    {
        "titulo": "Autoimagem",
        "codigo_html": '<div class="form-group"><label>Como você se sente em relação à sua autoimagem?</label><textarea class="form-control" rows="3"></textarea></div>',
        "modo": "Modo Autoconceito",
        "area": "Psicológico"
    }
]

# Função para adicionar um setor
def adicionar_setor(setor_nome, senha):
    novo_setor = Setor(setor=setor_nome, senha=senha)
    session.add(novo_setor)
    session.commit()
    return novo_setor

# Função para adicionar um formulário
def adicionar_formulario(nome, tipo_profissional, setor):
    novo_formulario = Formulario(nome=nome, tipo_profissional=tipo_profissional, setor=setor)
    session.add(novo_formulario)
    session.commit()
    return novo_formulario

# Função para adicionar uma pergunta
def adicionar_pergunta(titulo, codigo_html, modo, area):
    nova_pergunta = Pergunta(
        titulo=titulo,
        codigo_html=codigo_html,
        modo=modo,
        area=area
    )
    session.add(nova_pergunta)
    session.commit()
    return nova_pergunta

if __name__ == '__main__':
    # Criar setores e seus formulários apenas se as tabelas estiverem vazias
    if session.query(Setor).count() == 0:
        setores_dados = {
            "Alergia": [
                {"nome": "Consulta de Enfermagem", "tipo": "enfermeiro"},
                {"nome": "Anotação de Enfermagem", "tipo": "tecnico"}
            ],
            "Diabetes": [
                {"nome": "Consulta de Admissão", "tipo": "enfermeiro"},
                {"nome": "Consulta Insulina", "tipo": "enfermeiro"},
                {"nome": "Anotação de Enfermagem", "tipo": "tecnico"}
            ],
            "Centro De Infusão": [
                {"nome": "Consulta de Infusão", "tipo": "enfermeiro"},
                {"nome": "Anotação de Infusão", "tipo": "tecnico"}
            ],
            "Cardiologia": [
                {"nome": "Consulta Cardiológica", "tipo": "enfermeiro"},
                {"nome": "Anotação Cardiológica", "tipo": "tecnico"}
            ],
            "Estomaterapia": [
                {"nome": "Consulta Estomaterapia", "tipo": "enfermeiro"},
                {"nome": "Anotação Estomaterapia", "tipo": "tecnico"}
            ],
            "Ucamb": [
                {"nome": "Consulta Ucamb", "tipo": "enfermeiro"},
                {"nome": "Anotação Ucamb", "tipo": "tecnico"}
            ]
        }

        # Criar setores e formulários
        for setor_nome, formularios in setores_dados.items():
            setor = adicionar_setor(setor_nome, "senha123")
            for form in formularios:
                formulario = adicionar_formulario(form["nome"], form["tipo"], setor)
                
                # Adicionar perguntas de exemplo ao formulário
                for pergunta_dados in perguntas_exemplo:
                    pergunta = adicionar_pergunta(
                        pergunta_dados["titulo"],
                        pergunta_dados["codigo_html"],
                        pergunta_dados["modo"],
                        pergunta_dados["area"]
                    )
                    formulario.perguntas.append(pergunta)
                    session.commit()

                    

        print("Banco de dados inicializado com sucesso!")