ITEM_TYPE_ATTRIBUTES = {
    'auto': {
        'label': 'Automotivo',
        'fields': [
            {'key': 'marca', 'label': 'Marca', 'type': 'text'},
            {'key': 'modelo', 'label': 'Modelo', 'type': 'text'},
            {'key': 'ano_fabricacao', 'label': 'Ano fabricação', 'type': 'number'},
            {'key': 'ano_modelo', 'label': 'Ano modelo', 'type': 'number'},
            {'key': 'combustivel', 'label': 'Combustível', 'type': 'text'},
            {'key': 'zero_km', 'label': '0 KM?', 'type': 'boolean'},
        ],
        'coverages': [
            'Casco',
            'RCF-V',
            'RCF-D',
            'Apparatos',
            'Carro reserva',
            'Assistência 24h',
        ],
    },
    'property': {
        'label': 'Patrimonial',
        'fields': [
            {'key': 'tipo_imovel', 'label': 'Tipo (casa/apto/comercial)', 'type': 'text'},
            {'key': 'area_m2', 'label': 'Área (m²)', 'type': 'number'},
            {'key': 'ano_construcao', 'label': 'Ano construção', 'type': 'number'},
            {'key': 'andares', 'label': 'Andares', 'type': 'number'},
        ],
        'coverages': [
            'Incêndio',
            'Explosão',
            'Impacto de veículos',
            'Vendaval',
            'Roubo',
            'Responsabilidade civil',
        ],
    },
    'fleet': {
        'label': 'Frota',
        'fields': [
            {'key': 'quantidade_veiculos', 'label': 'Qtd. veículos', 'type': 'number'},
            {'key': 'uso', 'label': 'Uso (carga/passeio/misto)', 'type': 'text'},
        ],
        'coverages': [
            'Casco',
            'RCF-V',
            'RCF-D',
            'Apparatos',
        ],
    },
    'travel': {
        'label': 'Viagem',
        'fields': [
            {'key': 'destino', 'label': 'Destino', 'type': 'text'},
            {'key': 'motivo', 'label': 'Motivo (lazer/negócios)', 'type': 'text'},
            {'key': 'duracao_dias', 'label': 'Duração (dias)', 'type': 'number'},
        ],
        'coverages': [
            'Despesas médicas',
            'Bagagem',
            'Atraso de voo',
            'Cancelamento de viagem',
            'Repatriação',
        ],
    },
    'life': {
        'label': 'Vida',
        'fields': [
            {'key': 'tipo', 'label': 'Tipo (individual/grupo)', 'type': 'text'},
            {'key': 'idade_segurado', 'label': 'Idade segurado', 'type': 'number'},
            {'key': 'cpf_segurado', 'label': 'CPF segurado', 'type': 'text'},
        ],
        'coverages': [
            'Morte natural',
            'Morte acidental',
            'Invalidez permanente',
            'Doenças graves',
        ],
    },
    'equipment': {
        'label': 'Equipamento',
        'fields': [
            {'key': 'tipo_equipamento', 'label': 'Tipo', 'type': 'text'},
            {'key': 'marca', 'label': 'Marca', 'type': 'text'},
            {'key': 'modelo', 'label': 'Modelo', 'type': 'text'},
            {'key': 'numero_serie', 'label': 'Nº série', 'type': 'text'},
        ],
        'coverages': [
            'Incêndio',
            'Roubo',
            'Danos elétricos',
            'Responsabilidade civil',
        ],
    },
    'other': {
        'label': 'Outro',
        'fields': [],
        'coverages': [],
    },
}