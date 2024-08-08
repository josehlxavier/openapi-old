import requests
import json
import time
import argparse, getpass
from datetime import datetime

'''
#########IMPORTANTE###########IMPORTANTE###########IMPORTANTE###########IMPORTANTE#############

Esse código é apenas para suporte operacional no dia-a-dia. Não foram consideradas implicações
de segurança quanto ao seu uso e o uso é de inteira responsabilidade de quem estiver 
executando-o no momento.

Use por sua conta e risco.

#########IMPORTANTE###########IMPORTANTE###########IMPORTANTE###########IMPORTANTE#############
'''

password = ''

def extract_data(data):     # Obter os dados de um objeto JSON
    data = json.loads(data)
    linha_csv = []
    notas_concat = ''
    linha_csv.append(data['id'])
    for i in data['info']:
        if i['key'] == 'CustomColumn155sr': # "CustomColumn155sr" = "Usuário Solicitante"
            linha_csv.append(i['valueCaption'].replace('\\t',''))
        if i['key'] == 'insert_time': # Data de criação
            linha_csv.append(str(i['valueCaption']))
        if i['key'] == 'title': #Título da SR
            linha_csv.append(i['valueCaption'])
        if i['key'] == 'description': #Descrição da SR
            linha_csv.append(str(i['valueCaption']).replace('\t', '').replace('\n', '').replace('|','')) #Removendo linhas novas, tabs e pipes. Não quebrar a formatação do CSV(separador é o pipe)
        if i['key'] == 'notes': #
            if i['value'] is not None:
                for value in i['value']:
                    notas_concat += str(value) + '#'
                linha_csv.append(notas_concat.replace('\t', '').replace('\n', ''))
            else:
                linha_csv.append('Ainda não há')
        if i['key'] == 'CustomColumn114sr':
            linha_csv.append(i['valueCaption'])
        if i['key'] == 'category':
            linha_csv.append(i['valueCaption'])
        if i['key'] == 'close_time':
            if i['valueCaption'] != '' :
                linha_csv.append(i['valueCaption'])
            else:
                linha_csv.append('Em aberto')
        if i['key'] == 'CustomColumn16sr': # "CustomColumn16sr" = "Equipe de Atendimento"
            if i['valueCaption'] != '' :
                linha_csv.append(i['valueCaption'])
            else:
                linha_csv.append('Ticket ainda sem solução')
    linha_csv = '|'.join(map(str, linha_csv))
    linha_csv = filter(str.strip, linha_csv.splitlines())
    return linha_csv
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Programa desenvolvido para auxiliar a extração \n \
                                      de informações de tickets do Service Desk do Open Finance. \n \
                                     Recebe como parametro uma lista de tickets, separados por vírgula, \n \
                                     sem a "#" no início, o nome de usuário/e-mail e a senha utilizada \n \
                                     para login na plataforma.\n \
                                     Parametros obrigatórios: \n \
                                     -t, --tickets, Lista de tickets que devem ser consultados \n \
                                     -u, --user, E-mail de login do Service Desk \n \
                                     -p, --password, Senha de acesso ao Service Desk \n \
                                     \nParametros opcionais: \n \
                                     -fo, --file_output, Nome do arquivo que deve ser gerado. Caso nao fornecido, será utilizada a data/hora atual.')
    parser.add_argument('-t', '--tickets', help='Lista de tickets que devem ser buscadas', type=str)
    parser.add_argument('-u', '--user', help='Email utilizado para login no Service Desk', type=str)
    parser.add_argument('-p', '--password', help='Senha de acesso ao Service Desk', action='store_true', dest='password' )
    parser.add_argument('-fo','--file_output', help="Nome do arquivo que deve ser gerado. Caso nao fornecido, será utilizada a data/hora atual.")
    args = vars(parser.parse_args())
    print(str(args.keys()) + str(args.values()))
    if not args['file_output']:
        args['file_output'] = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        assert args['tickets'] and args['user'] and args['password']            
    except AssertionError as e:
        args['tickets'] = input('Digite os numeros dos tickets separados por virgula: ')
        args['user'] = input('Digite o email do usuario para login: ')
        args['password'] = getpass.getpass('Digite a senha de acesso ao Service Desk: ')
        
    #lista de tickets pagamentos:
    #lista_sr_id = [49769,37251,33889,33873,35535,33840,39135,47785,36943,33290,40371,35191,38135,46522,33439,43541,45120,41957,36080,35598,39008,36523,41917,41529,36622,38865,33353,32237,32103,45679,45631,47950,47907,43631,45894,43162,39545,38550,38337,36537,34753,34207,32772,32467,40205,39674,37291,32771,32174,34494,35201,45652,48364,36406,37652,36640,34512,34203,32672,32246,38323,37664,38355,37791,36906,36203,44645,37495,33736,36247,36334,34611,34320,43022,46933,38764,40612,38936,39771,36078,38866,34764,41313,38799,38387,35284,48670,40177,34338,37347,33787,47944,41455,32528,32206,33148,32532,33151,32877,35534,37111,36755,32629,38991,42588,49052,44401,39434,36713,36393,40991,41672,39760,37815,39264,38366,33416,32135,32182,33441,32965,35196,32299,34507,44175,38942,38761,33693,33400,33867,35980,37775,33618,32838,33453,34588,33320,32178,35020,35385,35570,35567,35384,36736,36165,35150,35149,35571,34282,45704,42901,47181,42941,45199,37830,37593,33775,33773,33772,33672,33469,38041,38231,33557,43124,34754,32232,36154,32265,32231,32229,32803,35558,32226,35874,44359,43605,40709,35262,34461,39076,32336,32157,46375,45730,44605,48813,48812,48678,48040,48039,48026,48002,47665,48810]
    #lista de tickets JSR:
    lista_sr_id = args['tickets'].split(',')
    session = requests.Session()    # Criar uma sessão com o cookies vazio
    url = 'https://servicedesk.openfinancebrasil.org.br/api/v1/login' # Definir endereço para login
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json'
    }
    userName = args['user']
    passwd = args['password']
    payload = {'user_name': userName,'password': passwd, 'accountId' : 'obkbrasil'}
    payload = json.dumps(payload)
    response = session.post(url, headers=headers, data=payload)
    arqv_leitura = []
    if response.status_code == 200:     
        cookies = response.cookies      
        session.cookies = cookies
        for i in lista_sr_id:
            #queryParams = "?fields=assigned_group,update_time,status,description,request_user_name,CustomColumn16sr"
            url_busca_sr = 'https://servicedesk.openfinancebrasil.org.br/api/v1/sr/' + str(i)
            print("Ticket #"+str(i))
            response_leitura = session.get(url_busca_sr, headers=headers)
            arqv_leitura = open(str(args['file_output'] + '.csv'),'a', encoding='utf-8')
            with arqv_leitura as file:
                file.writelines(extract_data(response_leitura.text))
                file.write('\n')
            time.sleep(1)