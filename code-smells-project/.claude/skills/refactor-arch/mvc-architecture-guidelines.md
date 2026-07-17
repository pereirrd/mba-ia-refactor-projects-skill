# Guidelines de Arquitetura MVC

Alvo da **Fase 3**. Adapte nomes de pasta à convenção da linguagem, mantendo as
responsabilidades.

## Camadas

### Model
- Representa dados e persistência (entidades ORM **ou** repositórios SQL).
- Encapsula queries parametrizadas / métodos de domínio (`is_overdue`,
  `set_password`).
- **Não** conhece HTTP (`request`, `res`, status codes).
- **Não** formata resposta JSON final (pode expor `to_dict` sem segredos).

### View (Routes / Blueprints / Routers)
- Define paths, métodos HTTP e binding de parâmetros.
- Faz parse superficial do request e delega ao Controller.
- Serializa a resposta HTTP (JSON).
- **Não** contém regras de negócio complexas nem SQL.

### Controller
- Orquestra o caso de uso: valida entrada → chama Model/Service → decide status.
- Coordena side-effects (notificações) via serviços injetáveis.
- Mantém handlers finos e testáveis.
- **Não** instancia detalhes de infra espalhados (usa config/DI).

### Config
- Centraliza host, port, DB URI, SECRET_KEY, debug, CORS.
- Lê de variáveis de ambiente com defaults seguros para desenvolvimento.
- **Proibido** commitar secrets reais.

### Middlewares
- Error handler global (mapeia exceções → JSON + status).
- Auth/guards quando o domínio exigir.
- Logging estruturado (substituir `print` de produção).

### Composition Root (`app.py` / `app.js`)
- Cria a aplicação, registra rotas/controllers, inicializa DB.
- Único ponto de boot (`if __name__ == "__main__"` / `app.listen`).

## Estrutura de referência

### Python / Flask
```
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   ├── usuario_model.py
│   └── pedido_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py
```

### Node.js / Express
```
src/
├── config/settings.js
├── models/
├── views/routes.js
├── controllers/
├── middlewares/errorHandler.js
├── database.js
└── app.js
```

## Regras de ouro

1. Uma responsabilidade por módulo/arquivo de domínio.
2. Endpoints de negócio preservados (contrato público).
3. Backdoors perigosos removidos ou protegidos.
4. Senhas nunca retornadas nas respostas.
5. Error handling centralizado — sem `except:` nu / callbacks mudos.
6. Em projetos já parcialmente organizados: mover o que está no lugar errado
   (ex.: categories fora de reports), wired services, thin routes — sem rewrite
   desnecessário.
