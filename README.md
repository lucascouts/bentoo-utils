# Bentoo Utils

Bentoo Utils é um conjunto de ferramentas para o desenvolvimento e manutenção do Bentoo, um fork personalizado do Gentoo construído a partir de um stage3.

## Funcionalidades

O pacote atual inclui o Overlay Manager, que simplifica o gerenciamento do overlay 'bentoo' no GitHub.

### Comandos Disponíveis

- `bentoo overlay repo add [path]`: Adiciona arquivos ao staging area do Git
- `bentoo overlay repo status`: Mostra o status atual do repositório Git
- `bentoo overlay repo commit`: Cria um novo commit com as mudanças atuais
- `bentoo overlay repo push`: Envia as mudanças para o repositório remoto

## Instalação

### Via Emerge (Recomendado para usuários Gentoo/Bentoo)

1. Adicione o overlay Bentoo ao seu sistema (se ainda não estiver adicionado).
2. Emerge o pacote:

   ```
   emerge --ask sys-apps/bentoo-utils
   ```

### Instalação Manual (para desenvolvimento)

1. Clone o repositório:

   ```
   git clone https://github.com/lucascouts/bentoo-utils.git
   cd bentoo-utils
   ```

2. Instale o pacote:

   ```
   pip install -e .
   ```

## Configuração

Após a instalação, você precisa configurar o caminho do seu overlay Bentoo:

1. Edite o arquivo `/home/.bentoo/config.json`:

   ```json
   {
     "overlay": {
       "repo": {
         "type": "git",
         "user": "seu_usuario",
         "email": "seu_email@exemplo.com"
       },
       "local": "/caminho/para/seu/overlay/bentoo"
     }
   }
   ```

2. Substitua "seu_usuario", "seu_email@exemplo.com" e o caminho do overlay pelos seus dados.

## Uso

Após a instalação e configuração, você pode usar os comandos do Bentoo Utils diretamente do terminal:

```
bentoo overlay repo add .
bentoo overlay repo status
bentoo overlay repo commit
bentoo overlay repo push
```

## Desenvolvimento

Para contribuir com o Bentoo Utils:

1. Fork o repositório no GitHub.
2. Clone seu fork: `git clone https://github.com/seu-usuario/bentoo-utils.git`
3. Crie uma branch para sua feature: `git checkout -b minha-nova-feature`
4. Faça suas alterações e commit: `git commit -am 'Adiciona alguma feature'`
5. Push para a branch: `git push origin minha-nova-feature`
6. Crie um novo Pull Request no GitHub.

## Licença

Este projeto está licenciado sob a GPL-2.0 License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Para questões ou sugestões, por favor abra uma issue no GitHub.