# condominio_black_falcon/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, g
import database as db
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-haha' # Mude em produção!
app.config['DATABASE'] = os.path.join(app.instance_path, 'condominio.db')

# Comando para inicializar o BD via Flask CLI: flask init-db
@app.cli.command('init-db')
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas."""
    db.init_db(app)

# --- Funções Auxiliares de Cálculo ---
def calcular_rateio_logica(valor_total_conta_reais, consumos_kwh):
    """
    Calcula todos os valores do rateio.
    consumos_kwh: dict no formato {'Casa 1': kWh, ..., 'Salão de Festas': kWh}
    """
    num_casas = 10 # Conforme definido nas regras de negócio

    consumo_total_interno_kwh = sum(consumos_kwh.values())

    if consumo_total_interno_kwh == 0:
        # Evita divisão por zero se não houver consumo (cenário improvável com salão)
        custo_medio_kwh = 0
    else:
        custo_medio_kwh = valor_total_conta_reais / consumo_total_interno_kwh

    custo_total_salao_reais = consumos_kwh.get('Salão de Festas', 0) * custo_medio_kwh
    
    if num_casas > 0:
        cota_salao_por_casa_reais = custo_total_salao_reais / num_casas
    else:
        cota_salao_por_casa_reais = 0 # Evita divisão por zero

    detalhes_unidades = []
    soma_verificacao_valores_finais = 0

    unidades_db = db.query_db("SELECT id, nome, tipo FROM Unidades")
    map_unidade_id_nome = {u['nome']: u['id'] for u in unidades_db}
    map_unidade_id_tipo = {u['id']: u['tipo'] for u in unidades_db}


    for nome_unidade, consumo_unidade_kwh in consumos_kwh.items():
        unidade_id = map_unidade_id_nome.get(nome_unidade)
        if not unidade_id:
            # Deveria tratar erro se uma unidade do formulário não existir no BD
            # Mas por simplicidade, vamos assumir que sempre existe
            continue

        custo_direto_reais = consumo_unidade_kwh * custo_medio_kwh
        valor_final_reais = custo_direto_reais

        if map_unidade_id_tipo.get(unidade_id) == 'casa':
            valor_final_reais += cota_salao_por_casa_reais
            soma_verificacao_valores_finais += valor_final_reais
        
        detalhes_unidades.append({
            'unidade_id': unidade_id,
            'nome': nome_unidade, # Para exibição fácil no template
            'consumo_kwh': consumo_unidade_kwh,
            'custo_direto_reais': custo_direto_reais,
            'valor_final_reais': valor_final_reais,
            'tipo': map_unidade_id_tipo.get(unidade_id)
        })
        
        # Para o Salão de Festas, o valor_final_reais é o seu custo direto.
        # A soma de verificação só considera o valor final das casas.

    return {
        'consumo_total_interno_kwh': consumo_total_interno_kwh,
        'custo_medio_kwh': custo_medio_kwh,
        'custo_total_salao_reais': custo_total_salao_reais,
        'cota_salao_por_casa_reais': cota_salao_por_casa_reais,
        'detalhes_unidades': detalhes_unidades,
        'soma_verificacao_valores_finais': soma_verificacao_valores_finais # Soma dos valores finais das casas
    }
# --- Rotas ---
@app.route('/')
@app.route('/dashboard')
def dashboard():
    ultimo_rateio = db.query_db("SELECT id, mes_referencia, ano_referencia, valor_total_reais FROM Contas ORDER BY ano_referencia DESC, mes_referencia DESC LIMIT 1", one=True)
    return render_template('dashboard.html', ultimo_rateio=ultimo_rateio)

@app.route('/rateio/novo', methods=['GET', 'POST'])
def novo_rateio():
    unidades_db = db.query_db("SELECT id, nome, tipo, ultima_leitura_kwh FROM Unidades ORDER BY tipo, nome")
    
    map_unidades_ultima_leitura = {u['id']: u['ultima_leitura_kwh'] for u in unidades_db if u['tipo'] == 'casa'}

    if request.method == 'POST':
        try:
            mes_ref = int(request.form['mes_referencia'])
            ano_ref = int(request.form['ano_referencia'])
            valor_total_conta = float(request.form['valor_total_reais'])

            existente = db.query_db("SELECT id FROM Contas WHERE mes_referencia = ? AND ano_referencia = ?", (mes_ref, ano_ref), one=True)
            if existente:
                flash(f'Já existe um rateio para {mes_ref:02d}/{ano_ref}.', 'danger')
                return redirect(url_for('novo_rateio'))

            if valor_total_conta < 0:
                flash("Valor total da conta não pode ser negativo.", 'danger')
                return render_template('novo_rateio.html', unidades=unidades_db, form_data=request.form, ultimas_leituras=map_unidades_ultima_leitura)

            consumos_calculados_kwh = {}
            leituras_atuais_casas = {} # Para armazenar as leituras atuais e depois atualizar Unidades.ultima_leitura_kwh
            leituras_anteriores_casas = {} # Para armazenar as leituras anteriores para o relatório

            for unidade in unidades_db:
                input_name = f"input_unidade_{unidade['id']}" # Nome do campo de entrada
                try:
                    valor_input = float(request.form[input_name])
                    if valor_input < 0:
                         flash(f"Valor para {unidade['nome']} não pode ser negativo.", 'danger')
                         return render_template('novo_rateio.html', unidades=unidades_db, form_data=request.form, ultimas_leituras=map_unidades_ultima_leitura)

                    if unidade['tipo'] == 'casa':
                        leitura_atual = valor_input
                        leitura_anterior = unidade['ultima_leitura_kwh']
                        
                        if leitura_atual < leitura_anterior:
                            flash(f"Leitura atual da {unidade['nome']} ({leitura_atual} kWh) não pode ser menor que a leitura anterior ({leitura_anterior} kWh). Verifique os dados ou se o medidor foi zerado/trocado.", 'danger')
                            return render_template('novo_rateio.html', unidades=unidades_db, form_data=request.form, ultimas_leituras=map_unidades_ultima_leitura)
                        
                        consumo_casa = leitura_atual - leitura_anterior
                        consumos_calculados_kwh[unidade['nome']] = consumo_casa
                        leituras_atuais_casas[unidade['id']] = leitura_atual # Guardar para atualizar Unidades
                        leituras_anteriores_casas[unidade['id']] = leitura_anterior # Guardar para DetalhesRateioUnidade
                    
                    elif unidade['tipo'] == 'salao_festas':
                        # Salão de festas continua sendo consumo direto
                        consumos_calculados_kwh[unidade['nome']] = valor_input
                        # Para o salão, podemos popular leitura_atual_kwh com o consumo e leitura_anterior_kwh como 0 ou NULL
                        leituras_atuais_casas[unidade['id']] = valor_input 
                        leituras_anteriores_casas[unidade['id']] = 0 # Ou None

                except ValueError:
                    flash(f"Valor inválido para {unidade['nome']}.", 'danger')
                    return render_template('novo_rateio.html', unidades=unidades_db, form_data=request.form, ultimas_leituras=map_unidades_ultima_leitura)
            
            # Calcular rateio com os consumos calculados
            dados_rateio_final = calcular_rateio_logica(valor_total_conta, consumos_calculados_kwh)

            # Salvar no banco
            conta_id = db.execute_db(
                "INSERT INTO Contas (mes_referencia, ano_referencia, valor_total_reais, consumo_total_interno_kwh, custo_medio_kwh, custo_total_salao_reais, cota_salao_por_casa_reais) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (mes_ref, ano_ref, valor_total_conta, 
                 dados_rateio_final['consumo_total_interno_kwh'], 
                 dados_rateio_final['custo_medio_kwh'],
                 dados_rateio_final['custo_total_salao_reais'],
                 dados_rateio_final['cota_salao_por_casa_reais'])
            )

            for detalhe_unidade_calculado in dados_rateio_final['detalhes_unidades']:
                unidade_id_atual = detalhe_unidade_calculado['unidade_id']
                
                # Determinar leitura_anterior e leitura_atual para salvar em DetalhesRateioUnidade
                leitura_ant_para_db = None
                leitura_atu_para_db = None

                unidade_info_db = next((u for u in unidades_db if u['id'] == unidade_id_atual), None)
                if unidade_info_db and unidade_info_db['tipo'] == 'casa':
                    leitura_ant_para_db = leituras_anteriores_casas.get(unidade_id_atual)
                    leitura_atu_para_db = leituras_atuais_casas.get(unidade_id_atual)
                elif unidade_info_db and unidade_info_db['tipo'] == 'salao_festas':
                    # Para o salão, o "consumo" é a leitura atual, e anterior pode ser 0 ou NULL
                    leitura_ant_para_db = 0 
                    leitura_atu_para_db = detalhe_unidade_calculado['consumo_kwh']


                db.execute_db(
                    "INSERT INTO DetalhesRateioUnidade (conta_id, unidade_id, leitura_anterior_kwh, leitura_atual_kwh, consumo_kwh, custo_direto_reais, valor_final_reais) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (conta_id, unidade_id_atual,
                     leitura_ant_para_db,
                     leitura_atu_para_db,
                     detalhe_unidade_calculado['consumo_kwh'], # Este é o consumo já calculado
                     detalhe_unidade_calculado['custo_direto_reais'], 
                     detalhe_unidade_calculado['valor_final_reais'])
                )
            
            # ATUALIZAR ultima_leitura_kwh na tabela Unidades para as CASAS
            for unidade_id, leitura_atual_val in leituras_atuais_casas.items():
                # Apenas atualiza se for uma casa e tivermos uma leitura atual para ela
                unidade_tipo_check = next((u['tipo'] for u in unidades_db if u['id'] == unidade_id), None)
                if unidade_tipo_check == 'casa':
                    db.execute_db("UPDATE Unidades SET ultima_leitura_kwh = ? WHERE id = ?", (leitura_atual_val, unidade_id))
            
            flash('Novo rateio lançado com sucesso!', 'success')
            return redirect(url_for('ver_rateio', id_rateio=conta_id))

        except ValueError as ve:
            flash(f'Por favor, verifique os valores inseridos: {str(ve)}', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro ao processar o rateio: {str(e)}', 'danger')
            app.logger.error(f"Erro ao salvar rateio: {e}", exc_info=True)

    now = datetime.now()
    default_form_data = {'mes_referencia': now.month, 'ano_referencia': now.year}
    return render_template('novo_rateio.html', unidades=unidades_db, form_data=default_form_data, ultimas_leituras=map_unidades_ultima_leitura)


@app.route('/rateio/ver/<int:id_rateio>')
def ver_rateio(id_rateio):
    conta = db.query_db("SELECT * FROM Contas WHERE id = ?", (id_rateio,), one=True)
    if not conta:
        flash('Rateio não encontrado.', 'danger')
        return redirect(url_for('historico'))

    detalhes = db.query_db("""
        SELECT du.*, u.nome as unidade_nome, u.tipo as unidade_tipo
        FROM DetalhesRateioUnidade du
        JOIN Unidades u ON du.unidade_id = u.id
        WHERE du.conta_id = ?
        ORDER BY u.tipo, u.nome
    """, (id_rateio,))

    detalhes_casas = [d for d in detalhes if d['unidade_tipo'] == 'casa']
    detalhe_salao = next((d for d in detalhes if d['unidade_tipo'] == 'salao_festas'), None)
    
    soma_verificacao = sum(d['valor_final_reais'] for d in detalhes_casas)

    return render_template('ver_rateio.html', conta=conta, detalhes_casas=detalhes_casas, detalhe_salao=detalhe_salao, soma_verificacao=soma_verificacao)


# ... (Mantenha as outras rotas como historico, excluir_rateio e o context_processor e if __name__...)
# A função calcular_rateio_logica que você me forneceu antes permanece a mesma,
# pois ela já espera um dicionário de `consumos_kwh` finais por unidade.
# A mudança principal é como esse `consumos_kwh` é gerado para as casas.

def calcular_rateio_logica(valor_total_conta_reais, consumos_kwh_finais):
    num_casas = 10 
    consumo_total_interno_kwh = sum(consumos_kwh_finais.values())
    custo_medio_kwh = valor_total_conta_reais / consumo_total_interno_kwh if consumo_total_interno_kwh > 0 else 0
    custo_total_salao_reais = consumos_kwh_finais.get('Salão de Festas', 0) * custo_medio_kwh
    cota_salao_por_casa_reais = custo_total_salao_reais / num_casas if num_casas > 0 else 0
    
    detalhes_unidades_calculados = []
    soma_verificacao_valores_finais = 0

    unidades_info_db = db.query_db("SELECT id, nome, tipo FROM Unidades")
    map_unidade_id_nome = {u['nome']: u['id'] for u in unidades_info_db}
    map_unidade_id_tipo = {u['id']: u['tipo'] for u in unidades_info_db}

    for nome_unidade, consumo_final_unidade_kwh in consumos_kwh_finais.items():
        unidade_id = map_unidade_id_nome.get(nome_unidade)
        if not unidade_id: continue

        custo_direto_reais = consumo_final_unidade_kwh * custo_medio_kwh
        valor_final_reais = custo_direto_reais

        if map_unidade_id_tipo.get(unidade_id) == 'casa':
            valor_final_reais += cota_salao_por_casa_reais
            soma_verificacao_valores_finais += valor_final_reais
        
        detalhes_unidades_calculados.append({
            'unidade_id': unidade_id,
            'nome': nome_unidade,
            'consumo_kwh': consumo_final_unidade_kwh, # Este é o consumo calculado (Leitura Atual - Leitura Anterior)
            'custo_direto_reais': custo_direto_reais,
            'valor_final_reais': valor_final_reais,
            'tipo': map_unidade_id_tipo.get(unidade_id)
        })
        
    return {
        'consumo_total_interno_kwh': consumo_total_interno_kwh,
        'custo_medio_kwh': custo_medio_kwh,
        'custo_total_salao_reais': custo_total_salao_reais,
        'cota_salao_por_casa_reais': cota_salao_por_casa_reais,
        'detalhes_unidades': detalhes_unidades_calculados, # Contém 'consumo_kwh' que é o calculado
        'soma_verificacao_valores_finais': soma_verificacao_valores_finais
    }

@app.route('/rateio/historico')
def historico():
    rateios = db.query_db("SELECT id, mes_referencia, ano_referencia, valor_total_reais, data_lancamento FROM Contas ORDER BY ano_referencia DESC, mes_referencia DESC")
    return render_template('historico.html', rateios=rateios)

@app.route('/rateio/excluir/<int:id_rateio>', methods=['POST'])
def excluir_rateio(id_rateio):
    # Primeiro, exclui os detalhes associados
    db.execute_db("DELETE FROM DetalhesRateioUnidade WHERE conta_id = ?", (id_rateio,))
    # Depois, exclui a conta principal
    db.execute_db("DELETE FROM Contas WHERE id = ?", (id_rateio,))
    flash('Rateio excluído com sucesso.', 'success')
    return redirect(url_for('historico')) # Note que esta linha também usa url_for('historico')



# Adicionar o context_processor se ainda não existir
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    if not os.path.exists(os.path.join(instance_dir, 'condominio.db')):
        with app.app_context():
            db.init_db(app)
    app.run(debug=True)